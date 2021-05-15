import unittest
from filememo import memoize
from pathlib import Path

from tempfile import TemporaryDirectory


class TestDirPath(unittest.TestCase):

    def test_with_path(self):
        with TemporaryDirectory() as td:
            cache_dir = Path(td) / 'cache'
            self.assertFalse(cache_dir.exists())

            @memoize(dir_path=cache_dir)
            def func_a():
                pass

            func_a()

            # cache dir must be created
            self.assertTrue(cache_dir.exists())
