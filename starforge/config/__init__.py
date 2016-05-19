from __future__ import absolute_import

import errno
from os.path import join, abspath, expanduser, dirname
try:
    from collections import OrderedDict
except:
    from ordereddict import OrderedDict

import yaml
from six import iteritems

from ..util import dict_merge, xdg_data_dir


DEFAULT_CONFIG_FILE = abspath(join(dirname(__file__), 'default.yml'))
DEFAULT_IMAGE_TYPE = 'docker'
DEFAULT_IMAGE_PKGTOOL = 'apt'
DEFAULT_IMAGE_PYTHONS = [
    '/python/cp26m-{arch}/bin/python',
    '/python/cp26mu-{arch}/bin/python',
    '/python/cp27m-{arch}/bin/python',
    '/python/cp27mu-{arch}/bin/python'
]


class Image(object):
    def __init__(self, name, image):
        self.name = name
        self.type = image.get('type', DEFAULT_IMAGE_TYPE)
        self.pkgtool = image.get('pkgtool', DEFAULT_IMAGE_PKGTOOL)
        self.plat_name = image.get('plat_name', None)
        self.force_plat = image.get('force_plat', True)
        self.buildpy = image.get('buildpy', 'python')
        self.pythons = image.get('pythons', DEFAULT_IMAGE_PYTHONS)
        self.run_cmd = image.get('run_cmd', None)
        self.run_args = image.get('run_args', {})
        self.postbuild = image.get('postbuild', None)
        self.insert_osk = image.get('insert_osk', False)
        self.snap_root = image.get('snap_root', None)
        self.snap_src = image.get('snap_src', None)
        self.ssh = image.get('ssh', {})
        self.vvfat_mount_base = image.get('vvfat_mount_base', None)
        if 'host' not in self.ssh:
            self.ssh['host'] = 'localhost'
        self.ssh['userhost'] = self.ssh['host']
        if 'user' in self.ssh:
            self.ssh['userhost'] = self.ssh['user'] + '@' + self.ssh['host']


class Imageset(object):
    def __init__(self, name, imageset, images):
        self.name = name
        self.images = OrderedDict()
        for image_name in imageset:
            self.images[image_name] = Image(image_name,
                                            images.get(image_name, {}))


class ConfigManager(object):
    @classmethod
    def open(cls, config_file):
        return cls(config_file=config_file)

    def __init__(self, config_file=None):
        self.config_file = config_file
        self.cache_path = xdg_data_dir()
        self.docker = {}
        self.qemu = {}
        self.imagesets = {}
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

        if 'imagesets' in config:
            for (name, imageset) in iteritems(config['imagesets']):
                self.imagesets[name] = Imageset(name, imageset,
                                                config.get('images', {}))

        self.config = config

    def dump_config(self):
        return self.config
