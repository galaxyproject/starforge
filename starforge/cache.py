"""
"""
from __future__ import absolute_import

import subprocess
import sys

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
            name = name.lower()
            for cfile in listdir(self.cache_path):
                if cfile.lower().startswith(name + '-'):
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

    def cache(self, name, execctx=None, buildpy='python', plat_specific=False, **kwargs):
        platforms = yaml.safe_load(open(self.cache_file).read())
        if name not in platforms:
            with execctx() as run:
                # ugly...
                cmd = "python -c 'import os; print os.uname()[4]'"
                arch = run(cmd, capture_output=True).splitlines()[0].strip()
                if plat_specific:
                    cmd = ("{buildpy} -c 'import starforge.interface.wheel; "
                           "print starforge.interface.wheel.get_platforms"
                           "(major_only=True)[0]'".format(buildpy=buildpy))
                else:
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


class PythonVersionCacher(BaseCacher):
    cache_file = '__pyvers_cache.yml'

    def __init__(self, cache_path):
        super(PythonVersionCacher, self).__init__(cache_path)
        self.cache_file = join(cache_path, PythonVersionCacher.cache_file)
        if not exists(self.cache_file):
            with open(self.cache_file, 'w') as handle:
                handle.write(yaml.dump({}))

    def check(self, name, **kwargs):
        versions = yaml.safe_load(open(self.cache_file).read())
        return versions.get(name, None)

    def cache(self, name, execctx=None, buildpy='python', **kwargs):
        versions = yaml.safe_load(open(self.cache_file).read())
        if name not in versions:
            with execctx() as run:
                cmd = "{buildpy} -c 'import sys; print(sys.version_info[0])'".format(buildpy=buildpy)
                vers = run(cmd, capture_output=True).splitlines()[0].strip()
                vers = 'py%d' % int(vers)
            versions[name] = vers
            with open(self.cache_file, 'w') as handle:
                handle.write(yaml.dump(versions))
        return versions[name]


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
        return cfpath


class PipSourceCacher(TarballCacher):
    def cache(self, name, version=None, fail_ok=False, **kwargs):
        if version is None:
            fatal('A version must be provided when caching from pip')
        cfpath = self.check(name, version=version)
        if cfpath is not None:
            info('Using cached sdist: %s', cfpath)
        else:
            try:
                cmd = [
                    'pip', '--no-cache-dir', 'download', '-d', self.cache_path, '--no-binary', ':all:',
                    '--no-deps', name + '==' + version
                ]
                info('Fetching sdist: %s', name)
                debug('Executing: %s', ' '.join(cmd))
                subprocess.check_call(cmd, stdout=sys.stderr)
                cfpath = self.check(name, version=version)
            except subprocess.CalledProcessError:
                if not fail_ok:
                    raise
        return cfpath


class CacheManager(object):
    def __init__(self, cache_path):
        self.cache_path = cache_path
        self.cachers = {}
        self.load_cachers()

    def load_cachers(self):
        self.cachers['pip'] = PipSourceCacher(self.cache_path)
        self.cachers['url'] = UrlCacher(self.cache_path)
        self.cachers['platform'] = PlatformStringCacher(self.cache_path)
        self.cachers['pyversion'] = PythonVersionCacher(self.cache_path)

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

    def platform_cache(self, name, execctx, buildpy, plat_specific=False):
        return self.cachers['platform'].cache(
            name,
            execctx=execctx,
            buildpy=buildpy,
            plat_specific=plat_specific)

    def pyversion_cache(self, name, execctx, buildpy):
        return self.cachers['pyversion'].cache(name, execctx=execctx, buildpy=buildpy)


def cache_wheel_sources(cache_manager, wheel_config):
    fail_ok = wheel_config.sources != []
    sources = []
    sources.append(cache_manager.pip_cache(wheel_config.name, wheel_config.version, fail_ok=fail_ok))
    for src_url in wheel_config.sources:
        sources.append(cache_manager.url_cache(src_url))
    return sources


def check_wheel_source(cache_manager, wheel_config):
    cached_source = cache_manager.pip_check(wheel_config.name, wheel_config.version)
    missing = '%s %s' % (wheel_config.name, wheel_config.version)
    if cached_source is None:
        # check first URL source instead
        if wheel_config.sources:
            cached_source = cache_manager.url_check(wheel_config.sources[0])
            missing = wheel_config.sources[0]
    assert cached_source is not None, 'Cache failure on: %s' % missing
    return cached_source
