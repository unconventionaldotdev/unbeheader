import os
from datetime import date
from unittest import mock

import pytest
import yaml

from unbeheader.config import CONFIG_FILE_NAME
from unbeheader.config import DEFAULT_SUBSTRING
from unbeheader.config import _load_config
from unbeheader.config import _validate_config
from unbeheader.config import _walk_to_root
from unbeheader.config import get_config


@pytest.fixture
def create_headers_file():
    def create_headers_file(data, dir_path):
        file_path = os.path.join(dir_path, CONFIG_FILE_NAME)
        with open(file_path, 'w') as yaml_file:
            yaml.dump(data, yaml_file)

    return create_headers_file


@mock.patch('unbeheader.config._load_config')
@mock.patch('unbeheader.config._validate_config')
def test_get_config(_validate_config, _load_config, tmp_path):
    end_year = date.today().year
    _load_config.return_value = {}
    config = get_config(tmp_path, end_year)
    assert _load_config.call_count == 1
    assert _validate_config.call_count == 1
    assert config['end_year'] == end_year


@mock.patch('unbeheader.config._load_config')
@mock.patch('unbeheader.config._validate_config')
def test_get_config_for_default_substring(_validate_config, _load_config, tmp_path):
    end_year = date.today().year
    _load_config.return_value = {}
    config = get_config(tmp_path, end_year)
    assert config['substring'] == DEFAULT_SUBSTRING
    _load_config.return_value = {'substring': ''}
    config = get_config(tmp_path, end_year)
    assert config['substring'] != DEFAULT_SUBSTRING


def test_load_config(create_headers_file, tmp_path):
    data_top = {'owner': 'Ordo Templi Orientis', 'start_year': 1904}
    create_headers_file(data_top, tmp_path)
    config = _load_config(tmp_path)
    assert config == data_top


def test_load_config_for_multiple_files(create_headers_file, tmp_path):
    data_top = {'owner': 'Ordo Templi Orientis', 'start_year': 1904}
    data_bottom = {'start_year': 1486}
    nested_dir_path = tmp_path / 'nested'
    nested_dir_path.mkdir()
    create_headers_file(data_top, tmp_path)
    create_headers_file(data_bottom, nested_dir_path)
    config = _load_config(nested_dir_path)
    assert config == {**data_top, **data_bottom}
    assert config['start_year'] == data_bottom['start_year']


def test_load_config_for_stop_on_root(create_headers_file, tmp_path):
    data_top = {'owner': 'Ordo Templi Orientis', 'start_year': 1904}
    data_bottom = {'root': True}
    nested_dir_path = tmp_path / 'nested'
    nested_dir_path.mkdir()
    create_headers_file(data_top, tmp_path)
    create_headers_file(data_bottom, nested_dir_path)
    config = _load_config(nested_dir_path)
    assert config == {}


def test_load_config_for_file_not_found(tmp_path):
    with pytest.raises(SystemExit) as exc:
        _load_config(tmp_path)
    assert exc.value.code == 1


def test_validate_config():
    config = {
        'owner': 'Ordo Templi Orientis',
        'start_year': 1904,
        'header': ''
    }
    _validate_config(config)


def test_validate_config_for_invalid_keys():
    invalid_config = {'Country': 'Germany'}
    with pytest.raises(SystemExit) as exc:
        _validate_config(invalid_config)
    assert exc.value.code == 1


def test_validate_config_for_missing_keys():
    incomplete_config = {}
    with pytest.raises(SystemExit) as exc:
        _validate_config(incomplete_config)
    assert exc.value.code == 1


def test_walk_to_root_for_non_existent_path():
    with pytest.raises(OSError):
        list(_walk_to_root('/path/to/nowhere'))


def test_walk_to_root_for_file_path(tmp_path):
    file_path = tmp_path / 'manuscript.py'
    file_path.touch()
    assert list(_walk_to_root(file_path)) == [str(p) for p in file_path.parents]


def test_walk_to_root_for_directory(tmp_path):
    assert list(_walk_to_root(tmp_path)) == [str(tmp_path)] + [str(p) for p in tmp_path.parents]


def test_walk_to_root_for_root_directory():
    root_dir = '/'
    expected_dirs = [root_dir]
    assert list(_walk_to_root(root_dir)) == expected_dirs
