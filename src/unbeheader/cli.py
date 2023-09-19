# This file is part of Unbeheader.
# Copyright (C) CERN & UNCONVENTIONAL

import subprocess
import sys
from datetime import date
from pathlib import Path

import click
from click import UsageError

from . import SUPPORTED_FILE_TYPES
from .headers import update_header
from .util import cformat
from .util import is_excluded

USAGE = '''
Updates all the headers in the supported files ({supported_file_types}).
By default, all the files tracked by git in the current repository are updated
to the current year.

You can specify a year to update to as well as a file or directory.
This will update all the supported files in the scope including those not tracked
by git. If the directory does not contain any supported files (or if the file
specified is not supported) nothing will be updated.
'''.format(supported_file_types=', '.join(SUPPORTED_FILE_TYPES)).strip()


@click.command(help=USAGE)
@click.option('--check', is_flag=True, help='Indicate that the script is running in check mode and should use a '
                                            'non-zero exit code unless all headers were already up to date. This also '
                                            'prevents files from actually being updated.')
@click.option('--year', '-y', type=click.IntRange(min=1000), default=date.today().year, metavar='YEAR',
              help='Indicate the target year')
@click.option('--path', '-p', 'path_str', type=click.Path(exists=True),
              help='Restrict updates to a specific file or directory')
def main(check: bool, year: int, path_str: str) -> None:
    path = Path(path_str).resolve() if path_str else None
    if path and path.is_dir():
        error = _run_on_directory(path, year, check)
    elif path and path.is_file():
        error = _run_on_file(path, year, check)
    else:
        error = _run_on_repo(year, check)
    if not error:
        click.secho('✅ All headers are up to date', fg='green')
    elif check:
        click.secho('❌ Some headers need to be added or updated', fg='red')
        sys.exit(1)
    else:
        click.secho('🔄 Some headers have been updated', fg='yellow')


def _run_on_directory(path: Path, year: int, check: bool) -> bool:
    error = False
    if not check:
        print(cformat('Updating headers to the year %{yellow!}{year}%{reset} for all the files in '
                      '%{yellow!}{path}%{reset}...').format(year=year, path=path))
    root_path = path
    for path in root_path.glob('**/*'):
        if path.is_dir():
            continue
        if not is_excluded(path, root_path):
            if update_header(path, year, check):
                error = True
    return error

def _run_on_file(path: Path, year: int, check: bool) -> bool:
    error = False
    if not check:
        print(cformat('Updating headers to the year %{yellow!}{year}%{reset} for the file '
                      '%{yellow!}{file}%{reset}...').format(year=year, file=path))
    if update_header(path, year, check):
        error = True
    return error


def _run_on_repo(year: int, check: bool) -> bool:
    error = False
    if not check:
        print(cformat('Updating headers to the year %{yellow!}{year}%{reset} for all '
                      'git-tracked files...').format(year=year))
    try:
        cmd = ('git', 'ls-files')
        untracked_flags = ('--others', '--exclude-standard')
        deleted_flags = ('--deleted',)
        # Get all files tracked by git
        git_file_paths = set(subprocess.check_output(cmd, text=True).splitlines())
        # Include untracked files
        git_file_paths |= set(subprocess.check_output(cmd + untracked_flags, text=True).splitlines())
        # Exclude deleted files
        git_file_paths -= set(subprocess.check_output(cmd + deleted_flags, text=True).splitlines())
        for file_path_str in git_file_paths:
            file_path = Path(file_path_str).absolute()
            if not is_excluded(file_path.parent, Path.cwd()):
                if update_header(file_path, year, check):
                    error = True
    except subprocess.CalledProcessError as e:
        msg = click.style('You must be within a git repository to run this script.', fg='red', bold=True)
        raise UsageError(msg) from e
    return error


if __name__ == '__main__':
    main()
