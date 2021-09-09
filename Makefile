# Settings
DOCKER_MULTI_PYTHON_IMAGE = fkrull/multi-python:focal
DOCKER_USER = "$(shell id -u):$(shell id -g)"

.PHONY: all \
	tox test flake8 open-coverage \
	docker-tox docker-tox-py37 docker-tox-py38 docker-tox-py39 \
	clean clean-all

# Default target
all: tox


# Test suite
# ----------

# Run complete tox suite
tox:
	tox

# Only run pytest
test:
	tox -e 'py{39,38,37,py3}'

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
		$(DOCKER_MULTI_PYTHON_IMAGE) \
		tox --workdir .tox_docker $(TOX_ARGS)

# Run partial tox test suites in Docker
docker-tox-py39: TOX_ARGS="-e py39"
docker-tox-py39: docker-tox
docker-tox-py38: TOX_ARGS="-e py38"
docker-tox-py38: docker-tox
docker-tox-py37: TOX_ARGS="-e py37"
docker-tox-py37: docker-tox


# Cleanup
# -------
clean:
	rm -rf .coverage .pytest_cache reports

clean-all: clean
	rm -rf .tox .tox_docker .eggs venv
