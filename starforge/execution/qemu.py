"""
"""
from __future__ import absolute_import

import copy
import socket
import tempfile
import uuid
from os import sep
from os.path import exists, join
from subprocess import check_call, CalledProcessError, Popen
from time import sleep
try:
    from subprocess import check_output
except ImportError:
    from ..util import check_output

from six import iteritems, b

from ..io import warn, info, error
from . import ExecutionContext


SSH_EXEC_TEMPLATE = '''from subprocess import Popen
Popen({cmd}).wait()
'''

CREATE_SYMLINK_TEMPLATE = '''from os import listdir, symlink, makedirs, unlink
from os.path import join, exists, dirname
mount_base = {mount_base}
mapping = dict()
for name in listdir(mount_base):
    sf_mount = join(mount_base, name, '.starforge.mount')
    if exists(sf_mount):
        mapping[open(sf_mount).read().strip()] = join(mount_base, name)
for guest in {guests}:
    assert guest in mapping, 'Volume for %s not found in %s!' % (guest,
                                                                 mount_base)
    if not exists(dirname(guest)):
        makedirs(dirname(guest))
    if exists(guest):
        unlink(guest)
    symlink(mapping[guest], guest)
'''


class QEMUExecutionContext(ExecutionContext):
    def __init__(self, image, qemu_config=None, osk_file=None, qemu_port=None,
                 **kwargs):
        self.image = image
        self.qemu_config = qemu_config
        self.qemu_use_sudo = qemu_config.get('qemu_use_sudo', False)
        self.btrfs_use_sudo = qemu_config.get('btrfs_use_sudo', False)
        self.qemu_port = qemu_port
        self.start_stop_image = qemu_port is None
        self.osk = None
        if osk_file is not None and exists(osk_file):
            self.osk = open(osk_file).read().strip()
        self._init()

    def _init(self):
        """ Set up things that can be modified, call this to reset state
        """
        self.run_args = copy.deepcopy(self.image.run_args)
        self.ssh_config = copy.deepcopy(self.image.ssh)
        self.ssh_args = []
        self.shares = None
        self.env = None
        self.snap = None
        self.share = None
        self.drives = []
        self.qemu_proc = None
        if 'drives' in self.image.run_args:
            self.drives = copy.deepcopy(self.image.run_args['drives'])
        if self.qemu_port is not None:
            self.run_args['sshport'] = self.qemu_port

        # set up ssh args
        self.ssh_args = self.normalize_cmd(self.ssh_config.get('args', ''))
        if self.qemu_port is not None:
            port = self.qemu_port
            self.run_args['sshport'] = self.qemu_port
        elif 'sshport' in self.run_args:
            port = self.run_args['sshport']
        else:
            port = None
        if port is not None:
            self.ssh_args.extend(['-o', 'Port=%s' % port])
        if 'keyfile' in self.ssh_config:
            self.ssh_args.extend(['-o',
                                  'IdentityFile=%s'
                                  % self.ssh_config['keyfile']])

    def _random_port(self):
        """Select a random port for ssh forwarding. There's a race condition
        because the random port could be reassigned prior to its use by QEMU,
        but this is basically the best we can do. If it becomes a problem,
        implement retrying.
        """
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind(('127.0.0.1', 0))
        port = sock.getsockname()[1]
        sock.close()
        return port

    def _execute(self, cmd, sudo=False):
        cmd = self.normalize_cmd(cmd)
        if sudo:
            cmd = ['sudo'] + cmd
        check_call(cmd)

    def _ssh(self, cmd, capture_output=False, template=SSH_EXEC_TEMPLATE,
             args=None):
        """ Processes in the guest would execute in a shell if run with `ssh
        guest cmd`, so instead, we create a stub python script to run the guest
        command without a shell.
        """
        if args is None:
            args = {}
        cmd = self.normalize_cmd(cmd)
        if template is None:
            ssh_cmd = (['ssh']
                       + self.ssh_args
                       + [self.ssh_config['userhost'], '--']
                       + cmd)
        else:
            args['cmd'] = cmd
            for (k, v) in iteritems(args):
                args[k] = repr(v)
            ssh_cmd = (['ssh']
                       + self.ssh_args
                       + [self.ssh_config['userhost'],
                          'mktemp', 'starforge.XXXXXXXX'])
            guest_temp = check_output(ssh_cmd).decode('ascii').strip()
            with tempfile.NamedTemporaryFile() as local_temp:
                template = template.format(**args)
                local_temp.write(b(template))
                local_temp.flush()
                self._scp('{local} {userhost}:{guest}'
                          .format(local=local_temp.name,
                                  guest=guest_temp,
                                  userhost=self.ssh_config['userhost']))
            ssh_cmd = (['ssh']
                       + self.ssh_args
                       + [self.ssh_config['userhost'],
                          '--', self.image.buildpy, guest_temp])
            if cmd:
                info('%s %s executes: %s',
                     self.image.buildpy, guest_temp, self.stringify_cmd(cmd))
            else:
                info('%s %s executes with args: %s',
                     self.image.buildpy, guest_temp, str(args))
        info('Executing: %s', self.stringify_cmd(ssh_cmd))
        try:
            if capture_output:
                return check_output(ssh_cmd)
            else:
                check_call(ssh_cmd)
        finally:
            if template is not None:
                ssh_cmd = (['ssh']
                           + self.ssh_args
                           + [self.ssh_config['userhost'],
                              'rm', '-f', guest_temp])
                try:
                    check_call(ssh_cmd)
                except CalledProcessError:
                    error('Failed to clean up guest temporary file %s',
                          guest_temp)

    def _scp(self, cmd):
        cmd = self.normalize_cmd(cmd)
        cmd = ['scp'] + self.ssh_args + cmd
        info('Executing: %s', self.stringify_cmd(cmd))
        check_call(cmd)

    def start(self, share=None, env=None, **kwargs):
        # if a port was provided on the command line, we assume the image is
        # already running
        if not self.start_stop_image:
            return

        # path to snapshot
        self.snap = join(self.image.snap_root, '@' + str(uuid.uuid1()))
        drives = []
        for drive in self.drives:
            if not drive['file'].startswith(sep):
                drive['file'] = join(self.snap, drive['file'])
            drives.append(drive)

        # convert shares to drives
        if share is not None:
            self.share = share
            for host, guest, read in share:
                # OS X can't mount the VVFAT volume if it's ro, but (at least
                # on OS X) updates to the VVFAT volume in the guest are not
                # reflected on the host anyway
                drives.append({'file': 'fat:rw:{host}'.format(host=host),
                               'format': 'raw'})
                # OS X does not mount the volumes in any reliable order, so use
                # this to determine the "mount" point later.
                with open(join(host, '.starforge.mount'), 'w') as fh:
                    fh.write(guest)

        # assemble drives into device/drive args
        drive_args = []
        for i, drive in enumerate(drives):
            fmt = ''
            if 'format' in drive:
                fmt = ',format=' + drive['format']
            drive_args.append('-device')
            drive_args.append('ide-drive,bus=ide.{i},drive=drive{i}'
                              .format(i=i))
            drive_args.append('-drive')
            drive_args.append('id=drive{i},if=none,file={f}{format}'
                              .format(i=i,
                                      f=drive['file'],
                                      format=fmt))

        # set up ssh args
        # select a random port if necessary
        if 'sshport' not in self.run_args:
            port = self.ssh_config.get('port', None)
            if port is None:
                port = self._random_port()
                info('Assigning random ssh port %s to QEMU guest', port)
            self.run_args['sshport'] = port
            self.ssh_args.extend(['-o', 'Port=%s' % self.run_args['sshport']])

        # perhaps the btrfs stuff should be abstracted
        if 'bootloader' in self.run_args:
            self.run_args['bootloader'] = join(self.snap,
                                               self.run_args['bootloader'])

        # assemble start command
        run_cmd = self.image.run_cmd.format(**self.run_args)
        run_cmd = self.normalize_cmd(run_cmd)
        run_cmd.extend(drive_args)
        display_cmd = copy.copy(run_cmd)
        if self.image.insert_osk:
            assert self.osk is not None, \
                'Image requested insertion of OSK but OSK is unknown!'
            run_cmd.append('-device')
            run_cmd.append('isa-applesmc,osk={osk}'.format(osk=self.osk))
            display_cmd.extend(['-device', 'isa-applesmc,osk=redacted'])
        info('Running qemu-system: %s', self.stringify_cmd(display_cmd))

        # snapshot the source image for this run
        cmd = ('btrfs subvolume snapshot {src} {dest}'
               .format(src=join(self.image.snap_root, self.image.snap_src),
                       dest=self.snap))
        self._execute(cmd, sudo=self.btrfs_use_sudo)

        # run QEMU
        if self.qemu_use_sudo:
            run_cmd = ['sudo'] + run_cmd
        self.qemu_proc = Popen(run_cmd)
        info('QEMU started in pid %s', self.qemu_proc.pid)

        # wait for the guest to boot. the first call to ssh will hang until the
        # system is mostly booted. after that it may fail until it's fully up,
        # so try a few times until we can be pretty sure that it's up
        info('Waiting for SSH server response...')
        for i in range(0, 6):
            try:
                # bypass the tempfile stuff for this check
                self._ssh('/usr/bin/true', template=None)
                info('SSH server responded')
                break
            except CalledProcessError:
                warn('SSH connection test failed, retry %s', (i + 1))
                sleep(5)
        else:
            raise Exception('Connection to guest SSH server failed')

        # OS X mounts the VVFAT volumes automatically, other OS' may not, but
        # at this point we don't care about other OS'

        # symlink guest volume paths to their guest mountpoints
        if share is not None:
            args = {'mount_base': self.image.vvfat_mount_base,
                    'guests': [t[1] for t in share]}
            # this can also fail (guest may not have mounted the vvfat volumes
            # yet), so try it a few times
            info('Linking guest volumes to expected mount points')
            for i in range(0, 6):
                try:
                    self._ssh(None, template=CREATE_SYMLINK_TEMPLATE,
                              args=args)
                    break
                except CalledProcessError:
                    warn('Linking failed, retry %s', (i + 1))
                    sleep(5)

        # SendEnv was also an option, but basically anything requires
        # modification of sshd_config, since we can't guarantee that the
        # guest's shell will read anything at startup
        if env is not None:
            with tempfile.NamedTemporaryFile() as envfile:
                for (k, v) in iteritems(env):
                    envfile.write(b('{k}={v}'.format(k=k, v=v)))
                envfile.flush()
                self._scp('{f} {userhost}:.ssh/environment'
                          .format(f=envfile.name,
                                  userhost=self.ssh_config['userhost']))

    def run(self, cmd, capture_output=False, **kwargs):
        cmd = self.normalize_cmd(cmd)
        return self._ssh(cmd, capture_output=capture_output)

    def destroy(self, **kwargs):
        if self.share is not None:
            for host, guest, read in self.share:
                if read != 'rw':
                    continue
                # FIXME: this breaks what we are claiming to do, which is
                # pretend that {guest} and {host} are a single FS. The problem
                # is that OS X fills {guest} with a bunch of garbage that we
                # don't want. So for the moment, just copy back *.whl, which is
                # the only thing we wanted.
                self._scp('{userhost}:{guest}/*.whl {host}'.format(
                    userhost=self.ssh_config['userhost'],
                    guest=guest,
                    host=host))
        if self.start_stop_image:
            try:
                self._ssh('shutdown -h now', template=None)
            except CalledProcessError as exc:
                assert exc.returncode == 255
            if self.qemu_proc is not None:
                info('Waiting for QEMU guest shutdown...')
                self.qemu_proc.wait()
                # TODO: if necessary, use poll() and kill() if it doesn't die
            cmd = 'btrfs subvolume delete {snap}'.format(snap=self.snap)
            self._execute(cmd, sudo=self.btrfs_use_sudo)
            self._init()
