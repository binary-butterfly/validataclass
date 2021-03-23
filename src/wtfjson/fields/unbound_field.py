# encoding: utf-8

"""
binary butterfly validator
Copyright (c) 2021, binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""


class UnboundField:
    def __init__(self, field_class, *args, name=None, **kwargs):
        self.field_class = field_class
        self.args = args
        self.name = name
        self.kwargs = kwargs

    def bind(self, form, field_name, **kwargs):
        return self.field_class(*self.args, **dict(form=form, field_name=field_name, **self.kwargs, **kwargs))
