from problem_tree import *
import unittest

class TestProbTree(unittest.TestCase):

    def test1(self):
        print("Testing 'aaaa'...")
        self.assertEqual(get_best_token_set("aaaa"),
                    {'aaa': 1, 'aa': 2, 'a': 4})

    def test2(self):
        print("Testing 'abcdabc'...")
        self.assertEqual(get_best_token_set("abcdabc"),
                    {'abc': 2, 'ab': 2, 'a': 2, 'b': 2, 'c': 2, 'd': 1})

if __name__ == "__main__":
    unittest.main()