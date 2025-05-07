"""
Business Source License 1.1

Copyright (C) 2025 Raman Marozau, raman@worktif.com
Use of this software is governed by the Business Source License included in the LICENSE file and at www.mariadb.com/bsl11.

Change Date: Never
On the date above, in accordance with the Business Source License, use of this software will be governed by the open source license specified in the LICENSE file.
Additional Use Grant: Free for personal and non-commercial research use only.

SPDX-License-Identifier: BUSL-1.1
"""

from purem import load_env_config


class Logger:
    def __init__(self):
        self._env = load_env_config()
        self._default_info_message = f"Something went wrong"

    def info(self, message: str, verbose: bool = False) -> str:
        if self._env.PUREM_VERBOSE is True or verbose is True:
            return f"[purem]: {message}\n"
        else:
            return f"[purem]: {self._default_info_message}\n"

    def info_new_line(self, message: str) -> str:
        if self._env.PUREM_VERBOSE is True:
            return f"\n[purem]: {message}\n"
        else:
            return f"\n[purem]: {self._default_info_message}\n"

    def printr(self, message: str) -> str or None:
        if self._env.PUREM_VERBOSE is True:
            print(self.info(message))
