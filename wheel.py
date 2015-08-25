#!/usr/bin/env python

import os
import sys
import urllib2
import argparse
import subprocess
from os.path import abspath, dirname, join, basename, exists

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

    version = wheels['packages'][args.package]['version']

    if args.image is not None:
        images = [args.image]
    else:
        try:
            imageset = wheels['packages'][args.package]['imageset']
            images = wheels['imagesets'][imageset]
        except:
            images = wheels['imagesets']['default']

    src_cache = join(WHEELS_BUILD_DIR, 'cache')
    if not exists(src_cache):
        os.makedirs(src_cache)

    src_url = wheels['packages'][args.package]['src']
    tgz = join(src_cache, basename(src_url))

    if not exists(tgz):
        with open(tgz, 'w') as handle:
            r = urllib2.urlopen(src_url, None, 15)
            handle.write(r.read())

    plat_cache = join(src_cache, '__platform_cache.json')
    if not exists(plat_cache):
        open(plat_cache, 'w').write(yaml.dump({}))
    platforms = yaml.safe_load(open(plat_cache).read())

    expected = {}

    for image in images:
        plat_name = wheels['images'].get(image, {}).get('plat_name', None)
        if plat_name is None:
            if image not in platforms:
                print 'Caching platform tag for image: %s' % image
                cmd = [ 'docker', 'run', image, '/python/2.6-ucs2/bin/python',
                        '-c', 'import wheel.pep425tags; print '
                        'wheel.pep425tags.get_platforms(major_only=True)[0]' ]
                platforms[image] = subprocess.check_output(cmd).strip()
                print 'Platform tag for %s is: %s' % (image, platforms[image])
                open(plat_cache, 'w').write(yaml.dump(platforms))
            plat_name = platforms[image]
        expected[image] = []
        for py in ('26', '27'):
            for abi_flags in ('m', 'mu'):
                whl = '%s-%s-cp%s-cp%s%s-%s.whl' % (args.package, version, py, py, abi_flags, plat_name)
                expected[image].append(join(WHEELS_DIST_DIR, args.package, whl))

    for image in images:
        for f in expected[image]:
            if not exists(f):
                break
            print '%s exists...' % f
        else:
            print 'Skipping build on %s because all expected wheels exist' % image
            continue
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
        missing = []
        for f in expected[image]:
            if not exists(f):
                missing.append(f)
        if missing:
            print 'The following expected wheels were not found after the attempted build on %s:' % image
            print '\n'.join(missing)
            sys.exit(1)

if __name__ == '__main__':
    main()
