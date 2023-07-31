import os
import subprocess
import sys
from datetime import date

import click

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
@click.pass_context
def main(ctx, ci, year, path):
    error = False
    if path and os.path.isdir(path):
        if not ci:
            print(cformat('Updating headers to the year %{yellow!}{year}%{reset} for all the files in '
                          '%{yellow!}{path}%{reset}...').format(year=year, path=path))
        for root, _, filenames in os.walk(path):
            for filename in filenames:
                if not is_excluded(root, path):
                    if update_header(os.path.join(root, filename), year, ci):
                        error = True
    elif path and os.path.isfile(path):
        if not ci:
            print(cformat('Updating headers to the year %{yellow!}{year}%{reset} for the file '
                          '%{yellow!}{file}%{reset}...').format(year=year, file=path))
        if update_header(path, year, ci):
            error = True
    else:
        if not ci:
            print(cformat('Updating headers to the year %{yellow!}{year}%{reset} for all '
                          'git-tracked files...').format(year=year))
        try:
            for filepath in subprocess.check_output(['git', 'ls-files'], text=True).splitlines():
                filepath = os.path.abspath(filepath)
                if not is_excluded(os.path.dirname(filepath), os.getcwd()):
                    if update_header(filepath, year, ci):
                        error = True
        except subprocess.CalledProcessError:
            raise click.UsageError(
                click.style('You must be within a git repository to run this script.', fg='red', bold=True))

    if not error:
        click.secho('\u2705 All headers are up to date', fg='green')
    elif ci:
        click.secho('\u274C Some headers need to be updated or added', fg='red')
        sys.exit(1)
    else:
        click.secho('\U0001F504 Some headers have been updated (or are missing)', fg='yellow')


if __name__ == '__main__':
    main()
