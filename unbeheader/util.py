import os
import re

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
