"""
"""
from __future__ import absolute_import

from os import unlink
from subprocess import (
    check_call,
    check_output
)

from six import iteritems

from . import ExecutionContext
from ..io import info
from ..util import stringify_cmd


class DockerExecutionContext(ExecutionContext):
    def __init__(self, image, docker_config=None, **kwargs):
        self.image = image
        self.docker_config = docker_config
        self.use_sudo = docker_config.get('use_sudo', False)
        self.share_args = []
        self.env = {}
        self.container_ids = []
        self.image_ids = []

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
        image = self.image.image
        if self.container_ids:
            image = ':'.join([image.split(':')[0], self.container_ids[-1]])
            check_call(['docker', 'commit', self.container_ids[-1], image])
            self.image_ids.append(image)
        cmd = self.normalize_cmd(cmd)
        run_cmd = 'docker run --cidfile __cid.txt'.split()
        run_cmd.extend(self.share_args)
        for (k, v) in iteritems(self.env):
            run_cmd.append('--env={k}={v}'.format(k=k, v=v))
        run_cmd.append(image)
        run_cmd.extend(cmd)
        if self.use_sudo:
            run_cmd = ['sudo'] + run_cmd
        info('Running docker: %s', stringify_cmd(run_cmd))
        output = None
        if capture_output:
            output = check_output(run_cmd)
        else:
            check_call(run_cmd)
        self.container_ids.append(open('__cid.txt').read().strip())
        unlink('__cid.txt')
        return output

    def destroy(self, **kwargs):
        for i in self.container_ids:
            check_call(['docker', 'rm', '-v', i])
        for i in self.image_ids:
            check_call(['docker', 'rmi', i])
        self.share_args = []
        self.container_ids = []
        self.image_ids = []
