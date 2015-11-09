"""
Forge wheels
"""
from __future__ import absolute_import

import os
import shlex
import subprocess
import tarfile
from os import uname, makedirs, chown, getcwd, chdir, rename, listdir, getuid, getgid
from os.path import exists, join, abspath
from shutil import rmtree, copy

from pkg_resources import parse_version
from wheel.pep425tags import get_platforms

from ..io import debug, info, warn
from ..util import Archive


SETUPTOOLS_WRAPPER = '''#!/usr/bin/env python
import setuptools
execfile('setup_wrapped.py')
'''


class ForgeWheel(object):
    def __init__(self, wheel_config, cache_manager, exec_context, image=None):
        self.wheel_config = wheel_config
        self.name = wheel_config.name
        self.version = wheel_config.version
        self.src_urls = wheel_config.sources
        self.cache_manager = cache_manager
        self.exec_context = exec_context
        self.image = image

    def cache_sources(self):
        fail_ok = self.src_urls != []
        self.cache_manager.pip_cache(self.name, self.version, fail_ok=fail_ok)
        for src_url in self.src_urls:
            self.cache_manager.url_cache(src_url)

    def get_expected_names(self):
        wheels = []
        py = 'py2'
        if self.wheel_config.purepy:
            # need to check universal
            cached_source = self.cache_manager.pip_check(self.name, self.version)
            arc = Archive.open(cached_source)
            if arc.universal:
                py = 'py2.py3'
            whl = '{name}-{version}-{py}-none-any.whl'.format(name=self.name.replace('-', '_'),
                                                              version=str(parse_version(self.version)),
                                                              py=py)
            wheels = [whl]
        else:
            platform = None
            if self.image:
                # get forced platform name if any
                platform = self.image.plat_name
            if platform is None:
                platform = self.cache_manager.platform_cache(self.image.name, self.exec_context, self.image.pythons[0])
            for python in self.image.pythons:
                # FIXME: this forces a very specific naming (i.e. '/pythons/cp{py}{flags}-{arch}/')
                abi = python.split('/')[2].split('-')[0]
                py = abi[2:4]
                whl = '{name}-{version}-cp{py}-{abi}-{platform}.whl'.format(name=self.name.replace('-', '_'),
                                                                            version=str(parse_version(self.version)),
                                                                            py=py,
                                                                            abi=abi,
                                                                            platform=platform)
                wheels.append(whl)
        return wheels


    def execute(self, cmd, cwd=None):
        debug('Executing: %s', ' '.join(cmd))
        with self.exec_context() as run:
            run(cmd, cwd=cwd)

    def bdist_wheel(self, output=None, uid=-1, gid=-1):
        # TODO: a lot of stuff in this method like installing from the package
        # manager and changing permissions should be abstracted out for
        # non-wheel executions
        uid = int(uid)
        gid = int(gid)
        arch = uname()[4]
        build = abspath(getcwd())
        name = self.wheel_config.name
        version = self.wheel_config.version
        pythons = []
        if self.image:
            pythons = self.image.pythons
            platform = self.image.plat_name
            pkgtool = self.image.pkgtool
        else:
            pythons = ['python']
            platform = None
            pkgtool = None
        if platform is not None:
            info('Platform name forced to: %s', platform)

        pkgs = self.wheel_config.get_dependencies(self.image.name)
        if pkgs:
            if pkgtool == 'apt':
                if arch == 'i686' and exists('/usr/lib/x86_64-linux-gnu'):
                    # multiarch install
                    pkgs = map(lambda x: '%s:i386' % x, pkgs)
                os.environ['DEBIAN_FRONTEND'] = 'noninteractive'
                self.execute(['apt-get', '-qq', 'update'])
                self.execute(['apt-get', 'install', '--no-install-recommends', '-y'] + pkgs)
            elif pkgtool == 'yum':
                self.execute(['yum', 'install', '-y'] + pkgs)
            elif pkgtool == 'zypper':
                self.execute(['zypper', '-n', 'in'] + pkgs)
            elif pkgtool == 'brew':
                if '/usr/local/bin' not in os.environ['PATH']:
                    os.environ['PATH'] = '/usr/local/bin:' + os.environ['PATH']
                self.execute(['sudo', '-u', 'admin', 'brew', 'install'] + pkgs, cwd='/tmp')
            else:
                warn('Skipping installation of dependencies: %s', ', '.join(pkgs))

        if output:
            if not exists(output):
                makedirs(output)
            chown(output, uid, gid)

        src_paths = [self.cache_manager.pip_check(name, version)]
        for src_url in self.wheel_config.sources:
            src_paths.append(self.cache_manager.url_check(name))

        for i, arc_path in enumerate(src_paths):
            arc = Archive.open(arc_path)
            assert len(arc.roots) == 1, "Could not determine root directory in archive"
            root = next(iter(arc.roots))
            root_t = abspath(join(getcwd(), root))
            os.environ['SRC_ROOT_%d' % i] = root_t
            # will cd to first root
            if i == 0:
                os.environ['SRC_ROOT'] = root_t
                root = root_t
            # TODO: don't use extractall (but since we *should* be running
            # under docker, we shouldn't need to care)
            arc.extractall(build)

        prebuild = self.wheel_config.prebuild
        if prebuild is not None:
            subprocess.check_call(prebuild, shell=True)

        chdir(join(build, root))

        if self.wheel_config.insert_setuptools:
            rename('setup.py', 'setup_wrapped.py')
            with open('setup.py', 'w') as handle:
                handle.write(SETUPTOOLS_WRAPPER)

        for py in pythons:
            py = py.format(arch=arch)
            build_args = []
            if pkgs and pkgtool == 'brew':
                build_args.extend(['build_ext', '-I', '/usr/local/include', '-L', '/usr/local/lib', '-R', '/usr/local/lib'])
            build_args.extend(shlex.split(self.wheel_config.build_args))
            cmd = [py, 'setup.py'] + build_args
            if platform is not None:
                cmd.append('--plat-name=%s' % platform)
            self.execute(cmd)
            rmtree('build')

        if output:
            for f in listdir('dist'):
                copy(join('dist', f), output)
                chown(join(output, f), uid, gid)

    def sdist(self, output=None, uid=-1, gid=-1):
        # TODO: implement
        py = pythons[0].format(arch=arch)
        cmd = [py, 'setup.py', 'sdist']
        self.execute(cmd)
