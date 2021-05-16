# SPDX-FileCopyrightText: (c) 2020 Artёm IG <github.com/rtmigo>
# SPDX-License-Identifier: MIT


import time
import unittest
from datetime import timedelta, datetime
from pathlib import Path
from tempfile import TemporaryDirectory

from filememo import memoize
from filememo._deco import FunctionException


class TestExceptions(unittest.TestCase):

    def test_cache_exceptions(self):
        with TemporaryDirectory() as td:
            calls = 0

            @memoize(dir_path=td)
            def divide(a: int, b: int) -> float:
                nonlocal calls
                calls += 1
                return a / b

            self.assertEqual(calls, 0)
            with self.assertRaises(FunctionException) as cm:
                divide(1, 0)
            self.assertIsInstance(cm.exception.inner, ZeroDivisionError)
            self.assertEqual(calls, 1)
            with self.assertRaises(FunctionException) as cm:
                divide(1, 0)
            self.assertIsInstance(cm.exception.inner, ZeroDivisionError)
            self.assertEqual(calls, 1)

    def test_do_not_cache_exceptions(self):
        with TemporaryDirectory() as td:
            calls = 0

            @memoize(dir_path=td, exceptions_max_age=None)
            def divide(a: int, b: int) -> float:
                nonlocal calls
                calls += 1
                return a / b

            self.assertEqual(calls, 0)
            with self.assertRaises(FunctionException) as cm:
                divide(1, 0)
            self.assertIsInstance(cm.exception.inner, ZeroDivisionError)
            self.assertEqual(calls, 1)
            with self.assertRaises(FunctionException) as cm:
                divide(1, 0)
            self.assertIsInstance(cm.exception.inner, ZeroDivisionError)
            self.assertEqual(calls, 2)

    def test_exceptions_max_age(self):
        with TemporaryDirectory() as td:
            calls = 0

            @memoize(dir_path=td, exceptions_max_age=timedelta(milliseconds=200))
            def divide(a: int, b: int) -> float:
                nonlocal calls
                calls += 1
                return a / b

            self.assertEqual(calls, 0)
            with self.assertRaises(FunctionException) as cm:
                divide(1, 0)
            self.assertIsInstance(cm.exception.inner, ZeroDivisionError)

            self.assertEqual(calls, 1)
            with self.assertRaises(FunctionException) as cm:
                divide(1, 0)
            self.assertIsInstance(cm.exception.inner, ZeroDivisionError)
            self.assertEqual(calls, 1)

            time.sleep(1)

            with self.assertRaises(FunctionException) as cm:
                divide(1, 0)
            self.assertIsInstance(cm.exception.inner, ZeroDivisionError)
            self.assertEqual(calls, 2)
            with self.assertRaises(FunctionException) as cm:
                divide(1, 0)
            self.assertIsInstance(cm.exception.inner, ZeroDivisionError)
            self.assertEqual(calls, 2)
