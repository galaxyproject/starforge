"""
"""
from __future__ import absolute_import

from subprocess import check_call
try:
    from subprocess import check_output
except ImportError:
    from ..util import check_output

from six import iteritems

from ..io import info
from . import ExecutionContext


class DockerExecutionContext(ExecutionContext):
    def __init__(self, image, docker_config=None, **kwargs):
        self.image = image
        self.docker_config = docker_config
        self.use_sudo = docker_config.get('use_sudo', False)
        self.share_args = []
        self.env = {}

    def start(self, share=None, env=None, **kwargs):
        if share is not None:
            for host, guest, read in share:
                self.share_args.append(
                    '--volume={host}:{guest}:{read}'.format(host=host,
                                                            guest=guest,
                                                            read=read))
        if env is not None:
            self.env = env

    def run(self, cmd, capture_output=False, **kwargs):
        cmd = self.normalize_cmd(cmd)
        run_cmd = 'docker run --rm'.split()
        run_cmd.extend(self.share_args)
        for (k, v) in iteritems(self.env):
            run_cmd.append('--env={k}={v}'.format(k=k, v=v))
        run_cmd.append(self.image.name)
        run_cmd.extend(cmd)
        if self.use_sudo:
            run_cmd = ['sudo'] + run_cmd
        info('Running docker: %s', ' '.join(run_cmd))
        if capture_output:
            return check_output(run_cmd)
        else:
            check_call(run_cmd)

    def destroy(self, **kwargs):
        self.share_args = []
