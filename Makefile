# Settings
# NOTE: The multi-python image is a fork of fkrull/multi-python, which as of now has not been updated for Python 3.10 yet
DOCKER_MULTI_PYTHON_IMAGE = gnufede/multi-python:focal
DOCKER_USER = "$(shell id -u):$(shell id -g)"

.PHONY: all venv build \
	tox test flake8 open-coverage \
	docker-tox docker-tox-py37 docker-tox-py38 docker-tox-py39 docker-tox-py310 docker-pull \
	clean clean-dist clean-all

# Default target
all: tox


# Development environment
# -----------------------

# Install a virtualenv
venv:
	virtualenv venv
	. venv/bin/activate && pip install -r requirements.txt && pip install -e .

# Build distribution package
build:
	. venv/bin/activate && python -m build


# Test suite
# ----------

# Run complete tox suite
tox:
	tox

# Only run pytest
test:
	tox -e 'clean,py{310,39,38,37,py3},report'

# Only run flake8 linter
flake8:
	tox -e flake8

# Open HTML coverage report in browser
open-coverage:
	$(or $(BROWSER),firefox) ./reports/coverage_html/index.html

# Run complete tox test suite in a multi-python Docker container
docker-tox:
	docker run --rm --tty \
		--user $(DOCKER_USER) \
		--mount "type=bind,src=$(shell pwd),target=/code" \
		--workdir /code \
		--env HOME=/tmp/home \
		--env COVERAGE_FILE=.coverage_docker \
		$(DOCKER_MULTI_PYTHON_IMAGE) \
		tox --workdir .tox_docker $(TOX_ARGS)

# Run partial tox test suites in Docker
docker-tox-py39: TOX_ARGS="-e py310"
docker-tox-py39: docker-tox
docker-tox-py39: TOX_ARGS="-e py39"
docker-tox-py39: docker-tox
docker-tox-py38: TOX_ARGS="-e py38"
docker-tox-py38: docker-tox
docker-tox-py37: TOX_ARGS="-e py37"
docker-tox-py37: docker-tox

# Pull the latest image of the multi-python Docker image
docker-pull:
	docker pull $(DOCKER_MULTI_PYTHON_IMAGE)


# Cleanup
# -------
clean:
	rm -rf .coverage .pytest_cache reports src/validataclass/_version.py

clean-dist:
	rm -rf dist/

clean-all: clean clean-dist
	rm -rf .tox .tox_docker .eggs src/*.egg-info venv
