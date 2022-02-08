import unittest
from functools import lru_cache
from tempfile import TemporaryDirectory

from filememo import memoize


class TestCombine(unittest.TestCase):
    def test(self):
        with TemporaryDirectory() as td:
            calls = 0

            def on_call(*args, **kwargs):
                nonlocal calls
                calls += 1

            @lru_cache
            @memoize(dir_path=td, _on_call=on_call)
            def cache_me():
                return ':)'

            self.assertEqual(calls, 0)
            self.assertEqual(cache_me(), ':)')
            self.assertEqual(calls, 1)
