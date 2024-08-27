import unittest
from .SuffixNode import *


class SuffixTests(unittest.TestCase):
    def testTreeComposition(self):
        suffix_tree, _ = get_suffix_tree("abbabababba yogabbagabba",
                                           min_freq=2,
                                           delimiters={" ", "\n"},
                                           tree=None,
                                           test=True)
        token_set = set(suffix_tree.flat_tree_store.child_dict.keys())
        base_token_set = {'ab', 'o', 'babba', 'g', 'gabba', 'bab', 'ababba', 'b', ' ',
                          'abba', 'y', '\n', 'a', 'bba', 'babab', 'abab', 'ba', 'bababba'}
        print(token_set, base_token_set)
        self.assertEqual(token_set, base_token_set)
