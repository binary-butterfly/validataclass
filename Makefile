.PHONY: all \
	tox test flake8 open-coverage \
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


# Cleanup
# -------
clean:
	rm -rf .coverage .pytest_cache reports

clean-all: clean
	rm -rf .tox .eggs venv
