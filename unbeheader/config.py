# This file is part of Unbeheader.
# Copyright (C) CERN & UNCONVENTIONAL

import sys
from collections.abc import Iterator
from pathlib import Path

import click
import yaml

# The substring which must be part of a comment block in order for the comment to be updated by the header
DEFAULT_SUBSTRING = 'This file is part of'

# The name of the files containing header configuration
CONFIG_FILE_NAME = '.header.yaml'


def get_config(path: Path, end_year: int) -> dict:
    """Get configuration from headers files."""
    config = _load_config(path)
    _validate_config(config)
    config['substring'] = config.get('substring', DEFAULT_SUBSTRING)
    config['end_year'] = end_year
    return config


def _load_config(path: Path) -> dict:
    config = {}
    found = False
    for dir_path in _walk_to_root(path):
        check_path = dir_path / CONFIG_FILE_NAME
        if check_path.is_file():
            found = True
            config.update((k, v) for k, v in yaml.safe_load(check_path.read_text()).items() if k not in config)
            if config.pop('root', False):
                break
    if not found:
        click.secho(f'No {CONFIG_FILE_NAME} file found', fg='red', err=True)
        sys.exit(1)
    return config


def _validate_config(config: dict):
    valid_keys = {'owner', 'start_year', 'substring', 'template'}
    mandatory_keys = {'owner', 'template'}
    config_keys = set(config)
    invalid_keys = config_keys - valid_keys
    missing_keys = mandatory_keys - config_keys
    if invalid_keys:
        click.secho(f'Invalid key found in {CONFIG_FILE_NAME} files: {list(invalid_keys)[0]}', fg='red', err=True)
        sys.exit(1)
    if missing_keys:
        click.secho(f'No valid {CONFIG_FILE_NAME} files found: {list(missing_keys)[0]} is missing', fg='red', err=True)
        sys.exit(1)


def _walk_to_root(path: Path) -> Iterator[Path]:
    """Yield directories starting from the given directory up to the root."""
    if not path.exists():
        raise OSError('Starting path not found')
    if path.is_file():
        path = path.parent
    yield path
    yield from path.parents
