""" setuptools/distutils hackery
"""
import json
import sys
from os import (
    getcwd,
    rename
)
from os.path import (
    exists,
    join
)
from subprocess import check_output, CalledProcessError

from ..io import (
    debug,
    error,
    warn
)


IMPORT_INTERFACE_WHEEL = 'import starforge.interface.wheel'
IMPORT_SETUPTOOLS = 'import setuptools'
WRAPPED_FILENAME = '__setup_wrapped_by_starforge.py'
SETUP_PY_WRAPPER = '''#!/usr/bin/env python
{import_interface_wheel}
{import_setuptools}
with open('{wrapped}') as f:
    code = compile(f.read(), '{wrapped}', 'exec')
exec(code)
'''

# FIXME: dedup
UNIVERSAL = 'universal'
PUREPY = 'purepy'
C_EXTENSION = 'c-extension'


def wrap_setup(package_dir=None, import_interface_wheel=False, import_setuptools=True):
    setup = 'setup.py'
    wrapped = WRAPPED_FILENAME
    if package_dir:
        setup = join(package_dir, setup)
        wrapped = join(package_dir, wrapped)
    if exists(wrapped):
        warn("Wrapped setup.py already exists, not overwriting: %s", wrapped)
        return
    rename(setup, wrapped)
    with open(setup, 'w') as fh:
        fh.write(SETUP_PY_WRAPPER.format(
            import_interface_wheel=IMPORT_INTERFACE_WHEEL if import_interface_wheel else '',
            import_setuptools=IMPORT_SETUPTOOLS if import_setuptools else '',
            wrapped=WRAPPED_FILENAME,
        ))


def check_setup(package_dir=None):
    package_dir = package_dir or getcwd()
    cmd = [sys.executable, 'setup.py', '--help-commands']
    out = _check_output(cmd, cwd=package_dir)
    for line in out.splitlines():
        try:
            if line.strip().split()[0] == 'bdist_wheel':
                return True
        except IndexError:
            pass
    return False


def wheel_type(package_dir=None):
    package_dir = package_dir or getcwd()
    if not check_setup(package_dir=package_dir):
        wrap_setup(package_dir=package_dir)
    t = None
    try:
        cmd = [sys.executable, 'setup.py', '-q', 'wheel_info', '--json']
        wheel_info = _check_output(cmd, cwd=package_dir)
        wheel_info = json.loads(wheel_info)
        if wheel_info['purepy']:
            if wheel_info['universal']:
                t = UNIVERSAL
            else:
                t = PUREPY
        else:
            t = C_EXTENSION
    except (CalledProcessError, ValueError) as exc:
        error("Failed to get wheel info: %s", exc)
    return t


def _check_output(cmd, cwd=None):
    debug('Executing in %s: %s', cwd, ' '.join(cmd))
    out = check_output(cmd, cwd=cwd)
    if sys.version_info >= (3,):
        out = out.decode('UTF-8')
    return out
