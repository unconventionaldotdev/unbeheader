# This file is part of Unbeheader.
# Copyright (C) CERN & UNCONVENTIONAL

import subprocess
import sys
from datetime import date
from pathlib import Path

import click
from click import UsageError

from . import SUPPORTED_FILES
from .headers import update_header
from .util import cformat
from .util import is_excluded

USAGE = '''
Updates all the headers in the supported files ({supported_files}).
By default, all the files tracked by git in the current repository are updated
to the current year.

You can specify a year to update to as well as a file or directory.
This will update all the supported files in the scope including those not tracked
by git. If the directory does not contain any supported files (or if the file
specified is not supported) nothing will be updated.
'''.format(supported_files=', '.join(SUPPORTED_FILES)).strip()


@click.command(help=USAGE)
@click.option('--ci', is_flag=True, help='Indicate that the script is running during CI and should use a non-zero '
                                         'exit code unless all headers were already up to date. This also prevents '
                                         'files from actually being updated.')
@click.option('--year', '-y', type=click.IntRange(min=1000), default=date.today().year, metavar='YEAR',
              help='Indicate the target year')
@click.option('--path', '-p', type=click.Path(exists=True), help='Restrict updates to a specific file or directory')
def main(ci: bool, year: int, path: str):
    path = Path(path).resolve() if path else None
    if path and path.is_dir():
        error = _run_on_directory(path, year, ci)
    elif path and path.is_file():
        error = _run_on_file(path, year, ci)
    else:
        error = _run_on_repo(year, ci)
    if not error:
        click.secho('\u2705 All headers are up to date', fg='green')
    elif ci:
        click.secho('\u274C Some headers need to be updated or added', fg='red')
        sys.exit(1)
    else:
        click.secho('\U0001F504 Some headers have been updated (or are missing)', fg='yellow')


def _run_on_directory(path: Path, year: int, ci: bool) -> bool:
    error = False
    if not ci:
        print(cformat('Updating headers to the year %{yellow!}{year}%{reset} for all the files in '
                      '%{yellow!}{path}%{reset}...').format(year=year, path=path))
    root_path = path
    for path in root_path.glob('**/*'):
        if path.is_dir():
            continue
        if not is_excluded(path, root_path):
            if update_header(path, year, ci):
                error = True
    return error

def _run_on_file(path: Path, year: int, ci: bool) -> bool:
    error = False
    if not ci:
        print(cformat('Updating headers to the year %{yellow!}{year}%{reset} for the file '
                      '%{yellow!}{file}%{reset}...').format(year=year, file=path))
    if update_header(path, year, ci):
        error = True
    return error


def _run_on_repo(year: int, ci: bool) -> bool:
    error = False
    if not ci:
        print(cformat('Updating headers to the year %{yellow!}{year}%{reset} for all '
                      'git-tracked files...').format(year=year))
    try:
        for file_path in subprocess.check_output(['git', 'ls-files'], text=True).splitlines():
            file_path = Path(file_path).absolute()
            if not is_excluded(file_path.parent, Path.cwd()):
                if update_header(file_path, year, ci):
                    error = True
    except subprocess.CalledProcessError as e:
        msg = click.style('You must be within a git repository to run this script.', fg='red', bold=True)
        raise UsageError(msg) from e
    return error


if __name__ == '__main__':
    main()
