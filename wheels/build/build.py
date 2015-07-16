#!/usr/bin/env python -u

import os
import sys
import shutil
import urllib2
import tarfile
import subprocess
from os.path import basename, join, exists

# FIXME: new image w/ python-yaml preinstalled pls
os.environ['DEBIAN_FRONTEND'] = 'noninteractive'
subprocess.check_call(['apt-get', 'install', '-y', 'python-yaml'])

import yaml

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


def build(wheel_name, wheel_dict):
    src_url = wheel_dict['src']
    tgz = join('/build', basename(src_url))

    bits = int(subprocess.Popen(['getconf', 'LONG_BIT'], stdout=subprocess.PIPE).stdout.read())

    if bits == 64:
        plat = 'linux_x86_64'
    elif bits == 32:
        plat = 'linux_i686'
    else:
        raise Exception("Sorry, can't run on your PDP-11 (`getconf LONG_BIT` produced: %s)")

    print 'Platform is: %s' % plat

    if wheel_dict.get('apt', []):
        execute(['apt-get', 'install', '-y'] + wheel_dict['apt'])


    dest = join(os.sep, 'host', 'dist', wheel_name)
    if not exists(dest):
        os.makedirs(dest)

    if not exists(BUILD):
        os.makedirs(BUILD)

    with open(tgz, 'w') as handle:
        r = urllib2.urlopen(src_url, None, 15)
        handle.write(r.read())

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
        cmd = [join(os.sep, 'python', py, 'bin', 'python'), 'setup.py', 'bdist_wheel', '--plat-name=%s' % plat]
        execute(cmd)
        shutil.rmtree('build')
    
    for f in os.listdir('dist'):
        shutil.copy(join('dist', f), dest)


def main():
    build_wheel = sys.argv[1]
    with open(WHEELS_YML, 'r') as handle:
        wheels = yaml.load(handle)

    build(build_wheel, wheels['packages'][build_wheel])

    if not build_wheel:
        for wheel_name, wheel_dict in wheels['packages'].items():
            build(wheel_name, wheel_dict)
    else:
        build(build_wheel, wheels['packages'][build_wheel])


if __name__ == '__main__':
    main()
