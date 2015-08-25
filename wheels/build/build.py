#!/usr/bin/env python -u

import os
import sys
import shutil
import tarfile
import subprocess
from os.path import basename, join, exists
from distutils.util import get_platform

import yaml

from wheel.pep425tags import get_platforms
from wheel.platform import get_specific_platform


WHEELS_YML = join(os.sep, 'host', 'build', 'wheels.yml')
BUILD = join(os.sep, 'build')

SETUPTOOLS_WRAPPER = '''#!/usr/bin/env python
import setuptools
execfile('setup_wrapped.py')
'''

PYTHONS = '2.6-ucs2 2.6-ucs4 2.7-ucs2 2.7-ucs4'.split()

def execute(cmd):
    print 'EXECUTING:', ' '.join(cmd)
    subprocess.check_call(cmd)


def build(wheel_name, wheel_dict, plat):
    src_url = wheel_dict['src']
    tgz = join(os.sep, '/host', 'build', 'cache', basename(src_url))

    if 'imageset' not in wheel_dict:
        bits = int(subprocess.Popen(['getconf', 'LONG_BIT'], stdout=subprocess.PIPE).stdout.read())
        if bits == 64:
            plat = 'linux_x86_64'
        elif bits == 32:
            plat = 'linux_i686'
        else:
            raise Exception("Sorry, can't run on your PDP-11 (`getconf LONG_BIT` produced: %s)")
        print 'Platform is: %s' % plat
    elif plat is not None:
        print 'Using platform from wheels.yml: %s' % plat
    else:
        print 'Using default platform: %s' % get_platforms(major_only=True)[0]


    distro = get_specific_platform()
    if distro is not None:
        distro = distro[0]

    if distro in ('debian', 'ubuntu') and wheel_dict.get('apt', []):
        os.environ['DEBIAN_FRONTEND'] = 'noninteractive'
        execute(['apt-get', '-qq', 'update'])
        execute(['apt-get', 'install', '--no-install-recommends', '-y'] + wheel_dict['apt'])
    elif distro in ('centos', 'rhel') and wheel_dict.get('yum', []):
        execute(['yum', 'install', '-y'] + wheel_dict['yum'])
    elif distro in ('opensuse', 'sles') and wheel_dict.get('zypper', []):
        execute(['zypper', '-n', 'in'] + wheel_dict['zypper'])

    dest = join(os.sep, 'host', 'dist', wheel_name)
    if not exists(dest):
        os.makedirs(dest)

    if not exists(BUILD):
        os.makedirs(BUILD)

    tf = tarfile.open(tgz)
    roots = set()
    for name in tf.getnames():
        roots.add(name.split(os.sep, 1)[0])
    assert len(roots) == 1, "Could not determine root directory in archive"
    root = roots.pop()

    # TODO: insecure, but hey, it's docker, soooo
    tf.extractall(BUILD)

    os.chdir(join(BUILD, root))

    if wheel_dict.get('insert_setuptools', False):
        os.rename('setup.py', 'setup_wrapped.py')
        with open('setup.py', 'w') as handle:
            handle.write(SETUPTOOLS_WRAPPER)

    for py in PYTHONS:
        cmd = [join(os.sep, 'python', py, 'bin', 'python'), 'setup.py', 'bdist_wheel']
        if plat is not None:
            cmd.append('--plat-name=%s' % plat)
        execute(cmd)
        shutil.rmtree('build')
    
    for f in os.listdir('dist'):
        shutil.copy(join('dist', f), dest)


def main():
    build_wheel = sys.argv[1]
    with open(WHEELS_YML, 'r') as handle:
        wheels = yaml.load(handle)

    try:
        tag = sys.argv[2]
    except:
        tag = None
    plat = wheels.get('images', {}).get(tag, {}).get('plat_name', None)

    build(build_wheel, wheels['packages'][build_wheel], plat)


if __name__ == '__main__':
    main()
