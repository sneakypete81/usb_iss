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

VENV = . .venv/bin/activate;

API_EXCLUDE := src/usb_iss/usb_iss.py src/usb_iss/driver.py

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
	$(VENV) pip install -Ur requirements_dev.txt

develop: venv ## install into a virtualenv
	$(VENV) pip install -e .

lint: ## check style with flake8
	$(VENV) flake8 src tests

test: ## run tests quickly with the default Python
	$(VENV) nosetests

test-all: ## run tests on every Python version with tox
	$(VENV) tox

coverage: ## check code coverage quickly with the default Python
	$(VENV) coverage run --source usb_iss .venv/bin/nosetests
	$(VENV) coverage report -m
	$(VENV) coverage html
	$(BROWSER) htmlcov/index.html

docs: ## generate Sphinx HTML documentation, including API docs
	rm -f docs/usb_iss.rst
	rm -f docs/modules.rst

	# Generate API documentation input
	$(VENV) sphinx-apidoc --no-toc --module-first -o docs/ src $(API_EXCLUDE)

	# Generate HTML documentation
	$(VENV) $(MAKE) -C docs clean
	$(VENV) $(MAKE) -C docs html
	$(BROWSER) docs/_build/html/index.html

release: dist ## package and upload a release
	$(VENV) twine upload dist/*

dist: clean venv ## builds source and wheel package
	$(VENV) python setup.py sdist
	$(VENV) python setup.py bdist_wheel
	ls -l dist
