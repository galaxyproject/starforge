"""
"""
from __future__ import absolute_import

import shlex
from abc import ABCMeta, abstractmethod
from contextlib import contextmanager


class ExecutionContext(object):
    __metaclass__ = ABCMeta

    def __init__(self, image, **kwargs):
        self.image = image

    def normalize_cmd(self, cmd):
        if isinstance(cmd, basestring):
            cmd = shlex.split(cmd)
        return cmd

    @contextmanager
    def run_context(self, **kwargs):
        self.start(**kwargs)
        yield self.run
        self.destroy()

    @abstractmethod
    def start(self, **kwargs):
        """
        """

    @abstractmethod
    def run(self, cmd):
        """
        """

    @abstractmethod
    def destroy(self):
        """
        """

