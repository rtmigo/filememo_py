# SPDX-FileCopyrightText: (c) 2021 Artёm IG <github.com/rtmigo>
# SPDX-License-Identifier: MIT

from ._dir_for_func import _caller_not_filememo


def get_caller():
    """Helps to test the _caller_not_filememo function.
    It is important that the _caller_not_filememo is called FROM filememo,
    from OTHER file than the defines the _caller_not_filememo.
    But as a result we are expecting the get the caller of `get_caller`.
    """
    return _caller_not_filememo()
