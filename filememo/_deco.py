# SPDX-FileCopyrightText: (c) 2020 Artёm IG <github.com/rtmigo>
# SPDX-License-Identifier: MIT


import tempfile
import datetime
from typing import Callable, Union
from pathlib import Path
import functools
import os
import hashlib
from pickledir import PickleDir


def _file_and_method(method: Callable) -> str:
    # it helps the decorator to understand what function he is decorating:
    # in what file it is and what it is called

    import inspect

    # finding the first file in the stack that is not-current (not _deco.py).
    # Presumably this is the file where the decorator is used

    abs_file = os.path.abspath(__file__)
    filename = None
    for frame in inspect.stack():
        a = os.path.abspath(frame.filename)
        if a != abs_file:
            filename = a
            break
    assert filename is not None

    # when we convent a callable to a string, we get somethong like
    # "<function my_function at 0x125382620>"
    # "<function func1.<locals>.func2 at 0x125382620>"

    string = str(method)
    if string.startswith('<bound '):  # <bound method
        function_name = string.split()[2]
    else:
        function_name = string.split()[1]

    # "/path/to/loading.py/_getCachedHistory"
    # "/path/to/loading.py/func1.<locals>.func2"
    return f'{filename}{os.path.sep}{function_name}'


def _md5(s: str):
    return hashlib.md5(s.encode('utf-8')).hexdigest()


def memoize(method: Callable = None, dir_path: Union[Path, str] = None,
            max_age: datetime.timedelta = None,
            version: int = None) -> Callable:
    # If called without method, we've been called with optional arguments.
    # We return a decorator with the optional arguments filled in.
    # Next time round we'll be decorating method.
    if method is None:
        return functools.partial(memoize, dir_path=dir_path, max_age=max_age,
                                 version=version)

    method_str = _file_and_method(method)

    @functools.wraps(method)
    def f(*args, **kwargs):
        key = (method_str, args, kwargs)

        # try get existing result from the cache
        try:
            return f.data[key]
        except KeyError:
            pass

        # get new result and store it to the cache
        new_result = method(*args, **kwargs)
        f.data.set(key, max_age=max_age, value=new_result)

        return new_result

    if dir_path is None:
        temp_parent = Path(tempfile.gettempdir())
        method_hash = _md5(method_str)
        if version is None:
            # we will use a hash to generate temp directory name.
            # The items will still have unique key, so there's no reason
            # to worry about hash collisions
            dir_path = temp_parent / method_hash
        else:
            # todo test
            assert version is not None
            # if `version` is specified there is a reason to worry:
            # - hashes may collide, so two functions will be saved
            #   in the same directory
            # - these two functions can use different `version` values,
            #   which will lead to random item deletion
            #
            # This combination of events is somewhat less likely than a
            # software error due to a computer crash during the end of the
            # world due to an asteroid impact.
            #
            # But we can protect ourselves from at least some of the
            # described problems. We will just save different versions
            # to different temporary directories.
            dir_path = temp_parent / f"{method_hash}_{version}"

    dir_path = Path(dir_path)

    f.data = PickleDir(dirpath=dir_path,
                       version=version if version is not None else 1)

    return f
