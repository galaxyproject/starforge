#!/usr/bin/env python
import os
import sys
import urllib2
import uuid
import argparse
import subprocess
from os.path import abspath, dirname, join, basename, exists, expanduser
from time import sleep

from pkg_resources import parse_version

import yaml


WHEELS_DIST_DIR = abspath(join(dirname(__file__), 'wheels', 'dist'))
WHEELS_BUILD_DIR = abspath(join(dirname(__file__), 'wheels', 'build'))
WHEELS_YML = join(WHEELS_BUILD_DIR, 'wheels.yml')

CONFIG_HOME = expanduser(os.environ.get('XDG_CONFIG_HOME', '~/.config'))
CONFIG_FILE = abspath(join(CONFIG_HOME, 'galaxy-starforge', 'config.yml'))
CONFIG_DEFAULT = {
    'wheel_osx_qemu': {
        'qemu_use_sudo': False,
        'btrfs_use_sudo': False,
        'run_cmd': 'qemu-system-x86_64',
        'run_args':
            '-enable-kvm '
            '-m 2048 '
            '-cpu core2duo '
            '-machine q35 '
            '-usb -device usb-kbd -device usb-mouse '
            '-device isa-applesmc,osk={osk} '
            '-kernel {bootloader} '
            '-vga std '
            '-vnc none '
            '-daemonize '
            '-smbios type=2 '
            '-device ide-drive,bus=ide.2,drive=MacHDD '
            '-drive id=MacHDD,if=none,file={diskimage} '
            '-netdev user,id=hub0port0,hostfwd=tcp:127.0.0.1:{sshport}-:22 '
            '-device e1000-82545em,netdev=hub0port0,id=mac_vnet0 '
            '-device ide-drive,bus=ide.4,drive=wheels '
            '-drive id=wheels,if=none,file=fat:rw:{wheels},format=raw',
        # relative to snap_root/snap_src
        'bootloader': 'boot',
        'diskimage': 'macintosh_hd.img',
        'ssh': {
            # You should probably change `host` to avoid ssh host key
            # conflicts. An ~/.ssh/config entry like this should work:
            # Host osxguest:
            #   Hostname localhost
            #   User root
            #   Port 8222
            # If you don't do this, be aware that '-p' is not automatically set
            # for you, so in that case you would need to add it to args.
            'args': [],
            'host': 'localhost',
            'port': '8222'
        },
        # qemu > 2.4 should have a label= option for fat drives
        'wheel_volume': '/Volumes/Untitled'
    }
}


def dict_merge(old, new):
    for k, v in new.items():
        if type(v) == dict:
            dict_merge(old[k], new[k])
        else:
            old[k] = v


def read_config():
    config = CONFIG_DEFAULT
    try:
        user_config = yaml.safe_load(open(CONFIG_FILE).read())
    except (OSError, IOError) as exc:
        if exc.errno == ernno.ENOENT:
            user_config = {}
        else:
            raise

    dict_merge(config, user_config)

    # set userhost
    ssh_config = config['wheel_osx_qemu']['ssh']
    ssh_config['userhost'] = ssh_config['host']
    if 'user' in ssh_config:
        ssh_config['userhost'] = ssh_config['user'] + '@' + ssh_config['host']
    if not type(ssh_config['args']) == list:
        ssh_config['args'] = ssh_config['args'].split()

    return config


def docker(images, purepy, args, version, wheels):
    src_cache = join(WHEELS_BUILD_DIR, 'cache')
    plat_cache = join(src_cache, '__platform_cache.json')
    if not exists(plat_cache):
        open(plat_cache, 'w').write(yaml.dump({}))
    platforms = yaml.safe_load(open(plat_cache).read())

    expected = {}

    norm = lambda x: str(x).replace('-', '_')
    for image in images:
        if purepy:
            whl = '%s-%s-py2-none-any.whl' % (norm(args.package), norm(version))
            expected[image] = [join(WHEELS_DIST_DIR, args.package, whl)]
        else:
            plat_name = wheels['images'].get(image, {}).get('plat_name', None)
            if plat_name is None:
                if image not in platforms:
                    print 'Caching platform tag for image: %s' % image
                    cmd = [ 'docker', 'run', '--rm', image, 'python', '-c',
                            'import wheel.pep425tags; print '
                            'wheel.pep425tags.get_platforms(major_only=True)[0]' ]
                    platforms[image] = subprocess.check_output(cmd).strip()
                    print 'Platform tag for %s is: %s' % (image, platforms[image])
                    open(plat_cache, 'w').write(yaml.dump(platforms))
                plat_name = platforms[image]
            expected[image] = []
            for py in ('26', '27'):
                for abi_flags in ('m', 'mu'):
                    whl = '%s-%s-cp%s-cp%s%s-%s.whl' % (norm(args.package), norm(version), py, py, abi_flags, plat_name)
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
        cmd = [ 'docker', 'run', '--rm',
                '--volume=%s/:/host/dist/' % WHEELS_DIST_DIR,
                '--volume=%s/:/host/build/:ro' % WHEELS_BUILD_DIR,
                image, buildpy, '-u', '/host/build/build.py',
                '-i', image, '-u', str(os.getuid()), '-g', str(os.getgid()),
                args.package ]
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


def osx_ssh(cmd, qemu_ssh_config):
    if isinstance(cmd, basestring):
        cmd = cmd.split()
    cmd = ['ssh'] + qemu_ssh_config['args'] + [qemu_ssh_config['userhost'], '--'] + cmd
    print 'Running:', ' '.join(cmd)
    subprocess.check_call(cmd)


def osx_scp(cmd, qemu_ssh_config):
    if isinstance(cmd, basestring):
        cmd = cmd.split()
    cmd = ['scp'] + qemu_ssh_config['args'] + cmd
    print 'Running:', ' '.join(cmd)
    subprocess.check_call(cmd)


def osx_qemu(args):
    config = read_config()
    qemu_config = config['wheel_osx_qemu']
    qemu_sudo = ['sudo'] if qemu_config['qemu_use_sudo'] else []
    btrfs_sudo = ['sudo'] if qemu_config['btrfs_use_sudo'] else []
    dist = 'wheels/dist/%s' % args.package
    if not os.path.exists(dist):
        os.makedirs(dist)
    work_snap = None
    if not args.no_qemu_boot:
        # ensure all the needed args are set
        wheels_dir = join(os.getcwd(), 'wheels')
        sshport = qemu_config['ssh']['port']
        osk = qemu_config.get('osk', None)
        assert osk is not None, 'Please set your OSK in %s' % CONFIG_FILE
        work_snap = join(qemu_config['snap_root'], '@' + str(uuid.uuid1()))
        bootloader = join(work_snap, qemu_config['bootloader'])
        diskimage = join(work_snap, qemu_config['diskimage'])

        # create a snapshot and boot
        cmd = btrfs_sudo + 'btrfs subvolume snapshot {src} {dest}'.format(src=join(qemu_config['snap_root'], qemu_config['snap_src']), dest=work_snap).split()
        print 'Creating snapshot:', ' '.join(cmd)
        subprocess.check_call(cmd)
        cmd = qemu_sudo + [qemu_config['run_cmd']] + qemu_config['run_args'].format(bootloader=bootloader, diskimage=diskimage, osk=osk, sshport=sshport, wheels=wheels_dir).split()
        print 'Running qemu-system:', ' '.join(cmd)
        subprocess.check_call(cmd)
    else:
        print 'QEMU boot not requested, assuming the guest is already booted...'
    # the first call to ssh will hang until the system is mostly booted. after
    # that it may fail until it's fully up, so try a few times until we can be
    # pretty sure that it's up
    print 'Waiting for SSH server response...'
    for i in range(0, 6):
        try:
            osx_ssh('/usr/bin/true', qemu_config['ssh'])
            print 'SSH server responded'
            break
        except subprocess.CalledProcessError as exc:
            print 'SSH connection test failed, retry %s' % (i + 1)
            sleep(5)
    # fat:ro can't be mounted in the guest, but it's ok because changes made to
    # the volume are not written back, so it's effectively read only
    osx_ssh('[ -h /host/build ] || (mkdir -p /host && ln -s /Volumes/Untitled/build /host/build)', qemu_config['ssh'])
    osx_ssh('/python/wheelenv/bin/python /host/build/build.py %s' % args.package, qemu_config['ssh'])
    osx_scp('%s:/host/dist/%s/*.whl %s/' % (qemu_config['ssh']['userhost'], args.package, dist), qemu_config['ssh'])
    delete_cmd = btrfs_sudo + 'btrfs subvolume delete {snap}'.format(snap=work_snap).split()
    if not args.no_qemu_shutdown:
        try:
            osx_ssh('shutdown -h now', qemu_config['ssh'])
        except subprocess.CalledProcessError as exc:
            assert exc.returncode == 255
        if work_snap is not None:
            print 'Deleting snapshot:', ' '.join(delete_cmd)
            subprocess.check_call(delete_cmd)
        else:
            print 'OS X was not booted under this run, so the snapshot is unknown and cannot be deleted automatically'
    else:
        print 'QEMU shutdown not requested, skipping shutdown.'
        if work_snap is not None:
            print 'After shutdown, the snapshot for this image can be deleted with:'
            print ' '.join(delete_cmd)


def main():
    parser = argparse.ArgumentParser(description='Build wheels in Docker')
    parser.add_argument('--image', '-i', help='Build only on this Docker image')
    parser.add_argument('--no-docker', default=False, action='store_true',
            help='Skip building Linux wheels')
    parser.add_argument('--no-qemu', default=False, action='store_true',
            help='Skip building OSX wheels')
    parser.add_argument('--no-qemu-boot', default=False, action='store_true',
            help='Do not boot the QEMU guest (assume it is already running)')
    parser.add_argument('--no-qemu-shutdown', default=False, action='store_true',
            help='Do not shut down the QEMU guest')
    parser.add_argument('package', help='Package name (in wheels.yml)')
    args =  parser.parse_args()

    with open(WHEELS_YML, 'r') as handle:
        wheels = yaml.load(handle)

    try:
        package = wheels['packages'].get(args.package, None) or wheels['purepy_packages'][args.package]
    except:
        raise Exception('Not in %s: %s' % (WHEELS_YML, args.package))
    purepy = args.package in wheels['purepy_packages']

    version = str(package['version'])

    if args.image is not None:
        imageset = None
        images = [args.image]
    else:
        imageset = package.get('imageset', 'default')
        if purepy and imageset == 'default':
            images = wheels['imagesets']['purepy']
        else:
            images = wheels['imagesets'][imageset]

    src_cache = join(WHEELS_BUILD_DIR, 'cache')
    if not exists(src_cache):
        os.makedirs(src_cache)

    src_urls = package.get('src', [])

    # fetch primary sdist
    for cfile in os.listdir(src_cache):
        if cfile.startswith(args.package + '-'):
            cver = cfile[len(args.package + '-'):]
            cver = cver.replace('.tar.gz', '').replace('.tgz', '')
            if parse_version(cver) == parse_version(version):
                print 'Using cached sdist: %s' % cfile
                break
    else:
        try:
            cmd = ['pip', '--no-cache-dir', 'install', '-d', src_cache,
                    '--no-binary', ':all:', '--no-deps', args.package + '==' +
                    version]
            print 'Fetching sdist: %s' % ' '.join(cmd)
            subprocess.check_call(cmd)
        except subprocess.CalledProcessError as exc:
            if not src_urls:
                raise
            print 'Warning: Fetching sdist failed, primary source will be from `src` attribute: %s' % exc

    # fetch additional source urls
    if isinstance(src_urls, basestring):
        src_urls = [src_urls]
    for src_url in src_urls:
        tgz = join(src_cache, basename(src_url))

        if not exists(tgz):
            with open(tgz, 'w') as handle:
                r = urllib2.urlopen(src_url, None, 15)
                handle.write(r.read())

    if not args.no_docker:
        docker(images, purepy, args, version, wheels)

    if not args.no_qemu and not purepy:
        osx_qemu(args)


if __name__ == '__main__':
    main()
