"""
"""
from __future__ import absolute_import

import shlex
from abc import ABCMeta, abstractmethod
from contextlib import contextmanager

from six import (
    string_types,
    with_metaclass
)


class ExecutionContext(with_metaclass(ABCMeta, object)):
    def __init__(self, image, **kwargs):
        self.image = image

    def normalize_cmd(self, cmd):
        if isinstance(cmd, string_types):
            cmd = shlex.split(cmd)
        return cmd

    @contextmanager
    def run_context(self, **kwargs):
        self.start(**kwargs)
        try:
            yield self.run
        finally:
            self.destroy()

    @abstractmethod
    def start(self, **kwargs):
        """
        """

    @abstractmethod
    def run(self, cmd, **kwargs):
        """
        """

    @abstractmethod
    def destroy(self, **kwargs):
        """
        """
