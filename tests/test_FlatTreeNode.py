import unittest

from tokenBN.SuffixNode import SuffixNode

class TestFlatTreeNode(unittest.TestCase):
    def setUp(self):
        self.test_text = "abbabababba yogabbagabba"
        self.delimiters = {" ", "\n"}
        self.threshold = 2

    def test_tokenize(self):
        actual_tokenization = ['abba', 'babab', 'ba', ' ', 'y', 'o', 'gabba', 'gabba']

        print("Testing tokenization...")
        suffix_tree = SuffixNode.from_text(
            text=self.test_text,
            threshold=self.threshold,
            delimiters=self.delimiters
        )
        tokenization = suffix_tree.flat_tree_store.tokenize(self.test_text, len(self.test_text) - 1)
        self.assertEqual(tokenization, actual_tokenization)