"""
"""
from __future__ import absolute_import

import click

from os import getcwd

from ..cli import pass_context
from ..config.wheels import WheelConfigManager
from ..forge.wheels import ForgeWheel
from ..cache import CacheManager
from ..execution.local import LocalExecutionContext
from ..util import xdg_config_file


@click.command('wheel')
@click.option('--wheels-config',
              default=xdg_config_file(name='wheels.yml'),
              type=click.Path(file_okay=True,
                              writable=False,
                              resolve_path=True),
              help='Path to wheels config file')
@click.option('-i', '--image',
              default=None,
              help='Name of image (in wheels config) under which wheel is '
                   'building')
@click.option('-o', '--output',
              default=getcwd(),
              type=click.Path(file_okay=False),
              help='Copy output wheels to OUTPUT')
@click.option('-u', '--uid',
              default=-1,
              type=click.STRING,
              help='Change ownership of output(s) to UID')
@click.option('-g', '--gid',
              default=-1,
              type=click.STRING,
              help='Change group of output(s) to UID')
@click.option('--fetch-srcs/--no-fetch-srcs',
              default=False,
              help='Enable or disable fetching/caching of sources (normally '
                   'this is done by `starforge wheel`')
@click.argument('wheel')
@pass_context
def cli(ctx, wheels_config, image, output, uid, gid, fetch_srcs, wheel):
    """ Build a wheel without virtualization.

    This command is not typically meant to be run directly, you should use
    `starforge wheel` instead. This is the command that `starforge wheel` calls
    inside the virtualized environment to actually produce wheels.

    WARNING: This command uses tarfile's extract_all() method, which is
    insecure. Because this method is intended to be run under ephemeral
    virtualization, this is not normally a concern, but if you are running it
    by hand, you should be aware of the security risk.
    """
    wheel_cfgmgr = WheelConfigManager.open(ctx.config, wheels_config)
    cachemgr = CacheManager(ctx.config.cache_path)
    wheel_config = wheel_cfgmgr.get_wheel_config(wheel)
    # `image` is an image_name until here
    image = wheel_config.get_image(image)
    ectx = LocalExecutionContext(image)
    forge = ForgeWheel(wheel_config, cachemgr, ectx.run_context, image=image)
    if fetch_srcs:
        forge.cache_sources()
    forge.bdist_wheel(output=output, uid=uid, gid=gid)
