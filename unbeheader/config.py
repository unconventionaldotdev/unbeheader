import os
import sys
from collections.abc import Iterator

import click
import yaml

# The substring which must be part of a comment block in order for the comment to be updated by the header
DEFAULT_SUBSTRING = 'This file is part of'

# The name of the files containing header configuration
CONFIG_FILE_NAME = '.header.yaml'


def get_config(path: str, end_year: int) -> dict:
    """Get configuration from headers files."""
    config = _load_config(path)
    _validate_config(config)
    config['substring'] = config.get('substring', DEFAULT_SUBSTRING)
    config['end_year'] = end_year
    return config


def _load_config(path: str) -> dict:
    config = {}
    found = False
    for dirname in _walk_to_root(path):
        check_path = os.path.join(dirname, CONFIG_FILE_NAME)
        if os.path.isfile(check_path):
            found = True
            with open(check_path) as f:
                config.update((k, v) for k, v in yaml.safe_load(f.read()).items() if k not in config)
            if config.pop('root', False):
                break
    if not found:
        click.secho(f'No {CONFIG_FILE_NAME} file found', fg='red', err=True)
        sys.exit(1)
    return config


def _validate_config(config: dict):
    valid_keys = {'owner', 'start_year', 'substring', 'header'}
    mandatory_keys = {'owner', 'header'}
    config_keys = set(config)
    invalid_keys = config_keys - valid_keys
    missing_keys = mandatory_keys - config_keys
    if invalid_keys:
        click.secho(f'Invalid key found in {CONFIG_FILE_NAME} files: {list(invalid_keys)[0]}', fg='red', err=True)
        sys.exit(1)
    if missing_keys:
        click.secho(f'No valid {CONFIG_FILE_NAME} files found: {list(missing_keys)[0]} is missing', fg='red', err=True)
        sys.exit(1)


def _walk_to_root(path: str) -> Iterator[str]:
    """Yield directories starting from the given directory up to the root."""
    # Based on code from python-dotenv (BSD-licensed):
    # https://github.com/theskumar/python-dotenv/blob/3ffcef60/src/dotenv/main.py#L252

    if not os.path.exists(path):
        raise OSError('Starting path not found')

    if os.path.isfile(path):
        path = os.path.dirname(path)

    last_dir = None
    current_dir = os.path.abspath(path)
    while last_dir != current_dir:
        yield current_dir
        parent_dir = os.path.abspath(os.path.join(current_dir, os.path.pardir))
        last_dir, current_dir = current_dir, parent_dir
