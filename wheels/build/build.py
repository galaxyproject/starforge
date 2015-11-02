#!/usr/bin/env python -u

import os
import sys
import shutil
import tarfile
import subprocess
from os.path import basename, join, exists, abspath
from distutils.util import get_platform

import yaml

from pkg_resources import parse_version

from wheel.pep425tags import get_platforms
from wheel.platform import get_specific_platform


# On CentOS 6, build.py runs under Python 2.6
try:
    from argparse import ArgumentParser
except ImportError:
    from optparse import OptionParser

    class ArgumentParser(OptionParser):

        def __init__(self, **kwargs):
            self.delegate = OptionParser(**kwargs)

        def add_argument(self, *args, **kwargs):
            if "required" in kwargs:
                del kwargs["required"]
            return self.delegate.add_option(*args, **kwargs)

        def parse_args(self, args=None):
            (options, args) = self.delegate.parse_args(args)
            return options


WHEELS_YML = join(os.sep, 'host', 'build', 'wheels.yml')
BUILD = join(os.sep, 'build')

SETUPTOOLS_WRAPPER = '''#!/usr/bin/env python
import setuptools
execfile('setup_wrapped.py')
'''

PUREPY_IMAGE = 'galaxy/purepy-wheel'
PUREPY_PYTHON = 'cp27mu'

LINUX_PYTHONS = 'cp26m cp26mu cp27m cp27mu'.split()
OSX_PYTHONS = 'cp26m cp27m'.split()

def execute(cmd, cwd=None):
    print 'EXECUTING:', ' '.join(cmd)
    subprocess.check_call(cmd, cwd=cwd)


def build(args, wheel_dict, plat, purepy=False):
    wheel_name = args.build_wheel
    uid = args.uid
    gid = args.gid
    if not purepy:
        if plat is not None:
            print 'Using platform from wheels.yml: %s' % plat
        else:
            print 'Using default platform: %s' % get_platforms(major_only=True)[0]

    distro = get_specific_platform()
    if distro is not None:
        distro = distro[0]

    if distro in ('debian', 'ubuntu') and wheel_dict.get('apt', []):
        pkgs = wheel_dict['apt']
        if os.uname()[4] == 'i686' and exists('/usr/lib/x86_64-linux-gnu'):
            # multiarch install
            pkgs = map(lambda x: '%s:i386' % x, pkgs)
        os.environ['DEBIAN_FRONTEND'] = 'noninteractive'
        execute(['apt-get', '-qq', 'update'])
        execute(['apt-get', 'install', '--no-install-recommends', '-y'] + pkgs)
    elif distro in ('centos', 'rhel', 'fedora') and wheel_dict.get('yum', []):
        execute(['yum', 'install', '-y'] + wheel_dict['yum'])
    elif distro in ('opensuse', 'sles') and wheel_dict.get('zypper', []):
        execute(['zypper', '-n', 'in'] + wheel_dict['zypper'])
    elif get_platform().startswith('macosx-') and wheel_dict.get('brew', []):
        if '/usr/local/bin' not in os.environ['PATH']:
            os.environ['PATH'] = '/usr/local/bin:' + os.environ['PATH']
        execute(['sudo', '-u', 'admin', 'brew', 'install'] + wheel_dict['brew'], cwd='/tmp')


    dist = join(os.sep, 'host', 'dist')
    dest = join(dist, wheel_name)
    if not exists(dest):
        os.makedirs(dest)
    os.chown(dist, uid, gid)
    os.chown(dest, uid, gid)

    if not exists(BUILD):
        os.makedirs(BUILD)

    os.chdir(BUILD)

    version = str(wheel_dict['version'])
    src_cache = join(os.sep, '/host', 'build', 'cache')
    src_paths = []
    src_urls = wheel_dict.get('src', [])

    for cfile in os.listdir(src_cache):
        if cfile.startswith(wheel_name + '-'):
            cver = cfile[len(wheel_name + '-'):]
            cver = cver.replace('.tar.gz', '').replace('.tgz', '').replace('.tar.bz2', '')
            if parse_version(cver) == parse_version(version):
                src_paths.append(join(src_cache, cfile))
                break
    else:
        if not src_urls:
            raise Exception('Could not find primary sdist in %s' % src_cache)

    if isinstance(src_urls, basestring):
        src_urls = [src_urls]
    for src_url in src_urls:
        src_paths.append(join(src_cache, basename(src_url)))

    for i, tgz in enumerate(src_paths):
        tf = tarfile.open(tgz)
        roots = set()
        for name in tf.getnames():
            roots.add(name.split(os.sep, 1)[0])
        assert len(roots) == 1, "Could not determine root directory in archive"
        root_t = abspath(join(os.getcwd(), roots.pop()))
        os.environ['SRC_ROOT_%d' % i] = root_t
        # will cd to first root
        if i == 0:
            os.environ['SRC_ROOT'] = root_t
            root = root_t

        # TODO: insecure, but hey, it's docker, soooo
        tf.extractall(BUILD)

    prebuild = wheel_dict.get('prebuild', None)
    if prebuild is not None:
        subprocess.check_call(prebuild, shell=True)

    os.chdir(join(BUILD, root))

    if wheel_dict.get('insert_setuptools', False):
        os.rename('setup.py', 'setup_wrapped.py')
        with open('setup.py', 'w') as handle:
            handle.write(SETUPTOOLS_WRAPPER)

    if get_platform().startswith('macosx-'):
        pythons = OSX_PYTHONS
    else:
        if wheel_dict.get('force_pythons', None):
            pythons = wheel_dict['force_pythons']
        elif purepy:
            pythons = [PUREPY_PYTHON]
        else:
            pythons = LINUX_PYTHONS

    for py in pythons:
        py = '%s-%s' % (py, os.uname()[4])
        build_args = []
        if get_platform().startswith('macosx-') and wheel_dict.get('brew', []):
            build_args.extend(['build_ext', '-I', '/usr/local/include', '-L', '/usr/local/lib', '-R', '/usr/local/lib'])
        build_args.extend(wheel_dict.get('build_args', 'bdist_wheel').split())
        cmd = [join(os.sep, 'python', py, 'bin', 'python'), 'setup.py'] + build_args
        if plat is not None:
            cmd.append('--plat-name=%s' % plat)
        execute(cmd)
        shutil.rmtree('build')

    # Sorta lazy, we should explicitly state whether or not an sdist should be built
    if not get_platform().startswith('macosx-'):
        py = '%s-%s' % (PUREPY_PYTHON, os.uname()[4])
        cmd = [join(os.sep, 'python', py, 'bin', 'python'), 'setup.py', 'sdist']
        execute(cmd)
    
    for f in os.listdir('dist'):
        shutil.copy(join('dist', f), dest)
        os.chown(join(dest, f), uid, gid)


def main():
    parser = ArgumentParser(description='Build wheel')
    parser.add_argument('-i', '--tag', default=None,
            help='Tag of the image on which the wheel is building')
    parser.add_argument('-u', '--uid', type=int, default=-1,
            help='Change ownership of output wheels to UID')
    parser.add_argument('-g', '--gid', type=int, default=-1,
            help='Change group of output wheels to GID')
    parser.add_argument('build_wheel', help='Package name (in wheels.yml)')
    args =  parser.parse_args()

    with open(WHEELS_YML, 'r') as handle:
        wheels = yaml.load(handle)

    plat = wheels.get('images', {}).get(args.tag, {}).get('plat_name', None)
    wheel_dict = wheels['packages'].get(args.build_wheel, None) or wheels['purepy_packages'][args.build_wheel]

    build(args, wheel_dict, plat, purepy=args.build_wheel in wheels['purepy_packages'])


if __name__ == '__main__':
    main()
