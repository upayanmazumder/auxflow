.PHONY: help install lint format format-check type test test-fast plan-validate bench clean pre-commit

help:
	@echo "install       install the package with development extras"
	@echo "lint          ruff check"
	@echo "format        ruff format (writes changes)"
	@echo "format-check  ruff format --check (CI mode, no writes)"
	@echo "type          mypy"
	@echo "test          full test suite"
	@echo "test-fast     skip engine-dependent tests"
	@echo "plan-validate score bench/plan/implementation-plan.yaml (deterministic)"
	@echo "bench         run the benchmark harness (requires the pinned container image)"
	@echo "pre-commit    install the pre-commit hooks"
	@echo "clean         remove caches and TeX build artifacts"

install:
	python -m pip install -e ".[dev]"

lint:
	ruff check src tests bench/plan

format:
	ruff format src tests bench/plan

format-check:
	ruff format --check src tests bench/plan

type:
	mypy

test:
	pytest

test-fast:
	pytest -m "not engine and not slow"

plan-validate:
	bash autoresearch.sh

bench:
	@echo "not yet implemented -- see bench/README.md and docs/EVALUATION.md"

pre-commit:
	pip install pre-commit
	pre-commit install

clean:
	find . -name '__pycache__' -type d -prune -exec rm -rf {} +
	rm -rf .pytest_cache .mypy_cache .ruff_cache
	for e in aux log toc lof lot loa out bbl blg idx ind ilg fls fdb_latexmk pdf; do \
	  find bench/corpus paper -type f -name "*.$$e" -delete 2>/dev/null || true; \
	done
