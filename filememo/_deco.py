# SPDX-FileCopyrightText: (c) 2020 Artёm IG <github.com/rtmigo>
# SPDX-License-Identifier: MIT


import datetime as dt
import functools
import hashlib
import tempfile
from pathlib import Path
from typing import Callable, Union, Optional

from pickledir import PickleDir

from filememo._dir_for_func import find_dir_for_method


def _md5(s: str):
    return hashlib.md5(s.encode('utf-8')).hexdigest()


class FunctionException(BaseException):
    def __init__(self, inner: BaseException):
        self.inner = inner


def _utc() -> dt.datetime:
    return dt.datetime.utcnow().replace(tzinfo=dt.timezone.utc)


def memoize(function: Callable = None,
            dir_path: Union[Path, str] = None,
            max_age: dt.timedelta = dt.timedelta.max,
            exceptions_max_age: Optional[dt.timedelta] = dt.timedelta.max,
            version: int = None) -> Callable:
    # If called without method, we've been called with optional arguments.
    # We return a decorator with the optional arguments filled in.
    # Next time round we'll be decorating method.
    if function is None:
        return functools.partial(memoize, dir_path=dir_path, max_age=max_age,
                                 version=version,
                                 exceptions_max_age=exceptions_max_age)

    # method_str = _file_and_method(method)

    @functools.wraps(function)
    def f(*args, **kwargs):
        key = (args, kwargs)

        # try get existing result from the cache
        # try:
        # we will use max_age on both reading and writing

        # print(f.data.dirpath)

        pd_result_max_age = max_age if max_age != dt.timedelta.max else None

        record = f.data._get_record(key, max_age=pd_result_max_age)
        if record is not None:

            exception, result = record.data

            if not exception:
                assert result != KeyError  # KeyError will be raised, not returned
                return result

            assert exception is not None
            if exceptions_max_age == dt.timedelta.max or \
                    (_utc() - record.created) <= exceptions_max_age:
                raise FunctionException(exception)
            else:
                # we did not return result and did not raise exception.
                # We will just restart the function
                pass

        # get new result and store it to the cache
        exception: Optional[BaseException] = None
        result = None
        try:
            result = function(*args, **kwargs)
        except BaseException as error:
            if not exceptions_max_age:
                raise FunctionException(exception)
            exception = error

        assert exception is None or exceptions_max_age is not None

        pd_exception_max_age = (exceptions_max_age
                                if exceptions_max_age != dt.timedelta.max
                                else None)

        # we will use max_age on both reading and writing
        f.data.set(key,
                   max_age=pd_exception_max_age if exception else pd_result_max_age,
                   value=(exception, result))

        if exception:
            raise FunctionException(exception)

        return result

    # dir_path is the parent path. Within this directory, we will create
    # a subdirectory that uniquely matches the function we are decorating.
    # - This will allow only function arguments to be used as cache keys,
    #   but not the function id (the subdirectory identifies function)
    # - This will eliminate potential problems with setting different `version`
    #   values in different decorators with the same dir_path

    if dir_path is not None:
        func_parent_dir = Path(dir_path)
    else:
        func_parent_dir = Path(tempfile.gettempdir()) / 'filememo'

    func_cache_dir = find_dir_for_method(func_parent_dir, function)

    f.data = PickleDir(dirpath=func_cache_dir,
                       version=version if version is not None else 1)

    return f
