"""
"""
from __future__ import absolute_import

from os import getcwd, getuid, getgid
from os.path import exists, abspath, join, isabs, dirname
from shutil import copy

import click

from ..io import info, warn
from ..cli import pass_context
from ..config.wheels import WheelConfigManager
from ..forge.wheels import ForgeWheel
from ..cache import CacheManager
from ..execution.docker import DockerExecutionContext
from ..execution.qemu import QEMUExecutionContext
from ..util import xdg_data_dir, xdg_config_file


BDIST_WHEEL_CMD_TEMPLATE = 'starforge bdist_wheel --wheels-config {config} -i {image} -o {output} -u {uid} -g {gid} {name}'
GUEST_HOST = '/host'
GUEST_SHARE = '/share'


@click.command('wheel')
@click.option('--wheels-config',
              default=xdg_config_file(name='wheels.yml'),
              type=click.Path(file_okay=True,
                              writable=False,
                              resolve_path=True),
              help='Path to wheels config file (default: %s)' % xdg_config_file(name='wheels.yml'))
@click.option('--osk',
              default=xdg_config_file(name='osk.txt'),
              type=click.Path(dir_okay=True,
                              writable=False,
                              resolve_path=False),
              help='Path file containing OSK, if the guest requires it (default: %s)' % xdg_config_file(name='osk.txt'))
@click.option('--docker/--no-docker',
              default=True,
              help='Build under Docker')
@click.option('--qemu/--no-qemu',
              default=True,
              help='Build under QEMU')
@click.argument('wheel')
@pass_context
def cli(ctx, wheels_config, osk, docker, qemu, wheel):
    """ Build a wheel.
    """
    wheel_cfgmgr = WheelConfigManager.open(ctx.config, wheels_config)
    cachemgr = CacheManager(ctx.config.cache_path)
    wheel_config = wheel_cfgmgr.get_wheel_config(wheel)
    for image_name, image in wheel_config.images.items():
        if image.type == 'docker':
            if not docker:
                continue
            ectx = DockerExecutionContext(image, ctx.config.docker)
        elif image.type == 'qemu':
            if not qemu:
                continue
            ectx = QEMUExecutionContext(image, ctx.config.qemu, osk_file=osk)
        forge = ForgeWheel(wheel_config, cachemgr, ectx.run_context, image=image)
        forge.cache_sources()
        build = False
        for name in forge.get_expected_names():
            if exists(name):
                info("%s already built", name)
            else:
                build = True
        if build:
            # make wheels.yml accessible in guest
            copy(wheels_config, join(xdg_data_dir(), 'wheels.yml'))
            cmd = BDIST_WHEEL_CMD_TEMPLATE.format(config=join(GUEST_SHARE, 'galaxy-starforge', 'wheels.yml'),
                                                  image=image_name,
                                                  output=GUEST_HOST,
                                                  uid=getuid(),
                                                  gid=getgid(),
                                                  name=wheel)
            # if buildpy is not just `python` assume starforge is installed
            # along with buildpy and probably isn't on $PATH
            if isabs(image.buildpy):
                cmd = join(dirname(image.buildpy), cmd)
            share = [(abspath(getcwd()), GUEST_HOST, 'rw'),
                     (abspath(xdg_data_dir()), join(GUEST_SHARE, 'galaxy-starforge'), 'ro')]
            env = {'XDG_DATA_HOME': GUEST_SHARE}
            with ectx.run_context(share=share, env=env) as run:
                run(cmd)
            for name in forge.get_expected_names():
                if not exists(name):
                    warn("%s missing, build failed?", name)
        else:
            info('All wheels from image %s already built', image_name)
    # TODO: need to call sdist
