import os
import unittest

from filememo._deco import _file_and_method


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

    def assertEnds(self, s: str, ending: str):
        s = s.replace(os.path.sep, '_')
        ending = ending.replace(os.path.sep, '_')
        if not s.endswith(ending):
            self.fail(f'{s} does not end with {ending}')

    def test_self(self):
        self.assertEnds(
            _file_and_method(self.test_self),
            '/test_file_and_method.py/Test.test_self')

    def test_func(self):
        self.assertEnds(
            _file_and_method(func),
            '/test_file_and_method.py/func')

    def test_inner(self):
        self.assertEnds(
            outer(),
            '/test_file_and_method.py/outer.<locals>.inner')

    def test_matroska(self):
        self.assertEnds(
            matroska1(),
            '/test_file_and_method.py/matroska1.<locals>'
            '.matroska2.<locals>.matroska3')
