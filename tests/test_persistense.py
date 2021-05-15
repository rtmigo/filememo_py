import os
import shutil
import sys
import time
import unittest
from pathlib import Path
from subprocess import check_call

from .keeps_value.run_me_twice import cache_path


class TestPersist(unittest.TestCase):

    def test_memoized(self):
        # testing that if we call process three times, the cached
        # value will persist

        if cache_path.exists():
            shutil.rmtree(cache_path)

        f = Path(__file__).parent / "keeps_value" / "_memoized.txt"
        if f.exists():
            os.remove(f)

        self.assertFalse(f.exists())
        self.assertFalse(cache_path.exists())

        for _ in range(3):
            check_call((sys.executable,
                        '-m',
                        'tests.keeps_value.run_me_twice',
                        'memoized'))

        self.assertTrue(cache_path.exists())
        self.assertEqual(f.read_text(), '1')

    def test_non_memoized(self):
        # testing ourselves: without caching the function is called
        # three times

        if cache_path.exists():
            shutil.rmtree(cache_path)

        f = Path(__file__).parent / "keeps_value" / "_non_memoized.txt"
        if f.exists():
            os.remove(f)

        self.assertFalse(f.exists())
        self.assertFalse(cache_path.exists())

        for _ in range(3):
            check_call((sys.executable,
                        '-m',
                        'tests.keeps_value.run_me_twice',
                        'non_memoized'))

        self.assertFalse(cache_path.exists())
        self.assertEqual(f.read_text(), '3')

    def test_systemp(self):
        # testing that if the dir path was not specified (it's system temp),
        # the values are cached between calls. In other words, it's not
        # a new temp directory each time

        f = Path(__file__).parent / "keeps_value" / "_memoized_systemp.txt"
        if f.exists():
            os.remove(f)

        self.assertFalse(f.exists())
        self.assertFalse(cache_path.exists())

        version = int(time.time()*1000)

        for _ in range(3):
            check_call((sys.executable,
                        '-m',
                        'tests.keeps_value.run_me_twice',
                        'systemp',
                        str(version)
                        ))

        self.assertEqual(f.read_text(), '1')



        #self.assertLessEqual(int(f.read_text()), 1)
