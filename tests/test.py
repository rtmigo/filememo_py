import os
import unittest
from datetime import timedelta
from pathlib import Path

from filememo import memoize


class TestDecorator(unittest.TestCase):

    def test(self):

        import tempfile, shutil, time

        tempTestDir = Path(tempfile.gettempdir()) / "TestDecorator"
        print("Using temp directory", tempTestDir)

        try:

            functionCalls = 0

            @memoize(dir=tempTestDir, max_age=timedelta(seconds=0.2))
            def real_function(a: int, b: int) -> int:
                nonlocal functionCalls
                functionCalls += 1
                return a + b

            self.assertEqual(0, functionCalls)
            self.assertEqual(3, real_function(1, 2))  # computing new
            self.assertEqual(1, functionCalls)
            self.assertEqual(3, real_function(1, 2))  # reading from cache
            self.assertEqual(1, functionCalls)

            time.sleep(0.5)
            # computing new (old is out of date)
            self.assertEqual(3, real_function(1, 2))
            self.assertEqual(2, functionCalls)

            self.assertEqual(9, real_function(5, 4))
            self.assertEqual(3, functionCalls)

            self.assertEqual(5, real_function(a=2, b=3))
            self.assertEqual(4, functionCalls)
            self.assertEqual(5, real_function(a=2, b=3))
            self.assertEqual(4, functionCalls)

            # the order of the kw-arguments theoretically (very theoretically)
            # can affect the result of the function, so if the same data is
            # given in a different order, calculate again
            self.assertEqual(5, real_function(b=3, a=2))
            self.assertEqual(5, functionCalls)


        finally:

            if os.path.exists(tempTestDir):
                shutil.rmtree(tempTestDir)
