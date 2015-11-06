"""
"""
from __future__ import absolute_import

from os.path import exists

import click

from ..io import info
from ..cli import pass_context
from ..config.wheels import WheelConfigManager
from ..forge.wheels import ForgeWheel
from ..cache import CacheManager
from ..execution.docker import DockerExecutionContext


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
                cmd = forge.get_bdist_wheel_cmd()
                with ectx.run_context() as run:
                    run(cmd)
        else:
            info('All wheels from image %s already built', image_name)
    # TODO: need to call sdist
