# SPDX-FileCopyrightText: (c) 2020 Artёm IG <github.com/rtmigo>
# SPDX-License-Identifier: MIT


import time
import unittest
from datetime import timedelta
from pathlib import Path
from tempfile import TemporaryDirectory

from filememo import memoize

global_func_calls = 0
inner_func_calls = 0

ver = int(time.time() * 100)


@memoize(version=ver)
def global_func(a, b):
    global global_func_calls
    global_func_calls += 1
    return a * b


def outer_func(a, b):
    @memoize(version=ver)
    def inner_func(_a, _b):
        global inner_func_calls
        inner_func_calls += 1
        return _a * _b

    return inner_func(a, b)


static_method_calls = 0
class_method_calls = 0

noargs_calls = 0


@memoize(version=ver)
def no_args():
    global noargs_calls
    noargs_calls += 1
    pass


class Class:

    @staticmethod
    @memoize(version=ver)
    def static(a, b):
        global static_method_calls
        static_method_calls += 1
        return a * b

    @classmethod
    @memoize(version=ver)
    def clmethod(cls, a, b):
        global class_method_calls
        class_method_calls += 1
        return a * b


class TestDecorator(unittest.TestCase):

    # test caching BETWEEN program runs

    def test(self):
        with TemporaryDirectory() as td:
            tempTestDir = Path(td) / "TestDecorator"
            print("Using temp directory", tempTestDir)

            function_calls = 0

            @memoize(dir_path=tempTestDir, max_age=timedelta(seconds=0.2))
            def real_function(a: int, b: int) -> int:
                nonlocal function_calls
                function_calls += 1
                return a + b

            self.assertEqual(0, function_calls)
            self.assertEqual(3, real_function(1, 2))  # computing new
            self.assertEqual(1, function_calls)
            self.assertEqual(3, real_function(1, 2))  # reading from cache
            self.assertEqual(1, function_calls)

            time.sleep(0.5)
            # computing new (old is out of date)
            self.assertEqual(3, real_function(1, 2))
            self.assertEqual(2, function_calls)

            self.assertEqual(9, real_function(5, 4))
            self.assertEqual(3, function_calls)

            self.assertEqual(5, real_function(a=2, b=3))
            self.assertEqual(4, function_calls)
            self.assertEqual(5, real_function(a=2, b=3))
            self.assertEqual(4, function_calls)

            # the order of the kw-arguments theoretically (very theoretically)
            # can affect the result of the function, so if the same data is
            # given in a different order, calculate again
            self.assertEqual(5, real_function(b=3, a=2))
            self.assertEqual(5, function_calls)

    def test_no_dir_path(self):
        calls = 0

        @memoize
        def function(a: int, b: int) -> int:
            nonlocal calls
            calls += 1
            return a * b

        function(1, 2)
        function(1, 2)

        self.assertLessEqual(calls, 1)

    def test_args(self):
        with TemporaryDirectory() as td:
            calls = 0

            @memoize(dir_path=td)
            def function(a: int, b: int) -> int:
                nonlocal calls
                calls += 1
                return a * b

            self.assertEqual(function(2, 3), 6)
            self.assertEqual(function(2, 3), 6)
            self.assertEqual(calls, 1)

            self.assertEqual(function(4, 5), 20)
            self.assertEqual(calls, 2)

            self.assertEqual(function(2, b=3), 6)
            self.assertEqual(calls, 3)

            self.assertEqual(function(a=2, b=3), 6)
            self.assertEqual(calls, 4)
            self.assertEqual(function(a=2, b=3), 6)
            self.assertEqual(calls, 4)

            self.assertEqual(function(b=3, a=2), 6)
            self.assertEqual(calls, 5)

    def test_global(self):
        self.assertEqual(global_func_calls, 0)
        self.assertEqual(global_func(2, 3), 6)
        self.assertEqual(global_func(2, 3), 6)
        self.assertEqual(global_func_calls, 1)

    def test_inner(self):
        self.assertEqual(inner_func_calls, 0)
        self.assertEqual(outer_func(2, 3), 6)
        self.assertEqual(outer_func(2, 3), 6)
        self.assertEqual(inner_func_calls, 1)

    def test_static(self):
        self.assertEqual(static_method_calls, 0)
        self.assertEqual(Class.static(2, 3), 6)
        self.assertEqual(Class.static(2, 3), 6)
        self.assertEqual(static_method_calls, 1)

    def test_class_method(self):
        self.assertEqual(class_method_calls, 0)
        self.assertEqual(Class.clmethod(2, 3), 6)
        self.assertEqual(Class.clmethod(2, 3), 6)
        self.assertEqual(class_method_calls, 1)

    def test_noargs(self):
        self.assertEqual(noargs_calls, 0)
        no_args()
        no_args()
        self.assertEqual(noargs_calls, 1)

    def test_path_as_path(self):
        with TemporaryDirectory() as td:
            @memoize(dir_path=Path(td))  # not string
            def function(a: int, b: int) -> int:
                pass

            function(1, 1)
