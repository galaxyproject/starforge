"""
"""
from __future__ import absolute_import

from os import getcwd, getuid, getgid
from os.path import exists, abspath, join
from shutil import copy

import click

from ..io import info
from ..cli import pass_context
from ..config.wheels import WheelConfigManager
from ..forge.wheels import ForgeWheel
from ..cache import CacheManager
from ..execution.docker import DockerExecutionContext
from ..util import xdg_data_dir


BDIST_WHEEL_CMD_TEMPLATE = 'starforge bdist_wheel --wheels-config {config} -i {image} -o {output} -u {uid} -g {gid} {name}'
GUEST_HOST = '/host'
GUEST_SHARE = '/share'


@click.command('wheel')
@click.option('--wheels-config',
              default='wheels.yml',
              type=click.Path(file_okay=True,
                              writable=False,
                              resolve_path=True),
              help='Path to wheels config file')
@click.argument('wheel')
@pass_context
def cli(ctx, wheels_config, wheel):
    """ Build a wheel.
    """
    wheel_cfgmgr = WheelConfigManager.open(wheels_config)
    cachemgr = CacheManager(ctx.config.cache_path)
    wheel_config = wheel_cfgmgr.get_wheel_config(wheel)
    for image_name, image in wheel_config.images.items():
        if image.type == 'docker':
            ectx = DockerExecutionContext(image_name, ctx.config.docker)
        elif image.type == 'qemu':
            debug('QEMU exec context not implemented yet...')
            #ectx = QEMUExecutionContext(image_name, ctx.config.qemu)
        forge = ForgeWheel(wheel_config, cachemgr, ectx.run_context, image=image_name)
        forge.cache_sources()
        build = False
        for name in forge.get_expected_names():
            if exists(name):
                info("%s already built", name)
            else:
                build = True
        if build:
            copy(wheels_config, join(xdg_data_dir(), 'wheels.yml'))
            cmd = BDIST_WHEEL_CMD_TEMPLATE.format(config=join(GUEST_SHARE, 'galaxy-starforge', 'wheels.yml'),
                                                  image=image_name,
                                                  output=GUEST_HOST,
                                                  uid=getuid(),
                                                  gid=getgid(),
                                                  name=wheel)
            share = [(abspath(getcwd()), GUEST_HOST, 'rw'),
                     (abspath(xdg_data_dir()), join(GUEST_SHARE, 'galaxy-starforge'), 'ro')]
            env = {'XDG_DATA_HOME': GUEST_SHARE}
            with ectx.run_context(share=share, env=env) as run:
                run(cmd)
        else:
            info('All wheels from image %s already built', image_name)
    # TODO: need to call sdist
