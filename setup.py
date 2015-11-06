#!/usr/bin/env python
# -*- coding: utf-8 -*-


from os.path import join
from setuptools import setup, find_packages


#with open('README.rst') as file:
#    long_description = file.read()
#
#long_description += '\n\n'
#with open('HISTORY.rst') as file:
#    long_description += file.read()

execfile(join('starforge', '__init__.py'))

setup(
    name = 'starforge',
    version = __version__,
    packages = find_packages(),
    description = 'Build Galaxy things in virtualized environments',
    #long_description = long_description,
    url = 'https://github.com/galaxyproject/starforge',
    author = 'The Galaxy Community',
    author_email = 'galaxy-dev@lists.galaxyproject.org',
    license = 'MIT',
    keywords = 'starforge galaxy docker qemu',
    package_data = {'': [
        'config/default.yml',
    ]},
    install_requires = [
        'click',
        'requests'
    ],
    entry_points = {
        'console_scripts': [
            'starforge = starforge.cli:starforge'
        ]
    },
    classifiers = [
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: POSIX',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3'
    ],
    zip_safe = False
)
