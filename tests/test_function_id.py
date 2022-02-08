# SPDX-FileCopyrightText: (c) 2021 Artёm IG <github.com/rtmigo>
# SPDX-License-Identifier: MIT

import unittest

from filememo._dir_for_func import _file_and_method, _caller_not_filememo
from filememo._indirect_caller import get_caller_indirect


def func():
    pass


def outer():
    def inner():
        pass

    return _file_and_method(inner)


def matroska1():
    def matroska2():
        def matroska3():
            pass

        return _file_and_method(matroska3)

    return matroska2()


class Test(unittest.TestCase):

    def test_caller_direct(self):
        s = _caller_not_filememo()
        self.assertEqual(s, __file__)

    def test_caller_indirect(self):
        s = get_caller_indirect()
        self.assertEqual(s, __file__)

    def assertEnds(self, s: str, ending: str):
        s = s.replace('\\', '/')
        ending = ending.replace('\\', '/')
        if not s.endswith(ending):
            self.fail(f'{s} does not end with {ending}')

    def test_self(self):
        self.assertEnds(
            _file_and_method(self.test_self),
            '/test_function_id.py/Test.test_self')

    def test_func(self):
        self.assertEnds(
            _file_and_method(func),
            '/test_function_id.py/func')

    def test_inner(self):
        self.assertEnds(
            outer(),
            '/test_function_id.py/outer.<locals>.inner')

    def test_matroska(self):
        self.assertEnds(
            matroska1(),
            '/test_function_id.py/matroska1.<locals>'
            '.matroska2.<locals>.matroska3')
