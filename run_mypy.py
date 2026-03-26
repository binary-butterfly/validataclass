"""
validataclass
Copyright (c) 2026, binary butterfly GmbH and contributors
Use of this source code is governed by an MIT-style license that can be found in the LICENSE file.
"""

# Helper script that wraps running mypy for easier debugging in PyCharm.

import sys
from mypy import api

# Set this to True to disable the mypy cache (or pass --no-incremental via CLI args)
disable_mypy_cache = False

# Run mypy
mypy_args = ['--show-traceback']
if disable_mypy_cache:
    mypy_args.append('--no-incremental')

result = api.run(mypy_args + sys.argv[1:])

if result[0]:
    print('\nType checking report:\n')
    print(result[0])  # stdout

if result[1]:
    print('\nError report:\n')
    print(result[1])  # stderr

print('\nExit status:', result[2])
