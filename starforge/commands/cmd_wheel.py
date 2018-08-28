"""
"""
from __future__ import absolute_import

import sys
from os import getcwd, getuid, getgid
from os.path import exists, abspath, join, isabs, dirname
from shutil import copy

import click
import yaml
from six import iteritems, itervalues

from ..io import debug, error, info, warn, fatal
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
              multiple=True,
              help="Image(s) to build with (must be in the wheel's imageset)")
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
    _set_imageset(cache_manager, wheel_config)
    images = wheel_config.images
    if image:
        images = {}
        for i in image:
            try:
                images[i] = wheel_config.get_image(i)
            except:
                warn("Image '%s' is not in '%s' imageset", i, wheel_config.imageset.name)
        if not images:
            info("Nothing to build: none of the specified images are in the wheel's imageset")
            sys.exit(2)
    # _set_imageset may or may not have already done this
    cache_wheel_sources(cache_manager, wheel_config)
    failed = False
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
                try:
                    run(cmd)
                except Exception:
                    failed = True
                    error("Caught exception while building on image: %s", image_name, exception=True)
            missing = [n for n in forge.get_expected_names() if not exists(n)]
            for name in missing:
                failed = True
                warn("%s missing, build failed?", name)
            if exit_on_failure and failed:
                fatal("Exiting due to previous error(s)")
        else:
            info('All wheels from image %s already built', image_name)
    if failed:
        fatal("Build failed, see error(s) above")
    else:
        info("Build OK")


def _set_imageset(cache_manager, wheel_config):
    debug("Configured wheel imageset: %s", wheel_config.configured_imageset)
    wheel_type = wheel_config.configured_wheel_type
    debug("Configured wheel type: %s", wheel_type)
    # TODO: probably refactor this
    if wheel_type is None:
        sdist_tarball = cache_wheel_sources(cache_manager, wheel_config)[0]
        sdist = PythonSdist.open(sdist_tarball)
        wheel_type = sdist.wheel_type
        debug("Detected wheel type: %s", wheel_type)
    if wheel_type is None:
        fatal("ERROR: Unable to determine wheel type of '%s', set `purepy`, `universal`, and/or `imageset` in wheel "
              "config", wheel_config.name)
    imageset = TYPE_IMAGESET_MAP[wheel_type]
    debug("Using imageset: %s", wheel_config.configured_imageset or imageset)
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
