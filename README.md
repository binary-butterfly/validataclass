# validataclass

[![Unit tests](https://github.com/binary-butterfly/validataclass/actions/workflows/tests.yml/badge.svg)](https://github.com/binary-butterfly/validataclass/actions/workflows/tests.yml)

Python library for input validation designed for (but not restricted to) JSON-based APIs, neatly integrating with dataclasses. 

**Status:** In development / alpha.


## Installation

(TODO...)


## Usage

~~See `docs/` for documentation on how to use this library and for examples.~~

The documentation is a work in progress and will be part of version 0.2.0.

Until then, take a look at the code. It's well documented using docstrings, including lots of examples.


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
