"""
"""
from __future__ import absolute_import

import zipfile
from os import getcwd
from os.path import abspath, dirname, exists, join

import click
from six import iteritems

from ..cli import pass_context
from ..config.wheels import WheelConfigManager
from ..forge.wheels import ForgeWheel
from ..execution.docker import DockerExecutionContext
from ..execution.local import LocalExecutionContext
from ..execution.qemu import QEMUExecutionContext
from ..io import debug, fatal, info
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
              default=None,
              help='Name of image (in wheels config) under which wheel is building')
@click.option('--qemu-port',
              default=None,
              help='Connect to running QEMU instance on PORT')
@click.argument('wheel')
@pass_context
def cli(ctx, wheels_config, osk, image, qemu_port, wheel):
    """ Test a wheel.
    """
    wheel_cfgmgr = WheelConfigManager.open(ctx.config, wheels_config)
    try:
        wheel_config = wheel_cfgmgr.get_wheel_config(wheel)
    except KeyError:
        fatal('Package not found in %s: %s', wheels_config, wheel)
    for (image_name, image_conf) in iteritems(wheel_config.images):
        if image and image_name != image:
            continue
        debug("Read image config: %s, image: %s, plat_name: %s, force_plat: %s",
              image_name, image_conf.image, image_conf.plat_name, image_conf.force_plat)
        if image_conf.type == 'local':
            ectx = LocalExecutionContext(image_conf)
        if image_conf.type == 'docker':
            ectx = DockerExecutionContext(image_conf, ctx.config.docker)
        elif image_conf.type == 'qemu':
            ectx = QEMUExecutionContext(image_conf, ctx.config.qemu, osk_file=osk, qemu_port=qemu_port)
        forge = ForgeWheel(wheel_config, None, ectx.run_context, image=image_conf)
        names = forge.get_expected_names()
        for py, name in zip(image_conf.pythons, names):
            if not exists(name):
                fatal("%s: No such file or directory", name)
            pip = join(dirname(py), 'pip')
            top_level = '{}-{}.dist-info/top_level.txt'.format(*(name.split('-')[:2]))
            pkgs = zipfile.ZipFile(name).open(top_level).read().splitlines()
            cwd = abspath(getcwd())
            share = [(cwd, cwd, 'ro')]
            with ectx.run_context(share=share) as run:
                run([pip, 'install', join(cwd, name)])
                for pkg in pkgs:
                    pkg = pkg.decode('utf-8')
                    info('Importing %s with %s', pkg, py)
                    run([py, '-c', 'import {pkg}; print({pkg})'.format(pkg=pkg)])
