# -- linting -------------------------------------------------------------------

.PHONY: lint
lint:
	ruff check .

# -- testing -------------------------------------------------------------------

.PHONY: headertest
headertest:
	unbehead --check

.PHONY: pytest
pytest:
	pytest

.PHONY: test
test: headertest pytest

# -- releasing -----------------------------------------------------------------

.PHONY: tag
tag:
	bin/tag.sh
