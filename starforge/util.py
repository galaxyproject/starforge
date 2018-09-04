"""
Utility things
"""
from __future__ import absolute_import

import os
import shlex
import tarfile
import zipfile
from os import pardir
from os.path import (
    abspath,
    dirname,
    expanduser,
    isabs,
    join,
    normpath
)
from subprocess import (
    CalledProcessError,
    PIPE,
    Popen,
    check_call
)
try:
    import lzma
except ImportError:
    try:
        import backports.lzma as lzma
    except ImportError:
        lzma = None
try:
    from tempfile import TemporaryDirectory
except ImportError:
    from backports.tempfile import TemporaryDirectory

try:
    from configparser import ConfigParser, NoSectionError, NoOptionError
except ImportError:
    from ConfigParser import ConfigParser, NoSectionError, NoOptionError

from six import iteritems, string_types

from .io import debug
from .packaging.setup import wheel_type

UNSUPPORTED_ARCHIVE_MESSAGE = "Missing support for '{arctype}' archives, use `pip install starforge[{extra}]` to install"


def dict_merge(old, new):
    """Recursive dictionary merge, values in `new` will replace values of
    conflicting keys in `old`.
    """
    for (k, v) in iteritems(new):
        if type(v) == dict:
            if k in old:
                dict_merge(old[k], new[k])
            else:
                old[k] = v
        else:
            old[k] = v


def xdg_config_file(name='config.yml'):
    config_home = expanduser(os.environ.get('XDG_CONFIG_HOME', '~/.config'))
    return abspath(join(config_home, 'galaxy-starforge', name))


def xdg_data_dir():
    data_home = expanduser(os.environ.get('XDG_DATA_HOME', '~/.local/share/'))
    return abspath(join(data_home, 'galaxy-starforge'))


def xdg_cache_dir():
    cache_home = expanduser(os.environ.get('XDG_CACHE_HOME', '~/.cache/'))
    return abspath(join(cache_home, 'galaxy-starforge'))


def check_output(*popenargs, **kwargs):
    """ From Python 2.7
    """
    if 'stdout' in kwargs:
        raise ValueError('stdout argument not allowed, it will be overridden.')
    process = Popen(stdout=PIPE, *popenargs, **kwargs)
    output, unused_err = process.communicate()
    retcode = process.poll()
    if retcode:
        cmd = kwargs.get("args")
        if cmd is None:
            cmd = popenargs[0]
        raise CalledProcessError(retcode, cmd, output=output)
    return output


def py_to_pip(py):
    if dirname(py):
        return join(dirname(py), 'pip')
    else:
        return 'pip'


def pip_install(pip='pip', args=None, packages=None, executor=check_call, add_galaxy_index=True, **kwargs):
    args = args or []
    packages = packages or []
    cmd = [pip, 'install']
    if add_galaxy_index and '--index-url' not in args:
        cmd.extend(shlex.split(
            '--index-url https://wheels.galaxyproject.org/simple/ --extra-index-url https://pypi.python.org/simple/'
        ))
    if not isinstance(args, list):
        args = shlex.split(args)
    cmd.extend(args)
    if not isinstance(packages, list):
        packages = shlex.split(packages)
    cmd.extend(packages)
    return executor(cmd, **kwargs)


# asbool implementation pulled from PasteDeploy
truthy = frozenset(['true', 'yes', 'on', 'y', 't', '1'])
falsy = frozenset(['false', 'no', 'off', 'n', 'f', '0'])


def asbool(obj):
    if isinstance(obj, string_types):
        obj = obj.strip().lower()
        if obj in truthy:
            return True
        elif obj in falsy:
            return False
        else:
            raise ValueError("String is not true/false: %r" % obj)
    return bool(obj)


class Archive(object):
    def __init__(self, arcfile):
        self._arcfile = arcfile
        self.__roots = set()
        if tarfile.is_tarfile(arcfile):
            self.arctype = 'tar'
            self.arc = tarfile.open(arcfile)
        elif zipfile.is_zipfile(arcfile):
            self.arctype = 'zip'
            self.arc = zipfile.ZipFile(arcfile)
        elif arcfile.endswith('.tar.xz'):
            self.arctype = 'tar'
            self.arc = tarfile.open(fileobj=lzma.open(arcfile))
        else:
            raise Exception('Unknown archive type: %s' % arcfile)

    @classmethod
    def open(cls, arcfile):
        return cls(arcfile)

    @property
    def roots(self):
        if not self.__roots:
            for name in self.getnames():
                self.__roots.add(name.split(os.sep, 1)[0])
        return self.__roots

    @property
    def root(self):
        """ For archives that are expected to only contain a single root.
        """
        assert len(self.roots) == 1, "Could not determine root directory in archive: %s" % self._arcfile
        return next(iter(self.roots))

    @property
    def getnames(self):
        if self.arctype == 'tar':
            return self.arc.getnames
        elif self.arctype == 'zip':
            return self.arc.namelist

    @property
    def extractfile(self):
        if self.arctype == 'tar':
            return self.arc.extractfile
        elif self.arctype == 'zip':
            return self.arc.open

    @property
    def extract(self):
        return self.arc.extract

    def extractall(self, path):
        for name in self.getnames():
            debug(name)
            assert safe_relpath(name), "%s: path is outside its root: %s" % (self._arcfile, name)
            self.extract(name, path)

    @property
    def universal(self):
        """ DEPRECATED: Return true if this archive contains an sdist for a universal wheel

        This method should be replaced with `wheel.bdist_wheel`.
        """
        assert len(self.roots) == 1, 'Cannot check archives with != 1 root'
        root = next(iter(self.roots))
        setup_cfg = join(root, 'setup.cfg')
        try:
            fh = self.extractfile(setup_cfg)
            cp = ConfigParser()
            cp.readfp(fh)
            try:
                universal = cp.get('bdist_wheel', 'universal')
            except NoSectionError:
                # this isn't documented but works, and PasteDeploy uses it
                universal = cp.get('wheel', 'universal')
            return asbool(universal)
        except (KeyError, NoSectionError, NoOptionError):
            return False


class PythonSdist(Archive):
    @property
    def wheel_type(self):
        with TemporaryDirectory(prefix='starforge_sdist_wheel_type_') as td:
            debug("Extracting '%s' to '%s'", self._arcfile, td)
            self.extractall(td)
            root = join(td, self.root)
            return wheel_type(root)


class UnsupportedArchiveModule(object):
    def __init__(self, arctype, extra):
        self.arctype = arctype
        self.extra = extra

    def open(self, *args, **kwargs):
        raise UnsupportedArchiveType(
            UNSUPPORTED_ARCHIVE_MESSAGE.format(
                arctype=self.arctype,
                extra=self.extra,
            )
        )


class UnsupportedArchiveType(Exception):
    pass


def safe_relpath(path):
    return not (isabs(path) or normpath(path).startswith(pardir))


if lzma is None:
    lzma = UnsupportedArchiveModule('xz', 'lzma')
