"""
"""
from __future__ import absolute_import

import subprocess

from ..io import warn, info
from . import ExecutionContext


class LocalExecutionContext(ExecutionContext):
    def __init__(self, image, **kwargs):
        self.image = image

    def start(self, **kwargs):
        pass

    def run(self, cmd, cwd=None, **kwargs):
        cmd = self.normalize_cmd(cmd)
        info('Running local: %s', ' '.join(cmd))
        return subprocess.check_output(cmd, cwd=cwd)

    def destroy(self, **kwargs):
        pass
