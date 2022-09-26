# Settings
# NOTE: The multi-python image is a fork of fkrull/multi-python, which as of now has not been updated for Python 3.10 yet
DOCKER_MULTI_PYTHON_IMAGE = gnufede/multi-python:focal
DOCKER_USER = "$(shell id -u):$(shell id -g)"

# Default target
.DEFAULT_GOAL := tox


# Development environment
# -----------------------

# Install a virtualenv
.PHONY: venv
venv:
	virtualenv venv
	. venv/bin/activate && pip install --upgrade pip tox build && pip install -e ".[testing]"

# Build distribution package
.PHONY: build
build:
	. venv/bin/activate && python -m build


# Test suite
# ----------

# Run complete tox suite
.PHONY: tox
tox:
	tox

# Run tox in venv (needs to be installed with `make venv` first)
.PHONY: venv-tox
venv-tox:
	. venv/bin/activate && tox

# Only run pytest
.PHONY: test
test:
	tox -e 'clean,py{310,39,38,37},report'

# Only run flake8 linter
.PHONY: flake8
flake8:
	tox -e flake8

# Open HTML coverage report in browser
.PHONY: open-coverage
open-coverage:
	$(or $(BROWSER),firefox) ./reports/coverage_html/index.html

# Run complete tox test suite in a multi-python Docker container
.PHONY: docker-tox
docker-tox:
	docker run --rm --tty \
		--user $(DOCKER_USER) \
		--mount "type=bind,src=$(shell pwd),target=/code" \
		--workdir /code \
		--env HOME=/tmp/home \
		$(DOCKER_MULTI_PYTHON_IMAGE) \
		tox --workdir .tox_docker $(TOX_ARGS)

# Run partial tox test suites in Docker
.PHONY: docker-tox-py310 docker-tox-py39 docker-tox-py38 docker-tox-py37
docker-tox-py310: TOX_ARGS="-e clean,py310,py310-report"
docker-tox-py310: docker-tox
docker-tox-py39: TOX_ARGS="-e clean,py39,py39-report"
docker-tox-py39: docker-tox
docker-tox-py38: TOX_ARGS="-e clean,py38,py38-report"
docker-tox-py38: docker-tox
docker-tox-py37: TOX_ARGS="-e clean,py37,py37-report"
docker-tox-py37: docker-tox

# Run all tox test suites, but separately to check code coverage individually
.PHONY: docker-tox-all
docker-tox-all:
	make docker-tox-py37
	make docker-tox-py38
	make docker-tox-py39
	make docker-tox-py310

# Pull the latest image of the multi-python Docker image
.PHONY: docker-pull
docker-pull:
	docker pull $(DOCKER_MULTI_PYTHON_IMAGE)


# Cleanup
# -------

.PHONY: clean
clean:
	rm -rf .coverage .pytest_cache reports src/validataclass/_version.py

.PHONY: clean-dist
clean-dist:
	rm -rf dist/

.PHONY: clean-all
clean-all: clean clean-dist
	rm -rf .tox .tox_docker .eggs src/*.egg-info venv
