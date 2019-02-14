"""
"""
from __future__ import absolute_import

from subprocess import (
    check_call,
    check_output
)

from . import ExecutionContext
from ..io import info
from ..util import stringify_cmd


class LocalExecutionContext(ExecutionContext):
    def __init__(self, image, **kwargs):
        self.image = image

    def start(self, **kwargs):
        pass

    def run(self, cmd, cwd=None, capture_output=False, **kwargs):
        cmd = self.normalize_cmd(cmd)
        info('Running local: %s', stringify_cmd(cmd))
        if capture_output:
            return check_output(cmd, cwd=cwd)
        else:
            check_call(cmd, cwd=cwd)

    def destroy(self, **kwargs):
        pass
