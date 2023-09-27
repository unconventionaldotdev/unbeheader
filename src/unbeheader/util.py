# This file is part of Unbeheader.
# Copyright (C) CERN & UNCONVENTIONAL

from __future__ import annotations

import re
from pathlib import Path
from re import Match

from colorclass import Color

from .typing import PathCache

# The name of the files that exclude the directory from header updates
EXCLUDE_FILE_NAME = '.no-header'


def cformat(string: str) -> Color:
    """Replace %{color} and %{color,bgcolor} with ANSI colors.

    Bold foreground can be achieved by suffixing the color with a '!'.
    """
    def repl(m: Match[str]) -> Color:
        bg = bold = ''
        if m.group('fg_bold'):
            bold = '{b}'
        if bg_color := m.group('bg'):
            bg = '{bg%s}' % bg_color.replace('grey', 'white')
        fg = '{%s}' % m.group('fg').replace('grey', 'white')
        return Color(f'{bold}{bg}{fg}')

    reset = Color('{/all}')
    string = string.replace('%{reset}', reset)
    string = re.sub(r'%\{(?P<fg>[a-z]+)(?P<fg_bold>!?)(?:,(?P<bg>[a-z]+))?}', repl, string)
    if not string.endswith(reset):
        string += reset
    return Color(string)


def is_excluded(path: Path, root_path: Path | None = None, cache: PathCache | None = None) -> bool:
    """"Whether the path is excluded by a .no-headers file.

    The .no-headers file is searched for in the path and all parents up to the root.

    :param path: The path to check.
    :param root_path: The root path to check up to.
    :param cache: A cache of paths that have been checked.
    """
    root_path = root_path if root_path else path
    cache = cache if cache else {}
    orig_path = path
    if path not in cache:
        cache[orig_path] = False
        while str(path).startswith(str(root_path)):
            if (path / EXCLUDE_FILE_NAME).exists():
                cache[orig_path] = True
                break
            path = path.parent
    return cache[orig_path]
