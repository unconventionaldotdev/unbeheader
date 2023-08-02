# The Unbeheader 🪡😵

> Never fail to maintain your file headers.

Unbeheader is a CLI tool to keep file headers up-to-date and to check that they remain so. The Unbeheader allows you to define file header templates in `.header.yaml` configuration files and then apply them to all the files in the project. Unbeheader knows how to update headers in [different file types](https://github.com/unconventionaldotdev/unbeheader/blob/master/unbeheader/__init__.py), including Python, JavaScript and CSS files.

A header template will be rendered like this in Python files:

```python
# This file is part of Thelema.
# Copyright (C) 1904 - 1947 Ordo Templi Orientis
```

Like this in JavaScript files:

```js
// This file is part of Thelema.
// Copyright (C) 1904 - 1947 Ordo Templi Orientis
```

And like this in CSS files:

```css
/* This file is part of Thelema.
 * Copyright (C) 1904 - 1947 Ordo Templi Orientis
 */
```

## Getting started

### Installation

Unbeheader is available on PyPI as [`unbeheader`](https://pypi.org/project/unbeheader/) and can be installed with `pip`:

```sh
pip install unbeheader
```

### Usage

It's possible to run Unbeheader in two modes: `fix` and `check`. The `fix` mode will update all files in the project with the correct header. The `check` mode will check that all files in the project have the correct header and exit with a non-zero status code if any file is missing or has an incorrect header.

> **NOTE:** Neither `fix` or `check` modes will work unless Unbeheader can find a `.header.yaml` configuration file. Read more on the [Configuration](#configuration) section.

To run Unbeheader in `fix` mode simply run the `unbeheader` command:

```sh
unbeheader                            # Update all the files in the Git repository
unbeheader --path .                   # Update all the files under the current directory
unbeheader --path /path/to/directory  # Update all the files under a directory
unbeheader --path /path/to/file.py    # Update a single file
```

By default, Unbeheader will pass the current year to generate the `{dates}` placeholder in the header template. To pass a different year, use the `--year` flag:

```sh
unbeheader --year 1947
```

To run Unbeheader in `check` mode, use the `--ci` flag:

```sh
unbehader --ci
```

## Configuration

Unbeheader reads its configuration from `.header.yaml` files placed in the file tree of the project. It is possible to override configuration values by placing `.header.yaml` files in subdirectories. This is useful when different headers are needed for different parts of the project. It is also possible to exclude a directory by placing an empty `.no-header` file in it.

Here is an example of a project structure with various `.header.yaml` and `.no-header` files:

```
./
├── artifacts/
│  └── .no-header   # This directory will be ignored
├── thelema/
│  └── .header.yaml  # This overrides the default configuration
└── .header.yaml     # This is the default configuration
```

<!-- ### The `.header.yaml` file -->

This `.header.yaml` file contains the header template, template values to interpolate and other settings for Unbeheader. The following is an example of a `.header.yaml` file:

```yaml
root: true
start_year: 1904
owner: Ordo Templi Orientis
substring: This file is part of
template: |-
  {comment_start} This file is part of Thelema.
  {comment_middle} Copyright (C) {dates} {owner}
  {comment_end}
```

Setting value keys:
- `root`: When set to `true`, it will stop Unbeheader from looking for `.header.yaml` files in parent directories. It defaults to `false`.
- `substring`: The substring that Unbeheader will look for to determine if a file has a header or not. If the substring is not found, Unbeheader will assume that the file has no header. It defaults to `This file is part of`.

Template value keys:
- `owner`: The owner of the project, used to generate the `{owner}` placeholder. This key is required.
- `start_year`: The start year of the header, used to generate the `{dates}` placeholder. It defaults to the year passed to the `unbeheader` command.

Finally, the `template` key is a multi-line string that will be used to generate the header template. The template accepts the interpolation of certain placeholders. These are:

- `{comment_start}`: The comment start string for the file type (e.g. `#` for Python files).
- `{comment_middle}`: The comment middle string for the file type (e.g. ` *` for CSS files).
- `{comment_end}`: The comment end string for the file type (e.g. ` */` for CSS files).
- `{dates}`: The start and end years of the header (e.g. `1904 - 1947`).
- `{owner}`: The owner of the project (e.g. `Ordo Templi Orientis`).

## Development

In order to develop Unbeheader, you will need to install the project and its dependencies in a virtualenv. This guide assumes that you have the following tools installed and available in your path:

- [`git`](https://git-scm.com/) (available in most systems)
- [`make`](https://www.gnu.org/software/make/) (available in most systems)
- [`poetry`](https://python-poetry.org/) ([installation guide](https://python-poetry.org/docs/#installation))
- [`pyenv`](https://github.com/pyenv/pyenv) ([installation guide](https://github.com/pyenv/pyenv#installation))

First, clone [the repository](https://github.com/unconventionaldotdev/unbeheader) locally with:

```shell
git clone https://github.com/unconventionaldotdev/unbeheader
cd unbeheader
```

Before creating the virtualenv, you probably want to be using the same version of Python that the development of the project is targeting. This is the version specified in the `.python-version` file and you can install it with `pyenv`:

```sh
pyenv install
```

You may now create the virtualenv and install the project with its dependencies in it with `poetry`:

```sh
poetry install
```

Once installed, you can invoke the `unbeheader` command with:

```sh
poetry run -- unbeheader
```

For convenience, you may want to spawn a shell within the virtualenv with:

```sh
poetry shell
unbeheader
```

### Contributing

This project uses GitHub Actions to run the tests and linter on every pull request to the `master` and `devel` branches. You are still encouraged to run the tests and linter locally before pushing your changes.

Tests can be run with:

```sh
poetry run -- make test
```

Linter can be run with:

```sh
poetry run -- make lint
```
