"""
Forge wheels
"""
from __future__ import absolute_import

import os
import shlex
import subprocess
from os import (
    chdir,
    chown,
    getcwd,
    listdir,
    makedirs,
    rename,
    uname
)
from os.path import (
    abspath,
    dirname,
    exists,
    join
)
from shutil import (
    copy,
    rmtree
)

from pkg_resources import parse_version
from six import iteritems

from ..cache import CacheManager, cache_wheel_sources, check_wheel_source
from ..config.wheels import WheelConfigManager
from ..execution.docker import DockerExecutionContext
from ..execution.local import LocalExecutionContext
from ..execution.qemu import QEMUExecutionContext
from ..io import debug, info, warn
from ..packaging.setup import check_setup, wheel_info, wrap_setup
from ..util import Archive, pip_install, py_to_pip


AUDITWHEEL_CMD = 'for whl in dist/*.whl; do auditwheel {auditwheel_args} $whl; rm $whl; done'
DELOCATE_CMD = 'for whl in dist/*.whl; do delocate-wheel {delocate_args} $whl; done'
DEFAULT_AUDITWHEEL_ARGS = 'repair -w dist'
DEFAULT_DELOCATE_ARGS = '-v'


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
        return cache_wheel_sources(self.cache_manager, self.wheel_config)

    def get_expected_names(self):
        wheels = []
        py = 'py2'
        if self.wheel_config.purepy:
            if self.wheel_config.universal:
                py = 'py2.py3'
            else:
                py = self.cache_manager.pyversion_cache(
                    self.image.name,
                    self.exec_context,
                    self.image.pythons[0])
            whl = ('{name}-{version}-{py}-none-any.whl'
                   .format(name=self.name.replace('-', '_'),
                           version=str(parse_version(self.version)),
                           py=py))
            wheels = [whl]
        else:
            platform = None
            if self.image:
                # get forced platform name if any
                platform = self.image.plat_name
            if platform is None:
                platform = self.cache_manager.platform_cache(
                    self.image.name,
                    self.exec_context,
                    self.image.pythons[0],
                    self.image.plat_specific)
            for python, py_abi_tag in zip(self.image.pythons, self.image.py_abi_tags):
                if not py_abi_tag:
                    # FIXME: this forces a very specific naming (i.e. '/pythons/cp{py}{flags}-{arch}/')
                    for py_abi_tag in python.split('/'):
                        if py_abi_tag.startswith('cp'):
                            break
                whl = ('{name}-{version}-{py_abi}-{platform}.whl'
                       .format(name=self.name.replace('-', '_'),
                               version=str(parse_version(self.version)),
                               py_abi=py_abi_tag,
                               platform=platform))
                wheels.append(whl)
        return wheels

    def get_sdist_expected_names(self):
        tarballs = []
        extensions = ('zip', 'tar.gz')
        for ext in extensions:
            tarballs.append('{name}-{version}.{ext}'
                            .format(name=self.name,
                                    version=str(parse_version(self.version)),
                                    ext=ext))
        return tarballs

    def execute(self, cmd, cwd=None, capture_output=False):
        debug('Executing: %s', ' '.join(cmd))
        with self.exec_context() as run:
            return run(cmd, cwd=cwd, capture_output=capture_output)

    def _get_prebuild_command(self, step):
        prebuild = self.wheel_config.prebuild
        # if prebuild is just a string then it's the `all` prebuild
        # command, but a dict with an explicit `all` key is also allowed
        # (and allows for `all` in combination with other prebuild commands)
        if step != 'all' and not isinstance(prebuild, dict):
            prebuild = None
        elif step != 'all' or isinstance(prebuild, dict):
            prebuild = prebuild.get(step, None)
        debug("Prebuild command for '%s' step is: %s", step, prebuild)
        return prebuild

    def _prep_build(self, build, output, uid, gid):
        if output:
            if not exists(output):
                makedirs(output)
            chown(output, uid, gid)

        src_paths = []
        pip_path = self.cache_manager.pip_check(self.name, self.version)
        if pip_path is not None:
            src_paths.append(pip_path)
        for src_url in self.wheel_config.sources:
            src_paths.append(self.cache_manager.url_check(src_url))

        root = None

        for i, arc_path in enumerate(src_paths):
            arc = Archive.open(arc_path)
            root_t = abspath(join(getcwd(), arc.root))
            os.environ['SRC_ROOT_%d' % i] = root_t
            # will cd to first root
            if i == 0:
                os.environ['SRC_ROOT'] = root_t
                root = root_t
            # TODO: don't use extractall (but since we *should* be running
            # under docker, we shouldn't need to care)
            arc.extractall(build)

        assert root is not None, "Unable to determine root directory"

        prebuild = self._get_prebuild_command('all')
        if prebuild is not None:
            subprocess.check_call(prebuild, shell=True)

        return root

    def _build_py_pip_install(self, pythons, packages, dependency_type=None):
        if not packages:
            return
        for py in pythons:
            info("Installing %s dependencies for build Python '%s': %s", dependency_type, py, ', '.join(packages))
            pip_install(pip=py_to_pip(py), packages=packages, executor=self.execute)

    def bdist_wheel(self, output=None, uid=-1, gid=-1):
        # TODO: a lot of stuff in this method like installing from the package
        # manager and changing permissions should be abstracted out for
        # non-wheel executions
        uid = int(uid)
        gid = int(gid)
        arch = uname()[4]
        build = abspath(getcwd())
        pythons = []
        if self.image:
            pythons = []
            for py in self.image.pythons:
                pythons.append(py.format(arch=arch))
            pythons = self.image.pythons
            platform = self.image.plat_name
            pkgtool = self.image.pkgtool
        else:
            pythons = ['python']
            platform = None
            pkgtool = None
        if platform is not None and self.image.force_plat:
            info('Platform name forced to: %s', platform)

        info("Entered bdist_wheel forge, image '%s', wheel '%s-%s'", self.image.name, self.name, self.version)

        for buildenv in (self.image.buildenv, self.wheel_config.buildenv):
            if buildenv:
                debug("Adding to build environment:")
                for k, v in iteritems(buildenv):
                    debug("%s=%s", k, v)
                    os.environ[k] = str(v)

        pkgs = self.wheel_config.get_dependencies(self.image.name)
        if pkgs:
            if pkgtool == 'apt':
                if arch == 'i686' and exists('/usr/lib/x86_64-linux-gnu'):
                    # multiarch install
                    pkgs = ['%s:i386' % x for x in pkgs]
                os.environ['DEBIAN_FRONTEND'] = 'noninteractive'
                self.execute(['apt-get', '-qq', 'update'])
                self.execute(['apt-get', 'install',
                              '--no-install-recommends', '-y'] + pkgs)
            elif pkgtool == 'yum':
                self.execute(['yum', 'install', '-y'] + pkgs)
            elif pkgtool == 'zypper':
                self.execute(['zypper', '-n', 'in'] + pkgs)
            elif pkgtool == 'brew':
                if '/usr/local/bin' not in os.environ['PATH']:
                    os.environ['PATH'] = '/usr/local/bin:' + os.environ['PATH']
                # brew exits 1 if a package is already installed
                installed = set(self.execute(['brew', 'list', '-1'], cwd='/tmp', capture_output=True).splitlines())
                needed = set(pkgs) - installed
                if needed:
                    self.execute(['brew', 'install'] + list(needed), cwd='/tmp')
            else:
                warn('Skipping installation of dependencies: %s',
                     ', '.join(pkgs))

        root = self._prep_build(build, output, uid, gid)

        prebuild = self._get_prebuild_command('wheel')
        if prebuild is not None:
            subprocess.check_call(prebuild, shell=True)

        chdir(join(build, root))

        # TODO: caching from the host would be nice but that requires pip's cache dir to be writable and owned by the
        # guest user, and with docker run --user, the pythons aren't writable

        # install setup requirements (these can be defined by the setup script but that presents a catch-22, so only
        # check the wheel config
        self._build_py_pip_install([self.image.buildpy], self.wheel_config.setup_requires,
            dependency_type='Starforge image Python setup_requires')
        self._build_py_pip_install(pythons, self.wheel_config.setup_requires, dependency_type='setup_requires')

        insert_setuptools = self.wheel_config.insert_setuptools
        if insert_setuptools is None:
            # if set explicitly to false, do not override with check_setup()
            insert_setuptools = not check_setup()

        if insert_setuptools or self.image.plat_specific:
            wrap_setup(
                import_interface_wheel=self.image.plat_specific,
                import_setuptools=insert_setuptools)

        # install anything defined by the package itself, overrideable by the wheel config
        install_requires = self.wheel_config.install_requires
        if install_requires is None:
            install_requires = wheel_info()['install_requires']
        self._build_py_pip_install(pythons, install_requires, dependency_type='install_requires')

        # install anything else the wheel config author wants installed
        self._build_py_pip_install(pythons, self.wheel_config.pip_install, dependency_type='wheel config pip_install')

        for py in pythons:
            build_args = []
            if pkgs and pkgtool == 'brew':
                build_args.extend(['build_ext',
                                   '-I', '/usr/local/include',
                                   '-L', '/usr/local/lib',
                                   '-R', '/usr/local/lib'])
            build_args.extend(shlex.split(self.wheel_config.build_args))
            cmd = [py, 'setup.py'] + build_args
            if platform is not None and self.image.force_plat:
                cmd.append('--plat-name=%s' % platform)
            self.execute(cmd)
            rmtree('build')

        if self.image.use_auditwheel:
            auditwheel_cmd = AUDITWHEEL_CMD.format(auditwheel_args=self.wheel_config.auditwheel_args or DEFAULT_AUDITWHEEL_ARGS)
            info('Running auditwheel command: %s', auditwheel_cmd)
            subprocess.check_call(auditwheel_cmd, shell=True)

        if self.image.use_delocate:
            delocate_cmd = DELOCATE_CMD.format(delocate_args=self.wheel_config.delocate_args or DEFAULT_DELOCATE_ARGS)
            info('Running delocate command: %s', delocate_cmd)
            subprocess.check_call(delocate_cmd, shell=True)

        if self.image.postbuild is not None:
            info('Running image postbuild command: %s', self.image.postbuild)
            subprocess.check_call(self.image.postbuild, shell=True)

        if output:
            for f in listdir('dist'):
                copy(join('dist', f), output)
                chown(join(output, f), uid, gid)

    def sdist(self, output=None, uid=-1, gid=-1):
        uid = int(uid)
        gid = int(gid)
        arch = uname()[4]
        build = abspath(getcwd())
        root = self._prep_build(build, output, uid, gid)
        prebuild = self._get_prebuild_command('sdist')
        if prebuild is not None:
            subprocess.check_call(prebuild, shell=True)
        chdir(join(build, root))
        if self.image:
            python = self.image.pythons[0].format(arch=arch)
        else:
            python = 'python'
        cmd = [python, 'setup.py', 'sdist']
        self.execute(cmd)
        if output:
            for f in listdir('dist'):
                copy(join('dist', f), output)
                chown(join(output, f), uid, gid)


def build_forges(global_config, wheels_config, wheel, images=None, **kwargs):
    wheel_cfgmgr = WheelConfigManager.open(global_config, wheels_config)
    cachemgr = CacheManager(global_config.cache_path)
    wheel_config = wheel_cfgmgr.get_wheel_config(wheel)
    images = images or wheel_config.images
    for (image_name, image_conf) in iteritems(images):
        debug("Read image config: %s, image: %s, plat_name: %s, force_plat: %s",
              image_name, image_conf.image, image_conf.plat_name, image_conf.force_plat)
        if image_conf.type == 'local':
            ectx = LocalExecutionContext(image_conf, **kwargs)
        if image_conf.type == 'docker':
            ectx = DockerExecutionContext(image_conf, global_config.docker, **kwargs)
        elif image_conf.type == 'qemu':
            ectx = QEMUExecutionContext(image_conf, global_config.qemu, **kwargs)
        yield ForgeWheel(wheel_config, cachemgr, ectx.run_context, image=image_conf)
