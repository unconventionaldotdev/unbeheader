# This file is part of Unbeheader.
# Copyright (C) CERN & UNCONVENTIONAL

from dataclasses import asdict
from datetime import date
from textwrap import dedent
from unittest import mock

import pytest
from colorclass import Color

from unbeheader import SUPPORTED_FILE_TYPES
from unbeheader.config import DEFAULT_SUBSTRING
from unbeheader.headers import _do_update_header
from unbeheader.headers import _generate_header
from unbeheader.headers import _print_results
from unbeheader.headers import update_header

COLOR_RESET = Color('{/all}')


@pytest.fixture
def config():
    return {
        'owner': 'Ordo Templi Orientis',
        'start_year': 1904,
        'end_year': 1904,
        'substring': DEFAULT_SUBSTRING,
        'template': dedent('''
            {comment_start} This file is part of Thelema.
            {comment_middle} Copyright (C) {dates} {owner}
            {comment_end}
        ''').lstrip()
    }


@pytest.fixture
def create_py_file(tmp_path):
    def create_py_file(file_content):
        file_path = tmp_path / 'manuscript.py'
        file_path.write_text(file_content)
        return file_path

    return create_py_file


@pytest.fixture
def py_files_settings():
    return {
        'regex': SUPPORTED_FILE_TYPES['py'].regex,
        'comments': SUPPORTED_FILE_TYPES['py'].comments
    }


@mock.patch('unbeheader.headers.get_config')
@mock.patch('unbeheader.headers._do_update_header')
def test_update_header(_do_update_header, get_config, create_py_file):
    config = {'owner': 'Ordo Templi Orientis'}
    get_config.return_value = config
    year = date.today().year
    check = True
    file_path = create_py_file('')
    file_ext = file_path.suffix[1:]
    update_header(file_path, year, check)
    _do_update_header.assert_called_once_with(
        file_path, config, SUPPORTED_FILE_TYPES[file_ext].regex, SUPPORTED_FILE_TYPES[file_ext].comments, check
    )


@mock.patch('unbeheader.headers.get_config')
@mock.patch('unbeheader.headers._do_update_header')
def test_update_header_for_non_existent_file(_do_update_header, get_config, tmp_path):
    year = date.today().year
    file_path = tmp_path / 'manuscript.py'
    assert update_header(file_path, year) is False
    assert _do_update_header.call_count == 0


@mock.patch('unbeheader.headers.get_config')
@mock.patch('unbeheader.headers._do_update_header')
def test_update_header_for_unsupported_file(_do_update_header, get_config, tmp_path):
    year = date.today().year
    file_path = tmp_path / 'manuscript.txt'
    file_path.touch()
    assert 'txt' not in SUPPORTED_FILE_TYPES
    assert update_header(file_path, year) is False
    assert _do_update_header.call_count == 0


@mock.patch('unbeheader.headers.get_config')
@mock.patch('unbeheader.headers._do_update_header')
def test_update_header_for_current_dir(_do_update_header, get_config, tmp_path):
    year = date.today().year
    file_path = tmp_path / '.'
    assert update_header(file_path, year) is False
    assert _do_update_header.call_count == 0


@mock.patch('unbeheader.headers._print_results')
@pytest.mark.parametrize(('before_content', 'after_content'), (
    # Test that files with only header are kept empty
    ('''
        # This file is part of Thelema.
        # Copyright (C) 1904 Ordo Templi Orientis
    ''',
    '''
    '''),
    # Test that partial header is updated with the full header
    ('''
        # This file is part of Thelema.
        print('Beware of the knowledge you will gain.')
    ''',
    '''
        # This file is part of Thelema.
        # Copyright (C) 1904 Ordo Templi Orientis

        print('Beware of the knowledge you will gain.')
    '''),
    # Test that multiple newlines are removed in one go
    ('''

        # This file is part of Thelema.
        # Copyright (C) 1904 Ordo Templi Orientis

        print('Beware of the knowledge you will gain.')
    ''',
    '''
        # This file is part of Thelema.
        # Copyright (C) 1904 Ordo Templi Orientis

        print('Beware of the knowledge you will gain.')
    '''),
    # Test that outdated header is updated with the correct year
    ('''
        # This file is part of Thelema.
        # Copyright (C) 1486 Ordo Templi Orientis

        print('Beware of the knowledge you will gain.')
    ''',
    '''
        # This file is part of Thelema.
        # Copyright (C) 1904 Ordo Templi Orientis

        print('Beware of the knowledge you will gain.')
    '''),
    # Test that there's no newline after shebang
    ('''
        #!/usr/bin/env python

        # This file is part of Thelema.
        # Copyright (C) 1904 Ordo Templi Orientis

        print('Beware of the knowledge you will gain.')
    ''',
    '''
        #!/usr/bin/env python
        # This file is part of Thelema.
        # Copyright (C) 1904 Ordo Templi Orientis

        print('Beware of the knowledge you will gain.')
    '''),
    # Test that multiple newlines are removed in one go with shebang
    ('''
        #!/usr/bin/env python


        # This file is part of Thelema.
        # Copyright (C) 1904 Ordo Templi Orientis

        print('Beware of the knowledge you will gain.')
    ''',
    '''
        #!/usr/bin/env python
        # This file is part of Thelema.
        # Copyright (C) 1904 Ordo Templi Orientis

        print('Beware of the knowledge you will gain.')
    '''),
))
def test_do_update_header(_print_results, before_content, after_content, config, create_py_file, py_files_settings):
    content = dedent(before_content)[1:] # Remove indentation and leading newline
    file_path = create_py_file(content)
    result = _do_update_header(file_path, config, check=False, **py_files_settings)
    assert result is True
    assert file_path.read_text() == dedent(after_content).lstrip()
    _print_results.assert_called_once_with(file_path, found=True, check=False)


@mock.patch('unbeheader.headers._print_results')
@pytest.mark.parametrize(('before_content', 'after_content'), (
    # Test that header is added in file missing it
    ('''
        print('Beware of the knowledge you will gain.')
     ''',
     '''
        # This file is part of Thelema.
        # Copyright (C) 1904 Ordo Templi Orientis

        print('Beware of the knowledge you will gain.')
     '''),
    # Test that header is added after shebang
    ('''
        #!/usr/bin/env python

        print('Beware of the knowledge you will gain.')
    ''',
    '''
        #!/usr/bin/env python
        # This file is part of Thelema.
        # Copyright (C) 1904 Ordo Templi Orientis

        print('Beware of the knowledge you will gain.')
    '''),
))
def test_do_update_header_for_not_found(_print_results, before_content, after_content, config,
                                        create_py_file, py_files_settings):
    content = dedent(before_content)[1:] # Remove indentation and leading newline
    file_path = create_py_file(content)
    result = _do_update_header(file_path, config, check=False, **py_files_settings)
    assert result is True
    assert file_path.read_text() == dedent(after_content).lstrip()
    _print_results.assert_called_once_with(file_path, found=False, check=False)


def test_do_update_header_for_no_changes(config, create_py_file, py_files_settings):
    file_content = dedent('''
        # This file is part of Thelema.
        # Copyright (C) 1904 Ordo Templi Orientis

        print('Beware of the knowledge you will gain.')
    ''').lstrip()
    file_path = create_py_file(file_content)
    result = _do_update_header(file_path, config, check=False, **py_files_settings)
    assert result is False


@mock.patch('unbeheader.headers._print_results')
@pytest.mark.parametrize(('file_content', 'header_found'), (
    ('''
        # This file is part of Thelema.
        print('Beware of the knowledge you will gain.')
    ''', True),
    ('''
        print('Beware of the knowledge you will gain.')
    ''', False),
))
def test_do_update_header_for_check(_print_results, file_content, header_found, config,
                                    create_py_file, py_files_settings):
    file_content = dedent(file_content).lstrip()
    file_path = create_py_file(file_content)
    result = _do_update_header(file_path, config, check=True, **py_files_settings)
    assert result is True
    assert open(file_path).read() == file_content
    _print_results.assert_called_once_with(file_path, found=header_found, check=True)


def test_do_update_header_for_empty_file(create_py_file, py_files_settings):
    file_path = create_py_file('')
    result = _do_update_header(file_path, {}, check=False, **py_files_settings)
    assert result is False


@pytest.mark.parametrize(('extension', 'expected'), (
    ('py', '''
        # This file is part of Thelema.
        # Copyright (C) 1904 Ordo Templi Orientis
    '''),
    ('wsgi', '''
        # This file is part of Thelema.
        # Copyright (C) 1904 Ordo Templi Orientis
    '''),
    ('js', '''
        // This file is part of Thelema.
        // Copyright (C) 1904 Ordo Templi Orientis
    '''),
    ('jsx', '''
        // This file is part of Thelema.
        // Copyright (C) 1904 Ordo Templi Orientis
    '''),
    ('css', '''
        /* This file is part of Thelema.
         * Copyright (C) 1904 Ordo Templi Orientis
         */
    '''),
    ('scss', '''
        // This file is part of Thelema.
        // Copyright (C) 1904 Ordo Templi Orientis
    '''),
    ('sh', '''
        # This file is part of Thelema.
        # Copyright (C) 1904 Ordo Templi Orientis
    '''),
))
def test_generate_header(extension, expected, config):
    data = asdict(SUPPORTED_FILE_TYPES[extension].comments) | config
    header = _generate_header(data)
    assert header == dedent(expected).lstrip()


def test_generate_header_for_different_end_year(config):
    end_year = date.today().year
    config['end_year'] = end_year
    data = asdict(SUPPORTED_FILE_TYPES['py'].comments) | config
    header = _generate_header(data)
    assert header == dedent(f'''
        # This file is part of Thelema.
        # Copyright (C) 1904 - {end_year} Ordo Templi Orientis
    '''.format(end_year)).lstrip()


@pytest.mark.parametrize('template', (
    '{root}', '{template}', '{substring}'
))
def test_generate_header_for_invalid_placeholder(template, config):
    data = asdict(SUPPORTED_FILE_TYPES['py'].comments) | config
    data['template'] = template
    with pytest.raises(SystemExit) as exc:
        _generate_header(data)
    assert exc.value.code == 1


@pytest.mark.parametrize(('found', 'check', 'expected'), (
    (True, True, 'Incorrect header'),
    (True, False, 'Updating header'),
    (False, True, 'Missing header'),
    (False, False, 'Adding header'),
))
def test_print_results(found, check, expected, monkeypatch, tmp_path, capsys):
    monkeypatch.delenv('CI', raising=False)
    _print_results(tmp_path, found, check)
    captured = capsys.readouterr()
    assert expected in captured.out
    assert COLOR_RESET in captured.out

@pytest.mark.parametrize(('envvar'), (
    ('1'), ('true'),
))
def test_print_results_for_ci(envvar, monkeypatch, tmp_path, capsys):
    monkeypatch.setenv('CI', envvar)
    _print_results(tmp_path, True, True)
    captured = capsys.readouterr()
    assert COLOR_RESET not in captured.out
