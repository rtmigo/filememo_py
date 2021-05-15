import hashlib
import os
from pathlib import Path
from typing import Optional, Callable


def _md5(s: str):
    return hashlib.md5(s.encode('utf-8')).hexdigest()


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


class PathCandidate:
    __slots__ = ['path']

    def __init__(self, candidate_path: Path):
        self.path = candidate_path

    func_id_basename = 'func.txt'

    @property
    def func_id_path(self) -> Path:
        return self.path / PathCandidate.func_id_basename

    @property
    def method_id(self) -> Optional[str]:
        try:
            return self.func_id_path.read_text()
        except FileNotFoundError:
            return None

    @method_id.setter
    def method_id(self, val: str) -> None:
        def write():
            self.func_id_path.write_text(val)

        try:
            write()
        except FileNotFoundError:
            self.func_id_path.parent.mkdir(parents=True)
            write()


def find_dir_for_method(parent: Path, method: Callable,
                        hash_func: Callable = _md5) -> Path:
    method_str = _file_and_method(method)
    method_hash = hash_func(method_str)
    for i in range(999):
        path_candidate = PathCandidate(parent / f'{method_hash}_{i}')

        if not path_candidate.path.exists():
            path_candidate.method_id = method_str
            assert path_candidate.method_id == method_str
            return path_candidate.path

        if path_candidate.method_id == method_str:
            return path_candidate.path

        # try next candidate
