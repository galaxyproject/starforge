"""
"""
from __future__ import absolute_import

import logging

from pip.index import PackageFinder
from pip.download import PipSession
from pip.req import InstallRequirement
from pip.index import PyPI
from pip.exceptions import BestVersionAlreadyInstalled
from pip._vendor.packaging.version import parse as parse_version
from pkg_resources import Distribution, DistributionNotFound
import click

from ..io import debug, info, fatal
from ..cli import pass_context
from ..util import xdg_config_file
from ..config.wheels import WheelConfigManager


@click.command('wheel_updates')
@click.option('--wheels-config',
              default=xdg_config_file(name='wheels.yml'),
              type=click.Path(file_okay=True,
                              writable=False,
                              resolve_path=True),
              help='Path to wheels config file')
@click.argument('wheel', nargs=-1,)
@pass_context
def cli(ctx, wheels_config, wheel):
    """ Determine what wheels have updates available.
    """
    wheels = wheel
    wheel_cfgmgr = WheelConfigManager.open(ctx.config, wheels_config)

    # Set log level for pip logging
    if ctx.debug:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.WARNING)

    session = PipSession(
        cache=None,
        retries=None,
        insecure_hosts=[]
    )
    finder = PackageFinder(
        find_links=[],
        index_urls=[PyPI.simple_url],
        session=session
    )

    if not wheels:
        wheel_configs = wheel_cfgmgr
    else:
        wheel_configs = []
        for wheel in wheels:
            try:
                wheel_config = wheel_cfgmgr.get_wheel_config(wheel)
            except KeyError:
                fatal('Package not found in %s: %s', wheels_config, wheel)
            if wheel_config.pinned:
                fatal("%s version is pinned to %s",
                      wheel, wheel_config.version)
            wheel_configs.append((wheel, wheel_config))

    for wheel, wheel_config in wheel_configs:
        if wheel_config.pinned:
            continue
        inst_req = InstallRequirement.from_line(
            wheel, None, isolated=False, wheel_cache=None)
        inst_req.satisfied_by = Distribution(
            wheels_config, None, wheel, wheel_config.version, None, None, None)
        try:
            # newest is actually a distlib Version object
            newest = finder.find_newest_version(inst_req, True)
            info('%s %s', wheel, newest)
        except BestVersionAlreadyInstalled:
            debug("%s %s in wheels config is the newest version",
                  wheel, wheel_config.version)


# This is mostly the find_requirement method from pip.index.PackageFinder in
# pip 8, but that method only returns the location. We need the version, not
# the link.  Modifications are present to support pip < 8. This works on at
# least pip 7.1.2, I have not tested other versions.
def find_requirement(self, req, upgrade):
    """Try to find a Link matching req

    Expects req, an InstallRequirement and upgrade, a boolean
    Returns a Link if found,
    Raises DistributionNotFound or BestVersionAlreadyInstalled otherwise
    """
    logger = logging.getLogger(__name__)

    try:
        all_candidates = self.find_all_candidates(req.name)
    except AttributeError:
        all_candidates = self._find_all_versions(req.name)

    # Filter out anything which doesn't match our specifier
    _versions = set(
        req.specifier.filter(
            # We turn the version object into a str here because otherwise
            # when we're debundled but setuptools isn't, Python will see
            # packaging.version.Version and
            # pkg_resources._vendor.packaging.version.Version as different
            # types. This way we'll use a str as a common data interchange
            # format. If we stop using the pkg_resources provided specifier
            # and start using our own, we can drop the cast to str().
            [str(c.version) for c in all_candidates],
            prereleases=(
                self.allow_all_prereleases
                if self.allow_all_prereleases else None
            ),
        )
    )
    applicable_candidates = [
        # Again, converting to str to deal with debundling.
        c for c in all_candidates if str(c.version) in _versions
    ]

    applicable_candidates = self._sort_versions(applicable_candidates)

    if req.satisfied_by is not None:
        installed_version = parse_version(req.satisfied_by.version)
    else:
        installed_version = None

    if installed_version is None and not applicable_candidates:
        logger.critical(
            'Could not find a version that satisfies the requirement %s '
            '(from versions: %s)',
            req,
            ', '.join(
                sorted(
                    set(str(c.version) for c in all_candidates),
                    key=parse_version,
                )
            )
        )

        raise DistributionNotFound(
            'No matching distribution found for %s' % req
        )

    best_installed = False
    if installed_version and (
            not applicable_candidates or
            applicable_candidates[0].version <= installed_version):
        best_installed = True

    if not upgrade and installed_version is not None:
        if best_installed:
            logger.debug(
                'Existing installed version (%s) is most up-to-date and '
                'satisfies requirement',
                installed_version,
            )
        else:
            logger.debug(
                'Existing installed version (%s) satisfies requirement '
                '(most up-to-date version is %s)',
                installed_version,
                applicable_candidates[0].version,
            )
        return None

    if best_installed:
        # We have an existing version, and its the best version
        logger.debug(
            'Installed version (%s) is most up-to-date (past versions: '
            '%s)',
            installed_version,
            ', '.join(str(c.version) for c in applicable_candidates) or
            "none",
        )
        raise BestVersionAlreadyInstalled

    selected_candidate = applicable_candidates[0]
    logger.debug(
        'Using version %s (newest of versions: %s)',
        selected_candidate.version,
        ', '.join(str(c.version) for c in applicable_candidates)
    )
    return selected_candidate.version


PackageFinder.find_newest_version = find_requirement
