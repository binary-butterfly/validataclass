# encoding: utf-8

"""
binary butterfly validator
Copyright (c) 2021, binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from typing import Optional

from ..validators import Length


class InputRequired(Length):
    default_message = 'input required'

    def __init__(self, message: Optional[str] = None):
        super().__init__(min=0, message=message)
