"""
"""
from __future__ import absolute_import

from os import getcwd, getuid, getgid
from os.path import exists, abspath, join, isabs, dirname
from shutil import copy

import click
import yaml
from six import iteritems, itervalues

from ..io import info, warn, fatal
from ..cli import pass_context
from ..config.wheels import WheelConfigManager
from ..forge.wheels import ForgeWheel
from ..cache import CacheManager
from ..execution.docker import DockerExecutionContext
from ..execution.qemu import QEMUExecutionContext
from ..util import xdg_data_dir, xdg_config_file


BDIST_WHEEL_CMD_TEMPLATE = (
    'starforge --config-file {config} bdist_wheel --wheels-config '
    '{wheels_config} -i {image} -o {output} -u {uid} -g {gid} {name}')
SDIST_CMD_TEMPLATE = (
    'starforge --config-file {config} sdist --wheels-config {wheels_config} '
    '-i {image} -o {output} -u {uid} -g {gid} {name}')
GUEST_HOST = '/host'
GUEST_SHARE = '/share'


@click.command('wheel')
@click.option('--wheels-config',
              default=xdg_config_file(name='wheels.yml'),
              type=click.Path(file_okay=True,
                              writable=False,
                              resolve_path=True),
              help='Path to wheels config file (default: '
                   '%s)' % xdg_config_file(name='wheels.yml'))
@click.option('--osk',
              default=xdg_config_file(name='osk.txt'),
              type=click.Path(dir_okay=True,
                              writable=False,
                              resolve_path=False),
              help='Path file containing OSK, if the guest requires it '
                   '(default: %s)' % xdg_config_file(name='osk.txt'))
@click.option('--docker/--no-docker',
              default=True,
              help='Build under Docker')
@click.option('--qemu/--no-qemu',
              default=True,
              help='Build under QEMU')
@click.option('--qemu-port',
              default=None,
              help='Connect to running QEMU instance on PORT')
@click.option('--exit-on-failure/--no-exit-on-failure',
              default=False,
              help='Immediately exit upon build failure (by default, '
                   'Starforge will try to build on all configured images '
                   'even if a previous image fails)')
@click.argument('wheel')
@pass_context
def cli(ctx, wheels_config, osk, docker, qemu, wheel, qemu_port,
        exit_on_failure):
    """ Build a wheel.
    """
    wheel_cfgmgr = WheelConfigManager.open(ctx.config, wheels_config)
    cachemgr = CacheManager(ctx.config.cache_path)
    try:
        wheel_config = wheel_cfgmgr.get_wheel_config(wheel)
    except KeyError:
        fatal('Package not found in %s: %s', wheels_config, wheel)
    for (image_name, image) in iteritems(wheel_config.images):
        if image.type == 'docker':
            if not docker:
                continue
            ectx = DockerExecutionContext(image, ctx.config.docker)
        elif image.type == 'qemu':
            if not qemu:
                continue
            ectx = QEMUExecutionContext(image, ctx.config.qemu,
                                        osk_file=osk, qemu_port=qemu_port)
        forge = ForgeWheel(wheel_config, cachemgr, ectx.run_context,
                           image=image)
        forge.cache_sources()
        build_wheel = False
        for name in forge.get_expected_names():
            if exists(name):
                info("%s already built", name)
            else:
                build_wheel = True
        if build_wheel:
            cmd, share, env = _prep_build(ctx.config, wheels_config,
                                          BDIST_WHEEL_CMD_TEMPLATE, image,
                                          wheel)
            with ectx.run_context(share=share, env=env) as run:
                run(cmd)
            missing = [n for n in forge.get_expected_names() if not exists(n)]
            for name in missing:
                warn("%s missing, build failed?", name)
            if exit_on_failure and missing:
                fatal("Exiting due to missing wheels")
        else:
            info('All wheels from image %s already built', image_name)

    image = filter(lambda x: x.type == 'docker',
                   itervalues(wheel_config.images))[0]
    ectx = DockerExecutionContext(image, ctx.config.docker)
    forge = ForgeWheel(wheel_config, cachemgr, ectx.run_context,
                       image=image)
    for name in forge.get_sdist_expected_names():
        if exists(name):
            info("sdist %s already built", name)
            break
    else:
        forge.cache_sources()
        cmd, share, env = _prep_build(ctx.config, wheels_config,
                                      SDIST_CMD_TEMPLATE, image, wheel)
        with ectx.run_context(share=share, env=env) as run:
            run(cmd)
        for name in forge.get_sdist_expected_names():
            if exists(name):
                break
        else:
            msg = "Possible sdists missing, build failed?"
            if exit_on_failure:
                fatal(msg)
            else:
                warn(msg)


def _prep_build(global_config, wheels_config, template, image, wheel_name):
    # make wheels.yml accessible in guest
    copy(wheels_config, join(xdg_data_dir(), 'wheels.yml'))
    with open(join(xdg_data_dir(), 'config.yml'), 'w') as f:
        yaml.dump(global_config.dump_config(), f)
    cmd = template.format(config=join(
        GUEST_SHARE, 'galaxy-starforge', 'config.yml'),
        wheels_config=join(GUEST_SHARE, 'galaxy-starforge', 'wheels.yml'),
        image=image.name,
        output=GUEST_HOST,
        uid=getuid(),
        gid=getgid(),
        name=wheel_name)
    # if buildpy is not just `python` assume starforge is installed
    # along with buildpy and probably isn't on $PATH
    if isabs(image.buildpy):
        cmd = join(dirname(image.buildpy), cmd)
    share = [(abspath(getcwd()), GUEST_HOST, 'rw'),
             (abspath(xdg_data_dir()), join(GUEST_SHARE,
                                            'galaxy-starforge'), 'ro')]
    env = {'XDG_DATA_HOME': GUEST_SHARE}
    return (cmd, share, env)
