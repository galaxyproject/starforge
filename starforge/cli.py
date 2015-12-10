""" Command line interface
"""
from __future__ import absolute_import

import click

import sys
from os import listdir
from os.path import abspath, dirname, join

from . import io
from .util import xdg_config_file
from .config import ConfigManager


CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'],
                        auto_envvar_prefix="STARFORGE")

cmd_folder = abspath(join(dirname(__file__), 'commands'))


class Context(object):
    def __init__(self):
        self.config_file = None
        self.__config = None

    @property
    def config(self):
        if self.__config is None:
            self.__config = ConfigManager(self.config_file)
        return self.__config


pass_context = click.make_pass_decorator(Context, ensure=True)


def set_debug(debug_opt):
    if debug_opt:
        io.DEBUG = True


def list_cmds():
    rv = []
    for filename in listdir(cmd_folder):
        if filename.endswith('.py') and \
           filename.startswith('cmd_'):
            rv.append(filename[len("cmd_"):-len(".py")])
    rv.sort()
    return rv


def name_to_command(name):
    try:
        if sys.version_info[0] == 2:
            name = name.encode('ascii', 'replace')
        mod_name = 'starforge.commands.cmd_' + name
        mod = __import__(mod_name, None, None, ['cli'])
    except ImportError as e:
        io.error("Problem loading command %s, exception %s" % (name, e))
        return
    return mod.cli


class StarforgeCLI(click.MultiCommand):
    def list_commands(self, ctx):
        return list_cmds()

    def get_command(self, ctx, name):
        return name_to_command(name)


@click.command(cls=StarforgeCLI, context_settings=CONTEXT_SETTINGS)
@click.option('-d', '--debug',
              is_flag=True,
              help='Enable debug mode.')
@click.option('-c', '--config-file',
              default=xdg_config_file(),
              type=click.Path(dir_okay=False,
                              resolve_path=True),
              help='Path to Starforge config.yml '
                   '(default: %s).' % xdg_config_file())
@pass_context
def starforge(ctx, debug, config_file):
    """ Build Galaxy things under virtualization
    """
    set_debug(debug)
    ctx.config_file = config_file
