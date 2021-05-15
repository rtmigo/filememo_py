# SPDX-FileCopyrightText: (c) 2020 Artёm IG <github.com/rtmigo>
# SPDX-License-Identifier: MIT


import datetime
import functools
import hashlib
import tempfile
from pathlib import Path
from typing import Callable, Union

from pickledir import PickleDir

from filememo._dir_for_method import find_dir_for_method


def _md5(s: str):
    return hashlib.md5(s.encode('utf-8')).hexdigest()


def memoize(function: Callable = None,
            dir_path: Union[Path, str] = None,
            max_age: datetime.timedelta = None,
            version: int = None) -> Callable:
    # If called without method, we've been called with optional arguments.
    # We return a decorator with the optional arguments filled in.
    # Next time round we'll be decorating method.
    if function is None:
        return functools.partial(memoize, dir_path=dir_path, max_age=max_age,
                                 version=version)

    # method_str = _file_and_method(method)

    @functools.wraps(function)
    def f(*args, **kwargs):
        key = (args, kwargs)

        # try get existing result from the cache
        try:
            # we will use max_age on both reading and writing
            result = f.data.get(key, max_age=max_age, default=KeyError)
            assert result != KeyError  # KeyError will be raised, not returned
            return result
        except KeyError:
            pass

        # get new result and store it to the cache
        new_result = function(*args, **kwargs)
        # we will use max_age on both reading and writing
        f.data.set(key, max_age=max_age, value=new_result)

        return new_result

    # dir_path is the parent path. Within this directory, we will create
    # a subdirectory that uniquely matches the function we are decorating.
    # - This will allow only function arguments to be used as cache keys,
    #   but not the function id (the subdirectory identifies function)
    # - This will eliminate potential problems with setting different `version`
    #   values in different decorators with the same dir_path

    if dir_path is not None:
        func_parent_dir = Path(dir_path)
    else:
        func_parent_dir = Path(tempfile.gettempdir())

    func_cache_dir = find_dir_for_method(func_parent_dir, function)

    f.data = PickleDir(dirpath=func_cache_dir,
                       version=version if version is not None else 1)

    return f
