#!/usr/bin/env python

import sys
import argparse
import subprocess
from os.path import abspath, dirname, join


IMAGES = ('natefoo/wheel64:squeeze', 'natefoo/wheel32:squeeze')
WHEELS_DIST_DIR = abspath(join(dirname(__file__), 'wheels', 'dist'))
WHEELS_BUILD_DIR = abspath(join(dirname(__file__), 'wheels', 'build'))
WHEELS_YML = join(WHEELS_BUILD_DIR, 'wheels.yml')


def main():
    parser = argparse.ArgumentParser(description='Build wheels in Docker')
    parser.add_argument('package', help='Package name (in wheels.yml)')
    args =  parser.parse_args()
    for image in IMAGES:
        cmd = [ 'docker', 'run',
                '--volume=%s/:/host/dist/' % WHEELS_DIST_DIR,
                '--volume=%s/:/host/build/:ro' % WHEELS_BUILD_DIR,
                image, 'python', '-u', '/host/build/build.py', args.package ]
        print 'Running docker:', ' '.join(cmd)
        subprocess.check_call(cmd)


if __name__ == '__main__':
    main()
