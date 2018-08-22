"""
"""
from __future__ import absolute_import

from os import getcwd, getuid, getgid
from os.path import exists, abspath, join, isabs, dirname
from shutil import copy

import click
import yaml
from six import iteritems, itervalues

from ..io import debug, info, warn, fatal
from ..cli import pass_context
from ..config.wheels import WheelConfigManager
from ..forge.wheels import ForgeWheel
from ..cache import CacheManager, cache_wheel_sources
from ..execution.docker import DockerExecutionContext
from ..execution.local import LocalExecutionContext
from ..execution.qemu import QEMUExecutionContext
from ..util import PythonSdist, xdg_cache_dir, xdg_config_file


LOCAL_BDIST_WHEEL_CMD_TEMPLATE = (
    'starforge {debug} --config-file {config} bdist_wheel --wheels-config {wheels_config} -i {image} {name}')
BDIST_WHEEL_CMD_TEMPLATE = (
    'starforge {debug} --config-file {config} bdist_wheel --wheels-config {wheels_config} -i {image} -o {output} -u '
    '{uid} -g {gid} {name}')
GUEST_HOST = '/host'
GUEST_SHARE = '/share'


# FIXME: dedup
UNIVERSAL = 'universal'
PUREPY = 'purepy'
C_EXTENSION = 'c-extension'
TYPE_IMAGESET_MAP = {
    UNIVERSAL: 'universal-wheel',
    PUREPY: 'purepy-wheel',
    C_EXTENSION: 'default-wheel',
}


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
@click.option('--sdist/--no-sdist',
              default=False,
              help='Build source distribution')
@click.option('--image',
              default=None,
              help="Image to build with (must be in the wheel's imageset)")
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
def cli(ctx, wheels_config, osk, sdist, image, docker, qemu, wheel, qemu_port, exit_on_failure):
    """ Build a wheel.
    """
    wheel_cfgmgr = WheelConfigManager.open(ctx.config, wheels_config)
    cache_manager = CacheManager(ctx.config.cache_path)
    try:
        wheel_config = wheel_cfgmgr.get_wheel_config(wheel)
    except KeyError:
        fatal('Package not found in %s: %s', wheels_config, wheel)
    wheel_type = wheel_config.configured_wheel_type
    debug("Configured wheel type: %s", wheel_type)
    # TODO: probably refactor this
    if wheel_type is None:
        sdist_tarball = cache_wheel_sources(cache_manager, wheel_config)[0]
        sdist = PythonSdist.open(sdist_tarball)
        wheel_type = sdist.wheel_type
        imageset = TYPE_IMAGESET_MAP[wheel_type]
        wheel_config.set_imageset(imageset=imageset)
        if wheel_type == UNIVERSAL:
            wheel_config.set_universal(True)
            # sets purepy
        elif wheel_type == PUREPY:
            wheel_config.set_purepy(True)
            wheel_config.set_universal(False)
        else:
            wheel_config.set_purepy(False)
            # sets universal
        debug("Detected wheel type '%s', using imageset '%s'", wheel_type, imageset)
    images = wheel_config.images
    if image:
        try:
            images = {image: wheel_config.get_image(image)}
        except:
            warn("Image '%s' is not in '%s' imageset, nothing to build", image, wheel_config.imageset.name)
            return
    for (image_name, image_conf) in iteritems(images):
        debug("Read image config: %s, image: %s, plat_name: %s, force_plat: %s",
              image_name, image_conf.image, image_conf.plat_name, image_conf.force_plat)
        if image_conf.type == 'docker':
            if not docker:
                continue
            ectx = DockerExecutionContext(image_conf, ctx.config.docker)
        elif image_conf.type == 'qemu':
            if not qemu:
                continue
            ectx = QEMUExecutionContext(image_conf, ctx.config.qemu, osk_file=osk, qemu_port=qemu_port)
        elif image_conf.type == 'local':
            ectx = LocalExecutionContext(image_conf)
        forge = ForgeWheel(wheel_config, cache_manager, ectx.run_context, image=image_conf)
        build_wheel = False
        for name in forge.get_expected_names():
            if exists(name):
                info("%s already built", name)
            else:
                build_wheel = True
        if build_wheel:
            if image_conf.type != 'local':
                cmd, share, env = _prep_build(ctx.debug, ctx.config, wheels_config, BDIST_WHEEL_CMD_TEMPLATE, image_conf, wheel)
            else:
                cmd = LOCAL_BDIST_WHEEL_CMD_TEMPLATE.format(
                    debug='--debug' if ctx.debug else '',
                    config=ctx.config_file,
                    wheels_config=wheels_config,
                    image=image_name,
                    name=wheel)
                share = None
                env = None
            with ectx.run_context(share=share, env=env) as run:
                run(cmd)
            missing = [n for n in forge.get_expected_names() if not exists(n)]
            for name in missing:
                warn("%s missing, build failed?", name)
            if exit_on_failure and missing:
                fatal("Exiting due to missing wheels")
        else:
            info('All wheels from image %s already built', image_name)


def _prep_build(debug, global_config, wheels_config, template, image, wheel_name):
    # make wheels.yml accessible in guest
    copy(wheels_config, join(xdg_cache_dir(), 'wheels.yml'))
    with open(join(xdg_cache_dir(), 'config.yml'), 'w') as f:
        yaml.dump(global_config.dump_config(), f)
    cmd = template.format(
        debug='--debug' if debug else '',
        config=join(GUEST_SHARE, 'galaxy-starforge', 'config.yml'),
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
             (abspath(xdg_cache_dir()), join(GUEST_SHARE,
                                            'galaxy-starforge'), 'ro')]
    env = {'XDG_CACHE_HOME': GUEST_SHARE}
    return (cmd, share, env)
