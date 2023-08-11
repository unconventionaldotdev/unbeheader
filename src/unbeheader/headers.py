# This file is part of Unbeheader.
# Copyright (C) CERN & UNCONVENTIONAL

import os
import sys
from pathlib import Path
from re import Pattern

import click

from . import SUPPORTED_FILES
from .config import get_config
from .util import cformat


def update_header(file_path: Path, year: int, ci: bool = False) -> bool:
    """Update the header of a file."""
    config = get_config(file_path, year)
    ext = file_path.suffix[1:]
    if ext not in SUPPORTED_FILES or not file_path.is_file():
        return False
    if file_path.name.startswith('.'):
        return False
    return _do_update_header(file_path, config, SUPPORTED_FILES[ext]['regex'], SUPPORTED_FILES[ext]['comments'], ci)


def _generate_header(data: dict) -> str:
    if 'start_year' not in data:
        data['start_year'] = data['end_year']
    if data['start_year'] == data['end_year']:
        data['dates'] = data['start_year']
    else:
        data['dates'] = '{} - {}'.format(data['start_year'], data['end_year'])
    template_data = {k: v for k, v in data.items() if k not in {'root', 'substring', 'template'}}
    try:
        comment = '\n'.join(line.rstrip() for line in data['template'].format(**template_data).strip().splitlines())
    except KeyError as e:
        click.secho(f'Invalid placeholder {{{e.args[0]}}} found in template', fg='red', err=True)
        sys.exit(1)
    return f'{comment}\n'


def _do_update_header(file_path: Path, config: dict, regex: Pattern[str], comments: dict, ci: bool) -> bool:
    found = False
    content = orig_content = file_path.read_text()
    # Do nothing for empty files
    if not content.strip():
        return False
    # Save the shebang line if there is one
    shebang_line = None
    if content.startswith('#!/'):
        shebang_line, content = content.split('\n', 1)
    # Find and update the header
    for match in regex.finditer(content):
        if config['substring'] in match.group():
            found = True
            match_end = content[match.end():].lstrip()
            match_end = f'\n{match_end}' if match_end else match_end
            if not content[:match.start()].strip() and not match_end.strip():
                # file is otherwise empty, we do not want a header in there
                content = ''
            else:
                content = content[:match.start()] + _generate_header(comments | config) + match_end
    # Strip leading empty characters
    content = content.lstrip()
    # Add the header if it was not found
    if not found:
        content = _generate_header(comments | config) + '\n' + content
    # Readd the shebang line if it was there
    if shebang_line:
        content = shebang_line + '\n' + content
    # Report that nothing changed
    if content == orig_content:
        return False
    # Print header update results
    if found:
        msg = 'Incorrect header in %{white!}{}' if ci else 'Updating header in %{white!}{}'
    else:
        msg = 'Missing header in %{white!}{}' if ci else 'Adding header in %{white!}{}'
    print(f'· {cformat(msg).format(os.path.relpath(file_path))}')
    # Write the updated file to disk
    if not ci:
        file_path.write_text(content)
    return True
