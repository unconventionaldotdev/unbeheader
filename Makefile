# -- linting -------------------------------------------------------------------

.PHONY: lint
lint:
	ruff check .

# -- testing -------------------------------------------------------------------

.PHONY: headertest
headertest:
	unbehead --ci

.PHONY: pytest
pytest:
	pytest

.PHONY: test
test: headertest pytest
