"""
"""
from __future__ import absolute_import

import zipfile
from os import getcwd
from os.path import abspath, dirname, exists, join

import click

from ..cli import pass_context
from ..forge.wheels import build_forges
from ..io import debug, error, fatal, info
from ..util import xdg_config_file


@click.command('test_wheel')
@click.option('--wheels-config',
              default=xdg_config_file(name='wheels.yml'),
              type=click.Path(file_okay=True, writable=False, resolve_path=True),
              help='Path to wheels config file')
@click.option('--osk',
              default=xdg_config_file(name='osk.txt'),
              type=click.Path(dir_okay=True, writable=False, resolve_path=False),
              help='File containing OSK, if the guest requires it (default: %s)' % xdg_config_file(name='osk.txt'))
@click.option('-i', '--image',
              multiple=True,
              help='Name of image(s) (in wheels config) under which wheel is building')
@click.option('--qemu-port',
              default=None,
              help='Connect to running QEMU instance on PORT')
@click.argument('wheel')
@pass_context
def cli(ctx, wheels_config, osk, image, qemu_port, wheel):
    """ Test a wheel.
    """
    if not image:
        fatal("At least one image must be specified")
    try:
        ran_tests = False
        for forge in build_forges(ctx.config, wheels_config, wheel, images=image, osk_file=osk, qemu_port=qemu_port):
            info("Testing wheel on image '%s': %s", forge.image.name, wheel)
            names = forge.get_expected_names()
            debug("Expecting wheel files:\n  %s", '\n  '.join(names))
            for py, name in zip(forge.image.pythons, names):
                _test_wheel(forge, py, name, forge.wheel_config.skip_tests)
                ran_tests = True
        assert ran_tests, 'No tests ran'
    except KeyError:
        fatal('Package not found in %s: %s', wheels_config, wheel)
    except Exception:
        fatal('Tests failed', exception=True)


def _test_wheel(forge, py, name, skip):
    if not exists(name):
        fatal("%s: No such file or directory", name)
    info('Testing wheel: %s', name)
    pip = join(dirname(py), 'pip')
    top_level = '{}-{}.dist-info/top_level.txt'.format(*(name.split('-')[:2]))
    pkgs = zipfile.ZipFile(name).open(top_level).read().splitlines()
    cwd = abspath(getcwd())
    share = [(cwd, cwd, 'ro')]
    with forge.exec_context(share=share) as run:
        run([pip, 'install', join(cwd, name)])
        for pkg in pkgs:
            pkg = pkg.decode('utf-8')
            info('%s: import %s: ', py, pkg, nl=False)
            if pkg not in skip:
                try:
                    run([py, '-c', 'import {pkg}; print({pkg})'.format(pkg=pkg)])
                    info('OK')
                except Exception:
                    error('FAIL')
                    raise
            else:
                info('skipped')
