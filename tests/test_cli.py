# This file is part of Unbeheader.
# Copyright (C) CERN & UNCONVENTIONAL

import os
from datetime import date
from unittest import mock

import pytest
from click import UsageError
from click.testing import CliRunner

from unbeheader.cli import _run_on_directory
from unbeheader.cli import _run_on_file
from unbeheader.cli import _run_on_repo
from unbeheader.cli import main


@mock.patch('unbeheader.cli._run_on_directory')
def test_main_for_directory(_run_on_directory, tmp_path):
    runner = CliRunner()
    runner.invoke(main, ['--path', tmp_path])
    _run_on_directory.assert_called_once()


@mock.patch('unbeheader.cli._run_on_file')
def test_main_for_file(_run_on_file, tmp_path):
    file_path = tmp_path / 'manuscript.py'
    file_path.touch()
    runner = CliRunner()
    runner.invoke(main, ['--path', file_path])
    _run_on_file.assert_called_once()


@mock.patch('unbeheader.cli._run_on_repo')
def test_main_for_repo(_run_on_repo):
    runner = CliRunner()
    runner.invoke(main)
    _run_on_repo.assert_called_once()


@mock.patch('unbeheader.cli._run_on_file')
def test_main_for_ci_error(_run_on_file, tmp_path):
    _run_on_file.return_value = True
    file_path = tmp_path / 'manuscript.py'
    file_path.touch()
    runner = CliRunner()
    result = runner.invoke(main, ['--ci', '--path', file_path])
    assert result.exit_code == 1


@mock.patch('unbeheader.cli.update_header')
@pytest.mark.parametrize('updated', (True, False))
def test_run_on_file(update_header, updated, tmp_path):
    update_header.return_value = updated
    file_path = tmp_path / 'manuscript.py'
    error = _run_on_file(file_path, date.today().year, False)
    assert error == updated


@mock.patch('unbeheader.cli.is_excluded')
@mock.patch('unbeheader.cli.update_header')
@pytest.mark.parametrize('updated', (True, False))
def test_run_on_directory(update_header, is_excluded, updated, tmp_path):
    update_header.return_value = updated
    is_excluded.return_value = False
    sub_path = tmp_path / 'secrets'
    sub_path.mkdir()
    file_paths = (
        tmp_path / 'manuscript_a.py',
        tmp_path / 'manuscript_b.py',
        sub_path / 'manuscript_c.py'
    )
    for path in file_paths:
        path.touch()
    error = _run_on_directory(tmp_path, date.today().year, False)
    assert is_excluded.call_count == 3
    assert update_header.call_count == 3
    assert error == updated


@mock.patch('subprocess.check_output')
@mock.patch('unbeheader.cli.is_excluded')
@mock.patch('unbeheader.cli.update_header')
@pytest.mark.parametrize('updated', (True, False))
def test_run_on_repo(update_header, is_excluded, check_output, updated):
    check_output.side_effect = [
        '/path/to/somewhere.py\n/path/to/elsewhere.py\n',  # git ls-files
        '',                                                # git ls-files --others --exclude-standard
        ''                                                 # git ls-files --deleted
    ]
    update_header.return_value = updated
    is_excluded.return_value = False
    error = _run_on_repo(date.today().year, False)
    assert error == updated
    assert is_excluded.call_count == 2
    assert update_header.call_count == 2


@mock.patch('subprocess.check_output')
@mock.patch('unbeheader.cli.is_excluded')
@mock.patch('unbeheader.cli.update_header')
def test_run_on_repo_for_deleted_files(update_header, is_excluded, check_output):
    check_output.side_effect = [
        '/path/to/deleted.py',  # git ls-files
        '',                     # git ls-files --others --exclude-standard
        '/path/to/deleted.py'   # git ls-files --deleted
    ]
    is_excluded.return_value = False
    _run_on_repo(date.today().year, False)
    update_header.assert_not_called()


@mock.patch('subprocess.check_output')
@mock.patch('unbeheader.cli.is_excluded')
@mock.patch('unbeheader.cli.update_header')
def test_run_on_repo_for_untracked_files(update_header, is_excluded, check_output):
    check_output.side_effect = [
        '',                 # git ls-files
        '/path/to/new.py',  # git ls-files --others --exclude-standard
        ''                  # git ls-files --deleted
    ]
    is_excluded.return_value = False
    _run_on_repo(date.today().year, False)
    update_header.assert_called_once()


def test_run_on_repo_for_non_repo(tmp_path):
    os.chdir(tmp_path)
    with pytest.raises(UsageError):
        _run_on_repo(date.today().year, False)
