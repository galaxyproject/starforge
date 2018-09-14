"""
"""
from __future__ import absolute_import

from os.path import join

try:
    from tempfile import TemporaryDirectory
except ImportError:
    from backports.tempfile import TemporaryDirectory

import click

from ..cache import CacheManager, cache_wheel_sources
from ..cli import pass_context
from ..config.wheels import WheelConfigManager
from ..io import debug, fatal, info
from ..util import PythonSdist, xdg_config_file


# FIXME: dedup
UNIVERSAL = 'universal'
PUREPY = 'purepy'
C_EXTENSION = 'c-extension'


@click.command('wheel_type')
@click.option(
    '--wheels-config',
    default=xdg_config_file(name='wheels.yml'),
    type=click.Path(file_okay=True, writable=False, resolve_path=True),
    help='Path to wheels config file (default: %s)' % xdg_config_file(name='wheels.yml'))
@click.argument('wheel')
@pass_context
def cli(ctx, wheels_config, wheel):
    """ Determine wheel type.
    """
    wheel_config_manager = WheelConfigManager.open(ctx.config, wheels_config)
    cache_manager = CacheManager(ctx.config.cache_path)
    try:
        wheel_config = wheel_config_manager.get_wheel_config(wheel)
    except KeyError:
        fatal('Package not found in %s: %s', wheels_config, wheel)
    # if explicitly set in the wheel config we can avoid caching/checking the sdist
    wheel_type = wheel_config.configured_wheel_type
    if wheel_type is None:
        sdist_tarball = cache_wheel_sources(cache_manager, wheel_config)[0]
        sdist = PythonSdist.open(sdist_tarball)
        wheel_type = sdist.wheel_type or 'unknown'
    info(wheel_type, bold=None, fg=None, err=False)
