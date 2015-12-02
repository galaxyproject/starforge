"""
"""
from __future__ import absolute_import

import click

from ..io import info
from ..cli import pass_context
from ..config.wheels import WheelConfigManager
from ..util import xdg_config_file


@click.command('wheel')
@click.option('--wheels-config',
              default=xdg_config_file(name='wheels.yml'),
              type=click.Path(file_okay=True,
                              writable=False,
                              resolve_path=True),
              help='Path to wheels config file')
@click.argument('old-wheels-config')
@pass_context
def cli(ctx, wheels_config, old_wheels_config):
    """ Determine what wheels have changed between two wheel config files.
    """
    added = []
    removed = []
    modified = []
    wheel_cfgmgr = WheelConfigManager.open(ctx.config, wheels_config)
    old_wheel_cfgmgr = WheelConfigManager.open(ctx.config, old_wheels_config)
    for current_name, current_wheel in wheel_cfgmgr:
        if current_name not in old_wheel_cfgmgr:
            added.append(current_name)
        else:
            old_wheel = old_wheel_cfgmgr[current_name]
            if current_wheel.config != old_wheel.config:
                modified.append(current_name)
    for old_name, old_wheel in old_wheel_cfgmgr:
        if old_name not in wheel_cfgmgr:
            removed.append(old_name)
    for name in added:
        info('A %s', name)
    for name in removed:
        info('R %s', name, fg='red')
    for name in modified:
        info('M %s', name, fg='blue')
