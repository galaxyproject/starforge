"""
"""
from __future__ import absolute_import

import shlex
from abc import ABCMeta, abstractmethod
from contextlib import contextmanager
try:
    from shlex import quote
except ImportError:
    from pipes import quote

from six import with_metaclass, string_types


class ExecutionContext(with_metaclass(ABCMeta, object)):
    def __init__(self, image, **kwargs):
        self.image = image

    def normalize_cmd(self, cmd):
        if isinstance(cmd, string_types):
            cmd = shlex.split(cmd)
        return cmd

    def stringify_cmd(self, cmd):
        if isinstance(cmd, string_types):
            return cmd
        r = ''
        for e in cmd:
            r += quote(e) + ' '
        return r.strip()

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
