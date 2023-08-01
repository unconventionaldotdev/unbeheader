# -- linting -------------------------------------------------------------------

.PHONY: lint
lint:
	ruff check .

# -- testing -------------------------------------------------------------------

.PHONY: headertest
headertest:
	unbeheader --ci

.PHONY: pytest
pytest:
	pytest

.PHONY: test
test: headertest pytest
