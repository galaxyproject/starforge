"""
"""
from __future__ import absolute_import

import copy
import socket
import tempfile
import uuid
from os import sep
from os.path import exists, dirname, join
from subprocess import check_call, CalledProcessError
from time import sleep
try:
    from subprocess import check_output
except ImportError:
    from ..util import check_output

from ..io import warn, info, error
from . import ExecutionContext


SSH_EXEC_TEMPLATE = '''from subprocess import Popen
Popen({cmd}).wait()
'''


class QEMUExecutionContext(ExecutionContext):
    def __init__(self, image, qemu_config=None, osk_file=None, **kwargs):
        self.image = image
        self.qemu_config = qemu_config
        self.qemu_use_sudo = qemu_config.get('qemu_use_sudo', False)
        self.btrfs_use_sudo = qemu_config.get('btrfs_use_sudo', False)
        self.osk = None
        if osk_file is not None and exists(osk_file):
            self.osk = open(osk_file).read().strip()
        self._init()

    def _init(self):
        """ Set up things that can be modified, call this to reset state
        """
        self.run_args = copy.deepcopy(self.image.run_args)
        self.ssh_config = copy.deepcopy(self.image.ssh)
        self.shares = None
        self.env = None
        self.snap = None
        self.share = None
        self.drives = []
        if 'drives' in self.image.run_args:
            self.drives = copy.deepcopy(self.image.run_args['drives'])

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

    def _ssh(self, cmd, capture_output=False, shell=False):
        """ Processes in the guest would execute in a shell if run with `ssh
        guest cmd`, so instead, we create a stub python script to run the guest
        command without a shell.
        """
        cmd = self.normalize_cmd(cmd)
        ssh_args = self.normalize_cmd(self.ssh_config.get('args', ''))
        ssh_args.extend(['-p', str(self.run_args['sshport'])])
        if shell:
            ssh_cmd = ['ssh'] + ssh_args + [self.ssh_config['userhost'], '--'] + cmd
        else:
            ssh_cmd = ['ssh'] + ssh_args + [self.ssh_config['userhost'], 'mktemp', 'starforge.XXXXXXXX']
            guest_temp = check_output(ssh_cmd).strip()
            with tempfile.NamedTemporaryFile() as local_temp:
                local_temp.write(SSH_EXEC_TEMPLATE.format(cmd=repr(cmd)))
                local_temp.flush()
                self._scp('{local} {userhost}:{guest}'.format(local=local_temp.name,
                                                              guest=guest_temp,
                                                              userhost=self.ssh_config['userhost']))
            ssh_cmd = ['ssh'] + ssh_args + [self.ssh_config['userhost'], '--', self.image.buildpy, guest_temp]
            info('%s %s executes: %s', self.image.buildpy, guest_temp, ' '.join(cmd))
        info('Executing: %s', ' '.join(ssh_cmd))
        try:
            if capture_output:
                return check_output(ssh_cmd)
            else:
                check_call(ssh_cmd)
        finally:
            if not shell:
                ssh_cmd = ['ssh'] + ssh_args + [self.ssh_config['userhost'], 'rm', '-f', guest_temp]
                try:
                    check_call(ssh_cmd)
                except CalledProcessError:
                    error('Failed to clean up guest temporary file %s', guest_temp)


    def _scp(self, cmd):
        cmd = self.normalize_cmd(cmd)
        ssh_args = self.normalize_cmd(self.ssh_config.get('args', ''))
        ssh_args.extend(['-o', 'Port=%s' % self.run_args['sshport']])
        cmd = ['scp'] + ssh_args + cmd
        info('Executing: %s', ' '.join(cmd))
        check_call(cmd)

    def start(self, share=None, env=None, **kwargs):
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
                drives.append({'file' : 'fat:rw:{host}'.format(host=host),
                               'format' : 'raw'})

        # assemble drives into device/drive args
        drive_args = []
        for i, drive in enumerate(drives):
            fmt = ''
            if 'format' in drive:
                fmt = ',format=' + drive['format']
            drive_args.append('-device')
            drive_args.append('ide-drive,bus=ide.{i},drive=drive{i}'.format(i=i))
            drive_args.append('-drive')
            drive_args.append('id=drive{i},if=none,file={f}{format}'.format(i=i,
                                                                            f=drive['file'],
                                                                            format=fmt))

        # select a random port if necessary
        if 'sshport' not in self.run_args:
            if 'port' not in self.ssh_config:
                self.ssh_config['port'] = self._random_port()
                info('Assigning random ssh port %s to QEMU guest', self.ssh_config['port'])
            self.run_args['sshport'] = self.ssh_config['port']

        # perhaps the btrfs stuff should be abstracted
        if 'bootloader' in self.run_args:
            self.run_args['bootloader'] = join(self.snap, self.run_args['bootloader'])

        # assemble start command
        run_cmd = self.image.run_cmd.format(**self.run_args)
        run_cmd = self.normalize_cmd(run_cmd)
        if self.image.insert_osk:
            assert self.osk is not None, 'Image requested insertion of OSK but OSK is unknown!'
            run_cmd.append('-device')
            run_cmd.append('isa-applesmc,osk={osk}'.format(osk=self.osk))
        run_cmd.extend(drive_args)

        # snapshot the source image for this run
        cmd = 'btrfs subvolume snapshot {src} {dest}'.format(src=join(self.image.snap_root, self.image.snap_src), dest=self.snap)
        self._execute(cmd, sudo=self.btrfs_use_sudo)

        # run QEMU
        self._execute(run_cmd, sudo=self.qemu_use_sudo)

        # wait for the guest to boot. the first call to ssh will hang until the
        # system is mostly booted. after that it may fail until it's fully up,
        # so try a few times until we can be pretty sure that it's up
        info('Waiting for SSH server response...')
        for i in range(0, 6):
            try:
                # bypass the tempfile stuff for this check
                self._ssh('/usr/bin/true', shell=True)
                info('SSH server responded')
                break
            except CalledProcessError:
                warn('SSH connection test failed, retry %s', (i + 1))
                sleep(5)

        # OS X mounts the VVFAT volumes automatically, other OS' may not, but
        # at this point we don't care about other OS'

        # symlink guest volume paths to their guest mountpoints
        if share is not None:
            for i, share_tup in enumerate(share):
                host, guest, read = share_tup
                cmd = 'mkdir -p "{guest_parent}"'.format(guest_parent=dirname(guest))
                self._ssh(cmd)
                cmd = 'ln -sf "{mount}" "{guest}"'.format(mount=self.image.vvfat_mounts[i], guest=guest)
                self._ssh(cmd)

        # SendEnv was also an option, but basically anything requires
        # modification of sshd_config, since we can't guarantee that the
        # guest's shell will read anything at startup
        if env is not None:
            with tempfile.NamedTemporaryFile() as envfile:
                for k, v in env.items():
                    envfile.write('{k}={v}')
                envfile.flush()
                self._scp('{f} {userhost}:.ssh/environment'.format(f=envfile.name,
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
        self._ssh('shutdown -h now')
        cmd = 'btrfs subvolume delete {snap}'.format(snap=self.snap)
        self._execute(cmd, sudo=self.btrfs_use_sudo)
        self._init()
