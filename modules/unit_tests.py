import unittest
from .SuffixNode import *


class SuffixTests(unittest.TestCase):
    def testTreeComposition(self):
        suffix_tree, _ = get_suffix_tree("abbabababba",
                                           min_freq=2,
                                           delimiters={" ", "\n"},
                                           tree=None,
                                           test=True)
        token_set = set(suffix_tree.flat_tree_store.child_dict.keys())
        base_token_set = {'bba', '', 'abababba', 'b', 'abba', 'ba', 'baa'}
        print(token_set, base_token_set)
        self.assertEqual(token_set, base_token_set)
