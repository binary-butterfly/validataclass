# encoding: utf-8

"""
binary butterfly validator
Copyright (c) 2021, binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

import re
from typing import Any, Optional

from ..abstract_input import AbstractInput
from ..fields import Field
from ..validators import Regexp
from ..exceptions import ValidationError
from ..external import HostnameValidation


class URL(Regexp):
    default_message = 'invalid url'

    def __init__(self, require_tld: bool = True, allow_ip: bool = True, message: Optional[str] = None):
        super().__init__(
            r"^[a-z]+://(?P<host>[^\/\?:]+)(?P<port>:[0-9]+)?(?P<path>\/.*?)?(?P<query>\?.*)?$",
            re.IGNORECASE,
            message
        )
        self.validate_hostname = HostnameValidation(
            require_tld=require_tld,
            allow_ip=allow_ip,
        )

    def __call__(self, value: Any, form: AbstractInput, field: Field):
        match = super().__call__(value, form, field)
        if not self.validate_hostname(match.group('host')):
            raise ValidationError(self.message)
