.PHONY: help install lint type test test-fast bench clean

help:
	@echo "install    install the package with development extras"
	@echo "lint       ruff"
	@echo "type       mypy"
	@echo "test       full test suite"
	@echo "test-fast  skip engine-dependent tests"
	@echo "bench      run the benchmark harness (requires the pinned container image)"
	@echo "clean      remove caches and TeX build artifacts"

install:
	python -m pip install -e ".[dev]"

lint:
	ruff check src tests

type:
	mypy

test:
	pytest

test-fast:
	pytest -m "not engine and not slow"

bench:
	@echo "not yet implemented -- see bench/README.md and docs/EVALUATION.md"

clean:
	find . -name '__pycache__' -type d -prune -exec rm -rf {} +
	rm -rf .pytest_cache .mypy_cache .ruff_cache
	for e in aux log toc lof lot loa out bbl blg idx ind ilg fls fdb_latexmk pdf; do \
	  find bench/corpus paper -type f -name "*.$$e" -delete 2>/dev/null || true; \
	done
