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


def _max_to_none(delta: dt.timedelta) -> Optional[dt.timedelta]:
    if delta == dt.timedelta.max:
        return None
    else:
        return delta


def _is_outdated_exception(created: dt.datetime,
                           max_age: Optional[dt.timedelta]) -> bool:
    if max_age == dt.timedelta.max:
        return False
    if max_age is None:  # means zero
        return True
    return (_utc() - created) > max_age


def _is_outdated_result(created: dt.datetime, max_age: dt.timedelta) -> bool:
    assert max_age is not None
    if max_age == dt.timedelta.max:
        return False
    return (_utc() - created) > max_age


def memoize(function: Callable = None,
            dir_path: Union[Path, str] = None,
            max_age: dt.timedelta = dt.timedelta.max,
            exceptions_max_age: Optional[dt.timedelta] = dt.timedelta.max,
            version: int = None,
            _on_call: Callable = None) -> Callable:
    # If called without method, we've been called with optional arguments.
    # We return a decorator with the optional arguments filled in.
    # Next time round we'll be decorating method.
    if function is None:
        return functools.partial(memoize, dir_path=dir_path, max_age=max_age,
                                 version=version,
                                 exceptions_max_age=exceptions_max_age,
                                 _on_call=_on_call)

    if max_age is None:
        raise ValueError('max_age must not be None')

    ##############################################################
    # THE FUNCTION TO RUN ON EVERY CALL

    @functools.wraps(function)
    def f(*args, **kwargs):
        key = (args, kwargs)

        # TRYING TO RETURN FROM CACHE

        # we will use max_age on both reading and writing
        record = f.data._get_record(key)
        if record is not None:

            old_exception, old_result = record.data

            if old_exception is not None:
                if not _is_outdated_exception(record.created,
                                              exceptions_max_age):
                    raise FunctionException(old_exception)
            else:
                assert old_exception is None
                # we don't need to delete anything on reading
                if not _is_outdated_result(record.created, max_age):
                    return old_result

            # we did not return result and did not raise exception.
            # We will restart the function

        # COMPUTING NEW RESULT AND SAVING TO CACHE
        try:
            if _on_call is not None:
                _on_call(*args, **kwargs)
            new_result = function(*args, **kwargs)
            new_exception = None
        except KeyboardInterrupt:
            raise
        except SystemExit:
            raise
        except BaseException as exc:
            new_exception = exc
            new_result = None

        if new_exception is not None and exceptions_max_age is None:
            raise FunctionException(new_exception)

        assert new_exception is None or exceptions_max_age is not None
        assert new_exception is None or new_result is None

        # we will use max_age on both reading and writing
        f.data.set(key,
                   max_age=_max_to_none(exceptions_max_age
                                        if new_exception is not None
                                        else max_age),
                   value=(new_exception, new_result))

        if new_exception is not None:
            raise FunctionException(new_exception)
        else:
            return new_result

    ##############################################################
    # CONTINUING INITIALIZING THE DECORATOR

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
