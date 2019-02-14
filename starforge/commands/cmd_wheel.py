"""
"""
from __future__ import absolute_import

import sys
from os import getcwd, getuid, getgid
from os.path import exists, abspath, join, isabs, dirname
from shutil import copy

import click
import yaml

from ..io import error, info, warn, fatal
from ..cli import pass_context
from ..forge.wheels import build_forges
from ..cache import cache_wheel_sources, check_wheel_source
from ..util import xdg_cache_dir, xdg_config_file


LOCAL_BDIST_WHEEL_CMD_TEMPLATE = (
    'starforge {debug} --config-file {config} bdist_wheel --wheels-config {wheels_config} -i {image} {name}')
BDIST_WHEEL_CMD_TEMPLATE = (
    'starforge {debug} --config-file {config} bdist_wheel --wheels-config {wheels_config} -i {image} -o {output} -u '
    '{uid} -g {gid} {name}')
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
@click.option('--sdist/--no-sdist',
              default=False,
              help='Build source distribution')
@click.option('--image',
              multiple=True,
              help="Image(s) to build with (must be in the wheel's imageset)")
@click.option('--docker/--no-docker',
              default=True,
              help='REMOVED: Use --image. (Build under Docker)')
@click.option('--qemu/--no-qemu',
              default=True,
              help='REMOVED: Use --image. (Build under QEMU)')
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
    try:
        ran_build = False
        failed = False
        for forge in build_forges(ctx.config, wheels_config, wheel, images=image, osk_file=osk, qemu_port=qemu_port):
            ran_build = True
            # _set_imageset may or may not have already done this
            # TODO: don't run repeatedly
            try:
                check_wheel_source(forge.cache_manager, forge.wheel_config)
            except AssertionError:
                cache_wheel_sources(forge.cache_manager, forge.wheel_config)
            build_wheel = False
            for name in forge.get_expected_names():
                if exists(name):
                    info("%s already built", name)
                else:
                    build_wheel = True
            if build_wheel:
                if forge.image.type != 'local':
                    cmd, share, env = _prep_build(ctx.debug, ctx.config, wheels_config, BDIST_WHEEL_CMD_TEMPLATE,
                                                  forge.image, wheel)
                else:
                    cmd = LOCAL_BDIST_WHEEL_CMD_TEMPLATE.format(
                        debug='--debug' if ctx.debug else '',
                        config=ctx.config_file,
                        wheels_config=wheels_config,
                        image=forge.image.name,
                        name=wheel)
                    share = None
                    env = None
                with forge.exec_context(share=share, env=env) as run:
                    try:
                        run(cmd)
                    except Exception:
                        failed = True
                        error("Caught exception while building on image: %s", forge.image.name, exception=True)
                missing = [n for n in forge.get_expected_names() if not exists(n)]
                for name in missing:
                    failed = True
                    warn("%s missing, build failed?", name)
                if exit_on_failure and failed:
                    fatal("Exiting due to previous error(s)")
            else:
                info('All wheels from image %s already built', forge.image.name)
        if not ran_build:
            info("Nothing to build: none of the specified images are in the wheel's imageset")
            sys.exit(2)
        if failed:
            fatal("Build failed, see error(s) above")
        else:
            info("Build OK")
    except KeyError:
        fatal('Package not found in %s: %s', wheels_config, wheel, exception=True)
    except Exception:
        fatal('Build failed', exception=True)


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
             (abspath(xdg_cache_dir()), join(GUEST_SHARE, 'galaxy-starforge'), 'ro')]
    env = {'XDG_CACHE_HOME': GUEST_SHARE}
    return (cmd, share, env)
