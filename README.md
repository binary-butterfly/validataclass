# validataclass

[![Unit tests](https://github.com/binary-butterfly/validataclass/actions/workflows/tests.yml/badge.svg)](https://github.com/binary-butterfly/validataclass/actions/workflows/tests.yml)

Python library for input validation designed for (but not restricted to) JSON-based APIs, neatly integrating with dataclasses.

**Status:** Beta.


## Installation

validataclass is available on [PyPI](https://pypi.org/project/validataclass/).

To install it using [pip](https://pip.pypa.io/en/stable/getting-started/), just run:

```shell
pip install validataclass
```

If you add the package to your dependencies, it is recommended to use [compatible release](https://www.python.org/dev/peps/pep-0440/#compatible-release)
version specifiers to make sure you always get the latest version of the library but without running into breaking changes:

```shell
pip install validataclass~=0.8
```

However, keep in mind that the library still is in its beta phase (as indicated by the major version of 0). There can
and will be smaller breaking changes between 0.x minor versions, but we will try to keep them at a minimum and save them
for the release of version 1.0.0.


## Usage

See [`docs/`](https://github.com/binary-butterfly/validataclass/blob/main/docs/index.md) for documentation on how to use this library and
for examples.

(**Note:** The documentation is mostly done now, but still a work in progress.)


## Development

### Virtual environment

To setup a virtualenv for development of the library, run `make venv`.

Alternatively you can manually run the following commands (which do the same as the make target):

```
$ virtualenv venv
$ source venv/bin/activate
$ pip install -r requirements.txt
$ pip install -e .
```


### Running unit tests

Unit tests can be run using `make tox` or by directly executing `tox`.

For this to work you need to either be inside the virtualenv (see above) or to have [tox](https://tox.wiki/en/latest/) installed
in your system locally.
