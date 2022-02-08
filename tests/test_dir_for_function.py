# SPDX-FileCopyrightText: (c) 2021 Artёm IG <github.com/rtmigo>
# SPDX-License-Identifier: MIT

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from pickledir import PickleDir

from filememo._dir_for_func import find_dir_for_method, PathCandidate


def func_a():
    pass


def func_b():
    pass


class TestFindDir(unittest.TestCase):

    def test_test_id_file_not_managed_by_pickledir(self):
        self.assertFalse(
            PickleDir._is_data_basename(PathCandidate.func_id_basename))

    def test_hash_collision(self):
        def bad_hash_func(_):
            return "123"

        with TemporaryDirectory() as td:
            a1 = find_dir_for_method(parent=Path(td), method=func_a,
                                     hash_func=bad_hash_func)
            b1 = find_dir_for_method(parent=Path(td), method=func_b,
                                     hash_func=bad_hash_func)
            a2 = find_dir_for_method(parent=Path(td), method=func_a,
                                     hash_func=bad_hash_func)

            # since we got hash collision, the directory names
            # must have suffixes other than "_1"
            self.assertTrue(a1.name.endswith("_0"))
            self.assertTrue(b1.name.endswith("_1"))

            self.assertEqual(a1, a2)
            self.assertNotEqual(a1, b1)

    def test_hashes_different(self):
        with TemporaryDirectory() as td:
            a1 = find_dir_for_method(parent=Path(td), method=func_a)
            b1 = find_dir_for_method(parent=Path(td), method=func_b)
            a2 = find_dir_for_method(parent=Path(td), method=func_a)

            self.assertEqual(a1, a2)
            self.assertNotEqual(a1, b1)

            # the following lines may fail only if MD5 hashes are the same
            # (which is highly unlikely)
            self.assertTrue(a1.name.endswith("_0"))
            self.assertTrue(b1.name.endswith("_0"))
