"""
Read wheel forging config
"""
from __future__ import absolute_import

try:
    from collections import OrderedDict
except:
    from ordereddict import OrderedDict

import yaml
from six import iteritems


DEFAULT_C_IMAGESET = 'default-wheel'
DEFAULT_PUREPY_IMAGESET = 'purepy-wheel'
DEFAULT_CONFIG_FILE = 'wheels.yml'


class WheelConfig(object):
    def __init__(self, name, global_config, config, imagesets, purepy=False):
        self.name = name
        self.config = config
        self.purepy = purepy
        self.version = str(config['version'])
        self.sources = config.get('src', [])
        self.prebuild = config.get('prebuild', None)
        self.insert_setuptools = config.get('insert_setuptools', False)
        self.force_pythons = config.get('force_pythons', None)
        self.build_args = config.get('build_args', 'bdist_wheel')
        self.buildpy = config.get('buildpy', 'python')
        if not purepy:
            default_imageset = DEFAULT_C_IMAGESET
        else:
            default_imageset = DEFAULT_PUREPY_IMAGESET
        self.imageset = imagesets[config.get('imageset', default_imageset)]
        self.images = self.imageset.images

    def get_images(self):
        return self.images

    def get_image(self, name):
        return self.images[name]

    def get_dependencies(self, image):
        if image is None:
            return []
        pkgtool = self.images[image].pkgtool
        return self.config.get(pkgtool, [])


class WheelConfigManager(object):
    @classmethod
    def open(cls, global_config, config_file):
        return cls(global_config, config_file=config_file)

    def __init__(self, global_config, config_file=None):
        self.global_config = global_config
        self.__config_file = config_file
        self.config = None
        self.wheels = OrderedDict()
        self.load_config()

    @property
    def config_file(self):
        if self.__config_file is None:
            return DEFAULT_CONFIG_FILE
        return self.__config_file

    def load_config(self):
        self.config = yaml.safe_load(open(self.config_file).read())
        for (name, wheel) in iteritems(self.config['packages']):
            self.wheels[name] = WheelConfig(name, self.global_config, wheel,
                                            self.global_config.imagesets,
                                            purepy=False)
        for (name, wheel) in iteritems(self.config['purepy_packages']):
            self.wheels[name] = WheelConfig(name, self.global_config, wheel,
                                            self.global_config.imagesets,
                                            purepy=True)

    def get_wheel_config(self, name):
        return self.wheels[name]

    def get_wheel_images(self, name):
        return self.get_wheel_config(name).get_images()

    def __iter__(self):
        for name, wheel in iteritems(self.wheels):
            yield name, wheel

    def __getitem__(self, name):
        return self.wheels[name]

    def __contains__(self, name):
        return name in self.wheels
