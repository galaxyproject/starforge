"""
Utility things
"""
from __future__ import absolute_import

import os
import tarfile
import zipfile
from os.path import join, abspath, expanduser
from subprocess import Popen, CalledProcessError, PIPE
try:
    from configparser import ConfigParser, NoSectionError, NoOptionError
except ImportError:
    from ConfigParser import ConfigParser, NoSectionError, NoOptionError

from six import iteritems, string_types


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
        self.__roots = set()
        if tarfile.is_tarfile(arcfile):
            self.arctype = 'tar'
            self.arc = tarfile.open(arcfile)
        elif zipfile.is_zipfile(arcfile):
            self.arctype = 'zip'
            self.arc = zipfile.ZipFile(arcfile)
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

    def getnames(self):
        if self.arctype == 'tar':
            return self.arc.getnames()
        elif self.arctype == 'zip':
            return self.arc.namelist()

    def extractfile(self, member):
        if self.arctype == 'tar':
            return self.arc.extractfile(member)
        elif self.arctype == 'zip':
            return self.arc.open(member)

    def extractall(self, path):
        # FIXME: replace with a safe extraction
        return self.arc.extractall(path)

    @property
    def universal(self):
        """ Return true if this archive contains an sdist for a universal wheel
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
