"""
validataclass
Copyright (c) 2026, binary butterfly GmbH and contributors
Use of this source code is governed by an MIT-style license that can be found in the LICENSE file.
"""

from typing import Any


class DebugLogger:
    """
    Logger class for plugin development and debugging.
    """

    debug_mode: bool

    def __init__(self, debug_mode: bool):
        self.debug_mode = debug_mode

    def log(self, level: str, context: str | None, msg: str, *objects: Any) -> None:
        """
        Log a message on a given level, optionally with a context (e.g. file/line) and with object dumps.
        Debug level messages are only logged if debug mode is enabled.
        """
        level = level.upper()
        if level == 'DEBUG' and not self.debug_mode:
            return

        if context is not None:
            msg = f'{context}: {msg}'

        obj_dumps = [f'{type(obj)} ({obj!s})' for obj in objects]
        if len(obj_dumps) == 1:
            msg = f'{msg}: {obj_dumps[0]})'
        elif len(obj_dumps) > 1:
            msg = '\n- '.join([f'{msg}:', *obj_dumps])

        print(f'[validataclass.mypy] [{level}] {msg}')
