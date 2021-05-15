# SPDX-FileCopyrightText: (c) 2021 Artёm IG <github.com/rtmigo>
# SPDX-License-Identifier: MIT

from ._dir_for_func import _caller_not_filememo


def get_caller_indirect():
    """Helps to test the _caller_not_filememo function.
    This function needs to be declared inside `filememo` not, in `tests`.
    The result of the function must be the file that called
    `get_caller_indirect`
    """
    return _caller_not_filememo()
