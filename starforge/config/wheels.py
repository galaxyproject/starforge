"""
Read wheel forging config
"""
from __future__ import absolute_import

try:
    from collections import OrderedDict
except:
    from ordereddict import OrderedDict

import yaml


DEFAULT_C_IMAGESET = 'default'
DEFAULT_PUREPY_IMAGESET = 'purepy'
DEFAULT_IMAGE_TYPE = 'docker'
DEFAULT_IMAGE_PKGTOOL = 'apt'
DEFAULT_CONFIG_FILE = 'wheels.yml'
DEFAULT_PYTHONS = '/python/cp26m-{arch} /python/cp26mu-{arch} /python/cp27m-{arch} /python/cp27mu-{arch}'.split()


class WheelImage(object):
    def __init__(self, name, image):
        self.name = name
        self.type = image.get('type', DEFAULT_IMAGE_TYPE)
        self.pkgtool = image.get('pkgtool', DEFAULT_IMAGE_PKGTOOL)
        self.plat_name = image.get('plat_name', None)
        self.pythons = image.get('pythons', DEFAULT_PYTHONS)


class WheelImageset(object):
    def __init__(self, name, imageset, images):
        self.name = name
        self.images = OrderedDict()
        for image_name in imageset:
            self.images[image_name] = WheelImage(image_name, images.get(image_name, {}))


class WheelConfig(object):
    def __init__(self, name, config, imagesets, purepy=False):
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
    def open(cls, config_file):
        return cls(config_file=config_file)

    def __init__(self, config_file=None):
        self.__config_file = config_file
        self.config = None
        self.wheels = OrderedDict()
        self.imagesets = {}
        self.load_config()

    @property
    def config_file(self):
        if self.__config_file is None:
            return DEFAULT_CONFIG_FILE
        return self.__config_file

    def load_config(self):
        self.config = yaml.safe_load(open(self.config_file).read())
        for name, imageset in self.config['imagesets'].items():
            self.imagesets[name] = WheelImageset(name, imageset, self.config['images'])
        for name, wheel in self.config['packages'].items():
            self.wheels[name] = WheelConfig(name, wheel, self.imagesets, purepy=False)
        for name, wheel in self.config['purepy_packages'].items():
            self.wheels[name] = WheelConfig(name, wheel, self.imagesets, purepy=True)

    def get_wheel_config(self, name):
        return self.wheels[name]

    def get_wheel_images(self, name):
        return self.get_wheel_config(name).get_images()
