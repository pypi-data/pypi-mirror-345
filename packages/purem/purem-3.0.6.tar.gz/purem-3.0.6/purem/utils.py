"""
Business Source License 1.1

Copyright (C) 2025 Raman Marozau, raman@worktif.com
Use of this software is governed by the Business Source License included in the LICENSE file and at www.mariadb.com/bsl11.

Change Date: Never
On the date above, in accordance with the Business Source License, use of this software will be governed by the open source license specified in the LICENSE file.
Additional Use Grant: Free for personal and non-commercial research use only.

SPDX-License-Identifier: BUSL-1.1
"""

import numpy as np
from numba import njit
from numpy import ndarray


@njit(parallel=True, fastmath=True)
def _compute_shifted_jit(entire_input: ndarray, entire_out: ndarray):
    x_max = np.float32(-np.inf)
    for i in range(entire_input.shape[0]):
        if entire_input[i] > x_max:
            x_max = entire_input[i]
    for i in range(entire_input.shape[0]):
        entire_out[i] = entire_input[i] - x_max
