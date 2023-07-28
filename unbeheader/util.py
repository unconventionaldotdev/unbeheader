import os
import re
import sys

import click
import yaml

from colorclass import Color


def cformat(string):
    """Replace %{color} and %{color,bgcolor} with ansi colors.

    Bold foreground can be achieved by suffixing the color with a '!'.
    """
    reset = Color('{/all}')
    string = string.replace('%{reset}', reset)
    string = re.sub(r'%\{(?P<fg>[a-z]+)(?P<fg_bold>!?)(?:,(?P<bg>[a-z]+))?}', _cformat_sub, string)
    if not string.endswith(reset):
        string += reset
    return Color(string)


def get_config(path, end_year):
    config = {}
    for dirname in _walk_to_root(path):
        check_path = os.path.join(dirname, 'headers.yml')
        if os.path.isfile(check_path):
            with open(check_path) as f:
                config.update((k, v) for k, v in yaml.safe_load(f.read()).items() if k not in config)
            if config.pop('root', False):
                break

    if 'start_year' not in config:
        click.echo('no valid headers.yml files found: start_year missing')
        sys.exit(1)
    if 'name' not in config:
        click.echo('no valid headers.yml files found: name missing')
        sys.exit(1)
    if 'header' not in config:
        click.echo('no valid headers.yml files found: header missing')
        sys.exit(1)
    config['end_year'] = end_year
    return config


def is_blacklisted(root, path, _cache={}):
    orig_path = path
    if path not in _cache:
        _cache[orig_path] = False
        while (path + os.path.sep).startswith(root):
            if os.path.exists(os.path.join(path, '.no-headers')):
                _cache[orig_path] = True
                break
            path = os.path.normpath(os.path.join(path, '..'))
    return _cache[orig_path]


def _cformat_sub(m):
    bg = bold = ''
    if m.group('fg_bold'):
        bold = '{b}'
    if bg_color := m.group('bg'):
        bg = '{bg%s}' % bg_color.replace('grey', 'white')
    fg = '{%s}' % m.group('fg').replace('grey', 'white')
    return Color(f'{bold}{bg}{fg}')


def _walk_to_root(path):
    """Yield directories starting from the given directory up to the root."""
    # Based on code from python-dotenv (BSD-licensed):
    # https://github.com/theskumar/python-dotenv/blob/e13d957b/src/dotenv/main.py#L245

    if os.path.isfile(path):
        path = os.path.dirname(path)

    last_dir = None
    current_dir = os.path.abspath(path)
    while last_dir != current_dir:
        yield current_dir
        parent_dir = os.path.abspath(os.path.join(current_dir, os.path.pardir))
        last_dir, current_dir = current_dir, parent_dir
