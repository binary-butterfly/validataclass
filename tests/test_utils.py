# encoding: utf-8

"""
binary butterfly validator
Copyright (c) 2021, binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""


def unpack_params(*args) -> list[tuple]:
    """
    Returns a list containing tuples build from the arguments. Arguments that are lists are "unpacked" by combining the other elements
    of the tuples with all elements in this list. Useful for constructing datasets for test parametrization.

    Examples:

    ```
    # No unpacking because none of the arguments is a list:
    unpack_params(1, 2, 3) == [
        (1, 2, 3)
    ]

    # Unpacking a single list of values
    unpack_params(1, 2, ['a', 'b', 'c']) == [
        (1, 2, 'a'),
        (1, 2, 'b'),
        (1, 2, 'c'),
    ]

    # Unpacking multiple lists
    unpack_params('foo', [1, 2, 3], ['a', 'b']) == [
        ('foo', 1, 'a'),
        ('foo', 1, 'b'),
        ('foo', 2, 'a'),
        ('foo', 2, 'b'),
        ('foo', 3, 'a'),
        ('foo', 3, 'b'),
    ]

    # Unpacking a list of tuples
    unpack_params('foo', [(1, 'a'), (2, 'b'), (3, 'c')]) == [
        ('foo', 1, 'a'),
        ('foo', 2, 'b'),
        ('foo', 3, 'c'),
    ]

    # Combine multiple unpacked lists, e.g. to use in pytest parametrization
    [
        *unpack_params('some_parameter', [('some', 1), ('test', 2), ('data', 3)]),
        *unpack_params('other_parameter', [('other', 42), ('values', 1337)]),
    ] == [
        ('some_parameter', 'some', 1),
        ('some_parameter', 'test', 2),
        ('some_parameter', 'data', 3),
        ('other_parameter', 'other', 42),
        ('other_parameter', 'values', 1337)
    ]
    ```
    """
    unpacked = [tuple()]
    for arg in args:
        if type(arg) is list:
            arg_tuples = [item if type(item) is tuple else (item,) for item in arg]
            unpacked = [(*current_params, *next_param) for current_params in unpacked for next_param in arg_tuples]
        else:
            unpacked = [(*current_params, arg) for current_params in unpacked]
    return unpacked
