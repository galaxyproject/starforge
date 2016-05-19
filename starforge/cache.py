"""
"""
from __future__ import absolute_import

import subprocess

from os import makedirs, listdir
from os.path import exists, join, basename
from abc import ABCMeta, abstractmethod
try:
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse

import requests
import yaml
from pkg_resources import parse_version
from six import with_metaclass

from .io import warn, info, debug, fatal


class BaseCacher(with_metaclass(ABCMeta, object)):
    def __init__(self, cache_path):
        if not exists(cache_path):
            makedirs(cache_path)
        self.cache_path = cache_path

    def abspath(self, name):
        return join(self.cache_path, name)

    @abstractmethod
    def check(self, name, **kwargs):
        """
        """

    @abstractmethod
    def cache(self, name, **kwargs):
        """
        """


class TarballCacher(BaseCacher):
    def __init__(self, cache_path):
        cache_path = join(cache_path, 'tarballs')
        super(TarballCacher, self).__init__(cache_path)

    def check(self, name, version=None):
        if version is None:
            cfpath = self.abspath(name)
            if exists(cfpath):
                return cfpath
        else:
            for cfile in listdir(self.cache_path):
                if cfile.startswith(name + '-'):
                    cver = cfile[len(name + '-'):]
                    if cver.endswith('.tar.gz'):
                        ext = len('.tar.gz')
                    elif cver.endswith('.tgz'):
                        ext = len('.tgz')
                    elif cver.endswith('.tar.bz2'):
                        ext = len('.tar.bz2')
                    elif cver.endswith('.zip'):
                        ext = len('.zip')
                    else:
                        warn('Unknown extension on cached file: %s', cfile)
                        continue
                    cver = cver[:-ext]
                    if parse_version(cver) == parse_version(version):
                        return self.abspath(cfile)
        return None


class PlatformStringCacher(BaseCacher):
    cache_file = '__platform_cache.yml'

    def __init__(self, cache_path):
        super(PlatformStringCacher, self).__init__(cache_path)
        self.cache_file = join(cache_path, PlatformStringCacher.cache_file)
        if not exists(self.cache_file):
            with open(self.cache_file, 'w') as handle:
                handle.write(yaml.dump({}))

    def check(self, name, **kwargs):
        platforms = yaml.safe_load(open(self.cache_file).read())
        return platforms.get(name, None)

    def cache(self, name, execctx=None, buildpy='python', **kwargs):
        platforms = yaml.safe_load(open(self.cache_file).read())
        if name not in platforms:
            with execctx() as run:
                # ugly...
                cmd = "python -c 'import os; print os.uname()[4]'"
                arch = run(cmd, capture_output=True).splitlines()[0].strip()
                cmd = ("{buildpy} -c 'import wheel.pep425tags; "
                       "print wheel.pep425tags.get_platforms"
                       "(major_only=True)[0]'".format(buildpy=buildpy))
                cmd = cmd.format(arch=arch)
                platform = run(
                    cmd,
                    capture_output=True
                ).splitlines()[0].strip()
            platforms[name] = platform
            with open(self.cache_file, 'w') as handle:
                handle.write(yaml.dump(platforms))
        return platforms[name]


class UrlCacher(TarballCacher):
    def check(self, name, **kwargs):
        tgz = basename(urlparse(name).path)
        return super(UrlCacher, self).check(tgz)

    def cache(self, name, **kwargs):
        cfpath = self.check(name)
        tgz = basename(urlparse(name).path)
        if cfpath is not None:
            info('Using cached file: %s', cfpath)
        else:
            cfpath = self.abspath(tgz)
            r = requests.get(name)
            with open(cfpath, 'wb') as handle:
                for chunk in r.iter_content(chunk_size=1024):
                    handle.write(chunk)


class PipSourceCacher(TarballCacher):
    def cache(self, name, version=None, fail_ok=False, **kwargs):
        if version is None:
            fatal('A version must be provided when caching from pip')
        cfpath = self.check(name, version=version)
        if cfpath is not None:
            info('Using cached sdist: %s', cfpath)
        else:
            try:
                # TODO: use the pip API
                cmd = [
                    'pip', '--no-cache-dir', 'install', '-d', self.cache_path,
                    '--no-binary', ':all:', '--no-deps', name + '==' + version
                ]
                info('Fetching sdist: %s', name)
                debug('Executing: %s', ' '.join(cmd))
                subprocess.check_call(cmd)
            except subprocess.CalledProcessError:
                if not fail_ok:
                    raise


class CacheManager(object):
    def __init__(self, cache_path):
        self.cache_path = cache_path
        self.cachers = {}
        self.load_cachers()

    def load_cachers(self):
        self.cachers['pip'] = PipSourceCacher(self.cache_path)
        self.cachers['url'] = UrlCacher(self.cache_path)
        self.cachers['platform'] = PlatformStringCacher(self.cache_path)

    def pip_check(self, name, version):
        return self.cachers['pip'].check(name, version=version)

    def url_check(self, name):
        return self.cachers['url'].check(name)

    def platform_check(self, name):
        return self.cachers['platform'].check(name)

    def pip_cache(self, name, version, fail_ok=False):
        return self.cachers['pip'].cache(
            name,
            version=version,
            fail_ok=fail_ok)

    def url_cache(self, name):
        return self.cachers['url'].cache(name)

    def platform_cache(self, name, execctx, buildpy):
        return self.cachers['platform'].cache(
            name,
            execctx=execctx,
            buildpy=buildpy)
