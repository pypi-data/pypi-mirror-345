.DEFAULT_GOAL := all

# Ensure cargo output is colored in terminals
export CARGO_TERM_COLOR=$(shell (test -t 0 && echo "always") || echo "auto")

# Only define maturin usage if in a virtualenv
USE_MATURIN = $(shell [ "$$VIRTUAL_ENV" != "" ] && (which maturin))

.PHONY: .uv  ## Check that uv is installed
.uv:
	@uv -V || echo 'Please install uv: https://docs.astral.sh/uv/getting-started/installation/'

.PHONY: .pre-commit  ## Check that pre-commit is installed
.pre-commit:
	@pre-commit -V || echo 'Please install pre-commit: https://pre-commit.com/'

.PHONY: install
install: .uv .pre-commit
	uv pip install -U wheel
	uv sync --frozen --active --group all
	uv pip install -v -e .
	pre-commit install

.PHONY: rebuild-lockfiles  ## Rebuild lockfiles from scratch, updating all dependencies
rebuild-lockfiles: .uv
	uv lock --upgrade

.PHONY: build-dev
build-dev:
	@rm -f python/datalint_core/*.so
	uv run maturin develop --uv

.PHONY: format
format:
	uv run ruff check --fix $(sources)
	uv run ruff format $(sources)
	cargo fmt

.PHONY: lint-python
lint-python:
	uv run ruff check $(sources)
	uv run ruff format --check $(sources)
	uv run griffe dump -f -d google -LWARNING -o/dev/null python/pydantic_core
	$(mypy-stubtest)

.PHONY: lint-rust
lint-rust:
	cargo fmt --version
	cargo fmt --all -- --check
	cargo clippy --version
	cargo clippy --tests -- -D warnings

.PHONY: pyright
pyright:
	uv run pyright

.PHONY: test
test:
	uv run pytest

.PHONY: clean
clean:
	rm -rf target
	rm -rf **/__pycache__
	rm -rf *.egg-info
	rm -rf .pytest_cache
	rm -rf python/datalint_core/*.so

.PHONY: all
all: format build-dev lint test
