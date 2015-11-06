from __future__ import absolute_import

import errno
import os
from os.path import join, abspath, expanduser, dirname

import yaml

from ..util import dict_merge, xdg_data_dir


DEFAULT_CONFIG_FILE = abspath(join(dirname(__file__), 'default.yml'))


class ConfigManager(object):
    @classmethod
    def open(cls, config_file):
        return cls(config_file=config_file)

    def __init__(self, config_file=None):
        self.config_file = config_file
        self.cache_path = xdg_data_dir()
        self.docker = {}
        self.qemu = {}
        self.load_config()

    def load_config(self):
        config = yaml.safe_load(open(DEFAULT_CONFIG_FILE).read())
        try:
            user_config = yaml.safe_load(open(self.config_file).read())
        except (OSError, IOError) as exc:
            if exc.errno == errno.ENOENT:
                user_config = {}
            else:
                raise

        dict_merge(config, user_config)

        if 'docker' in config:
            self.docker = config['docker']

        if 'qemu' in config:
            self.qemu = config['qemu']

        if 'cache_path' in config:
            self.cache_path = abspath(expanduser(config['cache_path']))

        self.config = config
