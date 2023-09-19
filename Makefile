# -- linting -------------------------------------------------------------------

.PHONY: ruff
ruff:
	ruff check .

.PHONY: unbehead
unbehead:
	unbehead --check

.PHONY: lint
lint: ruff unbehead

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
