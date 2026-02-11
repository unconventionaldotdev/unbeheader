# -- dependencies --------------------------------------------------------------

.PHONY: install
install:
	uv sync --locked

# -- linting -------------------------------------------------------------------

.PHONY: mypy
mypy:
	# FIXME: Remove flag once it's possible to disable color via envvar.
	#        The uncolored output is necessary on CI for the matcher to work.
	mypy . --no-color-output

.PHONY: ruff
ruff:
	ruff check .

.PHONY: unbehead
unbehead:
	unbehead --check

.PHONY: lint
lint: ruff unbehead mypy

# -- testing -------------------------------------------------------------------

.PHONY: pytest
pytest:
	pytest

.PHONY: test
test: pytest

# -- releasing -----------------------------------------------------------------

.PHONY: tag
tag:
	bin/tag.sh
