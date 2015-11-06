"""
"""
from __future__ import absolute_import

import subprocess

from ..io import warn, info
from . import ExecutionContext


class DockerExecutionContext(ExecutionContext):
    def __init__(self, image, docker_config=None, **kwargs):
        self.image = image
        self.docker_config = docker_config
        self.use_sudo = docker_config.get('use_sudo', False)
        self.share_args = []

    def start(self, share=None, **kwargs):
        if share is not None:
            for host, guest in share:
                self.share_args.append('--volume={host}:{guest}'.format(host=host, guest=guest))

    def run(self, cmd, **kwargs):
        cmd = self.normalize_cmd(cmd)
        run_cmd = 'docker run --rm'.split()
        run_cmd.extend(self.share_args)
        run_cmd.append(self.image)
        run_cmd.extend(cmd)
        if self.use_sudo:
            run_cmd = ['sudo'] + run_cmd
        info('Running docker: %s', ' '.join(run_cmd))
        return subprocess.check_output(run_cmd)

    def destroy(self, **kwargs):
        self.share_args = []
