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
        best_token_set = get_best_token_set("abcdabc")
        return best_token_set == {'abc': 2, 'ab': 2, 'a': 2, 'b': 2, 'c': 2, 'd': 1}\
                    or best_token_set == {'abc': 2, 'bc': 2, 'a': 2, 'b': 2, 'c': 2, 'd': 1}

    def test3(self):
        print("Testing '4hjk32789erfhefnbke32ir789df890342789efndjfsd78er'...")
        self.assertEqual(get_best_token_set("4hjk32789erfhefnbke32ir789df890342789efndjfsd78er"),
                    {'2789e': 2, '789e': 2, '89e': 2, 'fn': 2, '9e': 2, 'er': 2, '89': 4, '27': 2, '78': 4, '4': 2,
                     'h': 2, 'j': 2, 'k': 2, '3': 3, '2': 3, '7': 4, '8': 5, '9': 4, 'e': 5, 'r': 3, 'f': 5, 'n': 2,
                     'b': 1, 'i': 1, 'd': 3, '0': 1, 's': 1}
        )

    def test4(self):
        print("Testing 'she sells seashells by the sea shore'...")
        self.assertEqual(get_best_token_set("she sells seashells by the sea shore"),
                    {'she': 2, 'he': 3, 'ea': 2, 'ls': 2, 'sh': 3, 's': 8, 'h': 4, 'e': 7, ' ': 6, 'l': 4, 'a': 2,
                     'b': 1, 'y': 1, 't': 1, 'o': 1, 'r': 1}
        )

    def test5(self):
        print("Testing 'little pig, little pig'...")
        self.assertEqual(get_best_token_set("little pig, little pig"),
                    {' little lamb': 2, ' little lam': 2, ' little la': 2, ' little l': 2, ' little ': 2, 'little ': 2,
                     'little': 2, 'ittle ': 2, ' littl': 2, 'ttle ': 2, 'littl': 2, ' lamb': 2, 'tle ': 2, ' lit': 2,
                     'lamb': 2, 'litt': 2, 'e l': 2, 'amb': 2, 'lit': 2, 'itt': 2, 'le ': 2, 'li': 2, 'it': 2, 'tl': 2,
                     'am': 2, 'e ': 2, 'mb': 2, 'm': 3, 'a': 5, 'r': 1, 'y': 1, ' ': 6, 'h': 1, 'd': 1, 'l': 6, 'i': 2,
                     't': 4, 'e': 2, 'b': 2, ',': 1}
        )

if __name__ == "__main__":
    unittest.main()