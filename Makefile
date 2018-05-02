.PHONY: clean clean-test clean-pyc clean-build docs help
.DEFAULT_GOAL := help

define BROWSER_PYSCRIPT
import os, webbrowser, sys

try:
	from urllib import pathname2url
except:
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

BROWSER := python -c "$$BROWSER_PYSCRIPT"

help:
	@python -c "$$PRINT_HELP_PYSCRIPT" < $(MAKEFILE_LIST)

clean: clean-venv clean-build clean-pyc clean-test ## remove all venv, build, test, coverage and Python artifacts

clean-venv: ## remove venv artifacts
	rm -fr .venv

clean-build: ## remove build artifacts
	rm -fr build/
	rm -fr dist/
	rm -fr .eggs/
	find . -name '*.egg-info' -exec rm -fr {} +
	find . -name '*.egg' -exec rm -f {} +

clean-pyc: ## remove Python file artifacts
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

clean-test: ## remove test and coverage artifacts
	rm -fr .tox/
	rm -f .coverage
	rm -fr htmlcov/
	rm -fr .pytest_cache

venv: ## set up a virtualenv for development
	test -d .venv || virtualenv .venv
	. .venv/bin/activate; pip install -Ur requirements_dev.txt

develop: venv ## install into a virtualenv
	. .venv/bin/activate; pip install -e .

lint: ## check style with flake8
	. .venv/bin/activate; flake8 src tests

test: ## run tests quickly with the default Python
	. .venv/bin/activate; nosetests

test-all: ## run tests on every Python version with tox
	. .venv/bin/activate; tox

coverage: ## check code coverage quickly with the default Python
	. .venv/bin/activate; coverage run --source usb_iss .venv/bin/nosetests
	. .venv/bin/activate; coverage report -m
	. .venv/bin/activate; coverage html
	$(BROWSER) htmlcov/index.html

docs: ## generate Sphinx HTML documentation, including API docs
	rm -f docs/usb_iss.rst
	rm -f docs/modules.rst
	. .venv/bin/activate; sphinx-apidoc -o docs/ src
	. .venv/bin/activate; $(MAKE) -C docs clean
	. .venv/bin/activate; $(MAKE) -C docs html
	$(BROWSER) docs/_build/html/index.html

release: dist ## package and upload a release
	. .venv/bin/activate; twine upload dist/*

dist: clean venv ## builds source and wheel package
	. .venv/bin/activate; python setup.py sdist
	. .venv/bin/activate; python setup.py bdist_wheel
	ls -l dist
