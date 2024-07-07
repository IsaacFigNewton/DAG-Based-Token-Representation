from problem_tree import *
import unittest

class TestProbTree(unittest.TestCase):

    def test1(self):
        print("Testing 'aaaa'...")
        self.assertEqual(get_best_token_set("aaaa"),
                    {'aa': 2, 'a': 4}
        )

    def test2(self):
        print("Testing 'abcdabc'...")
        self.assertEqual(get_best_token_set("abcdabc"),
                    {'abc': 2, 'ab': 2, 'a': 2, 'b': 2, 'c': 2, 'd': 1}
        )

    def test3(self):
        print("Testing 'she sells seashells by the sea shore'...")
        self.assertEqual(get_best_token_set("she sells seashells by the sea shore"),
                    {'she': 2, 'he': 3, 'ea': 2, 'ls': 2, 'sh': 3, 's': 8, 'h': 4, 'e': 7, ' ': 6, 'l': 4, 'a': 2,
                     'b': 1, 'y': 1, 't': 1, 'o': 1, 'r': 1}
        )

    def test4(self):
        print("Testing 'mary had a little lamb, little lamb'...")
        self.assertEqual(get_best_token_set("mary had a little lamb, little lamb, little lamb"),
                    {' little lamb': 2, ' little lam': 2, ' little la': 2, ' little l': 2, ' little ': 2, 'little ': 2,
                     'little': 2, 'ittle ': 2, ' littl': 2, 'ttle ': 2, 'littl': 2, ' lamb': 2, 'tle ': 2, ' lit': 2,
                     'lamb': 2, 'litt': 2, 'e l': 2, 'amb': 2, 'lit': 2, 'itt': 2, 'le ': 2, 'li': 2, 'it': 2, 'tl': 2,
                     'am': 2, 'e ': 2, 'mb': 2, 'm': 3, 'a': 5, 'r': 1, 'y': 1, ' ': 6, 'h': 1, 'd': 1, 'l': 6, 'i': 2,
                     't': 4, 'e': 2, 'b': 2, ',': 1}
        )

if __name__ == "__main__":
    unittest.main()