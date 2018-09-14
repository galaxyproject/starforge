"""
"""
from __future__ import absolute_import

import sys
import traceback

import click


DEBUG = False


def debug(message, *args):
    if args:
        message = message % args
    if DEBUG:
        click.echo(message, err=True)


def info(message, *args, **kwargs):
    if args:
        message = message % args
    bold = kwargs.pop('bold', True)
    fg = kwargs.pop('fg', 'green')
    err = kwargs.pop('err', True)
    click.echo(click.style(message, bold=bold, fg=fg), err=err, **kwargs)


def error(message, *args, **kwargs):
    if args:
        message = message % args
    if (DEBUG or kwargs.pop('exception', False)) and sys.exc_info()[0] is not None:
        click.echo(traceback.format_exc(), nl=False)
    click.echo(click.style(message, bold=True, fg='red'), err=True)


def warn(message, *args):
    if args:
        message = message % args
    click.echo(click.style(message, fg='red'), err=True)


def fatal(message, *args, **kwargs):
    error(message, *args, **kwargs)
    sys.exit(1)
