FIND_NAME = find . -path './.venv' -prune -o -name

.PHONY: bump clean clean-build clean-pyc clean-test coverage cov dist doc help init install lint publish sync view

.DEFAULT_GOAL := help

define BROWSER_PYSCRIPT
import os, webbrowser, sys

from urllib.request import pathname2url

webbrowser.open("file://" + pathname2url(os.path.abspath(sys.argv[1])))
endef
export BROWSER_PYSCRIPT

define PRINT_HELP_PYSCRIPT
import re, sys

for line in sys.stdin:
	match = re.match(r'^([a-zA-Z_-]+):.*?## (.*)$$', line)
	if match:
		target, help = match.groups()
		print("%-20s %s" % (target, help))
endef
export PRINT_HELP_PYSCRIPT

define UPDATE_BUILDDATE_SCRIPT
import datetime
import fileinput
import pathlib
import re
import sys

build_date = datetime.datetime.now().strftime("%Y-%m-%d")
init_file = pathlib.Path.cwd() / "src" / "fspacker" / "__init__.py"
for line in fileinput.input(init_file, inplace=True):
	if "__build_date__" in line:
		print(f'__build_date__ = "{build_date}"')  # 替换整行
	else:
		print(line, end='')  # 保持原行
print(f"Update __build_date__ -> {build_date}")
endef
export UPDATE_BUILDDATE_SCRIPT

BROWSER := python -c "$$BROWSER_PYSCRIPT"
COVERAGE := coverage
RUFF := uvx ruff
SPHINX_APIDOC := sphinx-apidoc
SPHINX_BUILD := sphinx-build
UPDATE_BUILD_DATE := python -c "$$UPDATE_BUILDDATE_SCRIPT"
WATCHMEDO := uvx --from watchdog watchmedo

bump: ## bump project version using `bump-my-version`. Example: `0.7.7` -> `0.7.8`
	$(UPDATE_BUILD_DATE)
	uvx --from bump2version bumpversion patch

bumpmi: ## bump project version using `bump-my-version`, bump minor version.
	$(UPDATE_BUILD_DATE)
	uvx --from bump2version bumpversion minor

bumpma: ## bump project version using `bump-my-version`, bump major version.
	$(UPDATE_BUILD_DATE)
	uvx --from bump2version bumpversion major

bumpb: bump publish ## bump and publish

clean: clean-build clean-pyc clean-test ## remove all build, test, coverage and Python artifacts

clean-build: ## remove build artifacts
	rm -fr build/
	rm -fr dist/
	rm -fr .eggs/

clean-pyc: ## remove Python file artifacts
	$(FIND_NAME) '*.pyc' -exec rm -f {} +
	$(FIND_NAME) '__pycache__' -exec rm -fr {} +

clean-test: ## remove test and coverage artifacts
	rm -fr .tox/
	rm -f .coverage
	rm -fr htmlcov/
	rm -fr .pytest_cache

coverage: sync ## check code coverage quickly with the default Python
	$(COVERAGE) run --source fspacker -m pytest -m "not slow" -v --tb=short --disable-warnings --maxfail=1
	$(COVERAGE) report -m
	$(COVERAGE) html
	$(BROWSER) htmlcov/index.html

cov: coverage ## check code coverage quickly with the default Python

doc: sync ## generate Sphinx HTML documentation, including API docs
	rm -f docs/fspacker.rst
	rm -f docs/modules.rst
	$(SPHINX_APIDOC) -o docs/ src/fspacker
	rm -rf docs/_build
	$(SPHINX_BUILD) docs docs/_build
	$(BROWSER) docs/_build/index.html

dist: ## builds source and wheel package
	hatch build
	ls -l dist

help:
	@python -c "$$PRINT_HELP_PYSCRIPT" < $(MAKEFILE_LIST)

init: clean sync ## initialize environment
	git init
	uvx pre-commit install

install: clean sync ## install the package to the active Python's site-packages

lint: sync ## check style with ruff
	$(RUFF) check src tests --fix

publish: dist ## publish to pypi
	uv build
	uv publish

servedoc: sync docs ## compile the docs watching for changes
	$(WATCHMEDO) shell-command -p '*.rst' -c '$(MAKE) -C docs html' -R -D .

sync: ## sync project using uv
	uv sync

test: sync ## run tests quickly with the default Python
	pytest -m "not slow" -v --tb=short --disable-warnings --maxfail=1

test-all: test## run tests on every Python version with tox
	pytest -m "slow" -v --tb=short --disable-warnings --maxfail=1

view: ## view HTML documentation, including API docs
	$(BROWSER) docs/_build/index.html
