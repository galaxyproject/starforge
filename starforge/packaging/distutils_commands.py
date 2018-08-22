""" Informational commands for working with distutils Distributions.
"""
from __future__ import absolute_import, print_function

import json
from functools import partial

import yaml
from setuptools import Command

#from wheel.bdist_wheel import bdist_wheel

OUTPUT_TEMPLATE = """Distribution: {distribution}
Implementation: {implementation}
ABI: {abi}
Platform: {platform}
Tag: {tag}
Pure Python: {purepy}
Universal: {universal}
"""


class wheel_info(Command):

    description = 'output wheel info'

    user_options = [('yaml', None,
                     "output YAML"
                     " (default: false)"),
                    ('json', None,
                     "output JSON"
                     " (default: false)"),
                    ('pretty', None,
                     "pretty output"
                     " (default: false)"),
                   ]

    boolean_options = ['yaml', 'json', 'pretty']

    def initialize_options(self):
        self.yaml = False
        self.json = False
        self.pretty = False
        self.dump = None
        self.end = ''

    def finalize_options(self):
        if self.yaml:
            if self.pretty:
                self.dump = partial(
                    yaml.safe_dump,
                    default_flow_style=False,
                    indent=4)
            else:
                self.dump = yaml.safe_dump
        elif self.json:
            if self.pretty:
                self.dump = partial(
                    json.dumps,
                    sort_keys=True,
                    indent=4,
                    separators=(',', ': '))
                self.end = '\n'
            else:
                self.dump = json.dumps
        else:
            self.dump = dump_human

    def run(self):
        bdist_wheel = self.get_finalized_command('bdist_wheel')
        #bdist_wheel.finalize_options()
        tag = bdist_wheel.get_tag()
        info = {
            'distribution': bdist_wheel.wheel_dist_name,
            'purepy': bdist_wheel.root_is_pure,
            'universal': bdist_wheel.universal,
            'tag': {
                'implementation': tag[0],
                'abi': tag[1],
                'platform': tag[2],
                'str': '-'.join(tag),
            },
        }
        print(self.dump(info), end=self.end)


def dump_human(info):
    return OUTPUT_TEMPLATE.format(
        distribution=info['distribution'],
        implementation=info['tag']['implementation'],
        abi=info['tag']['abi'],
        platform=info['tag']['platform'],
        purepy='Yes' if info['purepy'] else 'No',
        universal='Yes' if info['universal'] else 'No',
        tag=info['tag']['str']
    )
