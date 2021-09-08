# encoding: utf-8

"""
binary butterfly validator
Copyright (c) 2021, binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from tests.test_utils import unpack_params


class UnpackParamsTest:
    """ Tests for the test helper function unpack_params(). """

    @staticmethod
    def test_unpack_params_without_lists():
        assert unpack_params(1, 2, 3) == [(1, 2, 3)]

    @staticmethod
    def test_unpack_single_list():
        assert unpack_params(1, 2, ['a', 'b', 'c']) == [
            (1, 2, 'a'),
            (1, 2, 'b'),
            (1, 2, 'c'),
        ]

    @staticmethod
    def test_unpack_multiple_lists():
        assert unpack_params('foo', [1, 2, 3], ['a', 'b']) == [
            ('foo', 1, 'a'),
            ('foo', 1, 'b'),
            ('foo', 2, 'a'),
            ('foo', 2, 'b'),
            ('foo', 3, 'a'),
            ('foo', 3, 'b'),
        ]

    @staticmethod
    def test_unpack_list_of_tuples():
        assert unpack_params('foo', [(1, 'a'), (2, 'b'), (3, 'c')]) == [
            ('foo', 1, 'a'),
            ('foo', 2, 'b'),
            ('foo', 3, 'c'),
        ]

    @staticmethod
    def test_unpack_multiple_lists_of_tuples():
        assert unpack_params([('foo', 'FOO'), ('bar', 'BAR'), ('baz', 'BAZ')], [(1, 'a'), (2, 'b'), (3, 'c')]) == [
            ('foo', 'FOO', 1, 'a'),
            ('foo', 'FOO', 2, 'b'),
            ('foo', 'FOO', 3, 'c'),
            ('bar', 'BAR', 1, 'a'),
            ('bar', 'BAR', 2, 'b'),
            ('bar', 'BAR', 3, 'c'),
            ('baz', 'BAZ', 1, 'a'),
            ('baz', 'BAZ', 2, 'b'),
            ('baz', 'BAZ', 3, 'c'),
        ]
