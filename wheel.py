#!/usr/bin/env python

import os
import sys
import urllib2
import argparse
import subprocess
from os.path import abspath, dirname, join, basename

import yaml


WHEELS_DIST_DIR = abspath(join(dirname(__file__), 'wheels', 'dist'))
WHEELS_BUILD_DIR = abspath(join(dirname(__file__), 'wheels', 'build'))
WHEELS_YML = join(WHEELS_BUILD_DIR, 'wheels.yml')


def main():
    parser = argparse.ArgumentParser(description='Build wheels in Docker')
    parser.add_argument('--image', '-i', help='Build only on this image')
    parser.add_argument('package', help='Package name (in wheels.yml)')
    args =  parser.parse_args()

    with open(WHEELS_YML, 'r') as handle:
        wheels = yaml.load(handle)

    assert args.package in wheels['packages'], 'Not in %s: %s' % (WHEELS_YML, args.package)

    if args.image is not None:
        images = [args.image]
    else:
        try:
            imageset = wheels['packages'][args.package]['imageset']
            images = wheels['imagesets'][imageset]
        except:
            images = wheels['imagesets']['default']

    src_cache = join(WHEELS_BUILD_DIR, 'cache')
    if not os.path.exists(src_cache):
        os.makedirs(src_cache)

    src_url = wheels['packages'][args.package]['src']
    tgz = join(src_cache, basename(src_url))

    if not os.path.exists(tgz):
        with open(tgz, 'w') as handle:
            r = urllib2.urlopen(src_url, None, 15)
            handle.write(r.read())

    for image in images:
        try:
            buildpy = wheels['images'][image]['buildpy']
        except:
            buildpy = 'python'
        cmd = [ 'docker', 'run',
                '--volume=%s/:/host/dist/' % WHEELS_DIST_DIR,
                '--volume=%s/:/host/build/:ro' % WHEELS_BUILD_DIR,
                image, buildpy, '-u', '/host/build/build.py', args.package, image ]
        print 'Running docker:', ' '.join(cmd)
        subprocess.check_call(cmd)


if __name__ == '__main__':
    main()
