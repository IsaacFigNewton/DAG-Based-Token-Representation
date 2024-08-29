import unittest
import urllib.request as url

from modules.SuffixNode import *
from modules.CompositionDAGNode import *
from utils.util import *


class SuffixTests(unittest.TestCase):
    def setUp(self):
        self.test_text = "abbabababba yogabbagabba"
        self.delimiters = {" ", "\n"}
        self.threshold = 2

    def test_add_suffix(self):
        # test adding plain suffixes, raw, no lube
        root = SuffixNode()
        root.flat_tree_store.root = root
        root.add_suffix("abc")
        root.add_suffix("def")
        tokens = root.get_tokens()
        actual_tokens = {"a", "d", "abc", "def"}
        self.assertEqual(tokens, actual_tokens)

        root = SuffixNode()
        root.flat_tree_store.root = root

        # Test adding a single suffix
        root.add_suffix("test")
        self.assertIn("t", root.keys_to_my_children)
        self.assertIn("t", root.flat_tree_store.child_dict)
        child = root.flat_tree_store.child_dict["t"]
        self.assertEqual(child.suffix, "t")
        self.assertEqual(child.token, "t")
        self.assertEqual(child.frequency, 1)

        # Test adding the same suffix again
        root.add_suffix("test")
        self.assertEqual(child.frequency, 2)

        # Test adding a suffix with a common prefix
        root.add_suffix("team")
        self.assertIn("te", child.flat_tree_store.child_dict)
        grandchild = child.flat_tree_store.child_dict["te"]
        self.assertEqual(grandchild.suffix, "e")
        self.assertEqual(grandchild.token, "te")

        # Test adding a completely new suffix
        root.add_suffix("xyz")
        self.assertIn("x", root.keys_to_my_children)
        self.assertIn("x", root.flat_tree_store.child_dict)

    def test_add_all_suffixes(self):
        root = SuffixNode()
        root.flat_tree_store.root = root
        root.add_all_suffixes("abc")
        root.add_all_suffixes("def")

        tokens = root.get_tokens()
        actual_tokens = {"a", "b", "c", "d", "e", "f", "bc", "ef", "abc", "def"}
        self.assertEqual(tokens, actual_tokens)

    def test_split_edge(self):
        tests = ["test", "teat"]
        root = SuffixNode()
        root.flat_tree_store.root = root
        root.add_all_suffixes("test")
        root.add_all_suffixes("teat")

        # Check the structure after splitting
        for character in set("testteat"):
            self.assertIn(character, root.keys_to_my_children)
            self.assertIn(character, root.flat_tree_store.child_dict)

        child = root.flat_tree_store.child_dict["t"]
        self.assertIn("te", child.keys_to_my_children)
        self.assertIn("te", child.flat_tree_store.child_dict)

        grandchild = child.flat_tree_store.child_dict["te"]
        self.assertIn("test", grandchild.keys_to_my_children)
        self.assertIn("teat", grandchild.keys_to_my_children)
        self.assertIn("test", grandchild.flat_tree_store.child_dict)
        self.assertIn("teat", grandchild.flat_tree_store.child_dict)

        great_grandchildren = {grandchild.flat_tree_store.child_dict[token] for token in tests}
        # Check the frequencies
        self.assertEqual(child.frequency, 4)
        self.assertEqual(grandchild.frequency, 2)
        for node in great_grandchildren:
            self.assertEqual(node.frequency, 1)

    def test_prune_tree(self):
        root = SuffixNode()
        root.flat_tree_store.root = root
        root.add_all_suffixes("abc")
        root.add_all_suffixes("abcd")

        root = root.prune_tree(threshold=2)

        # Check pruned structure
        for character in set("abcd"):
            self.assertIn(character, root.keys_to_my_children)
            self.assertIn(character, root.flat_tree_store.child_dict)

        child = root.flat_tree_store.child_dict["a"]
        self.assertIn("abc", child.keys_to_my_children)

        child = root.flat_tree_store.child_dict["c"]
        self.assertNotIn("d", child.keys_to_my_children)

        # Check frequencies after pruning
        self.assertEqual(root.flat_tree_store.child_dict["d"].frequency, 1)
        for child_token in set("abc"):
            self.assertEqual(root.flat_tree_store.child_dict[child_token].frequency, 2)

    # repeat, I know, but it should help with debugging
    def test_get_tokens(self):
        root = SuffixNode()
        root.flat_tree_store.root = root
        root.add_suffix("abc")
        root.add_suffix("def")

        tokens = root.get_tokens()
        actual_tokens = {"a", "d", "abc", "def"}
        self.assertEqual(tokens, actual_tokens)

    def test_add_delimiters_to_tree(self):
        root = SuffixNode()
        root.flat_tree_store.root = root
        root.add_delimiters_to_tree(delimiters=self.delimiters)

        self.assertIn(" ", root.keys_to_my_children)
        self.assertIn("\n", root.keys_to_my_children)
        self.assertIn(" ", root.flat_tree_store.child_dict)
        self.assertIn("\n", root.flat_tree_store.child_dict)

        # Check delimiter nodes
        space_node = root.flat_tree_store.child_dict[" "]
        self.assertEqual(space_node.suffix, " ")
        self.assertEqual(space_node.token, " ")
        self.assertEqual(space_node.frequency, 1)

    def check_built_tree(self, tree, text):
        for character in set(text).difference(delimiters):
            self.assertIn(character, tree.keys_to_my_children)
            self.assertIn(character, tree.flat_tree_store.child_dict)

        # Check alphabet token frequencies
        self.assertEqual(tree.flat_tree_store.child_dict["a"].frequency, 9)
        self.assertEqual(tree.flat_tree_store.child_dict["b"].frequency, 10)
        self.assertEqual(tree.flat_tree_store.child_dict["y"].frequency, 1)
        self.assertEqual(tree.flat_tree_store.child_dict["o"].frequency, 1)
        self.assertEqual(tree.flat_tree_store.child_dict["g"].frequency, 2)

    def test_build_trees(self):
        tree = SuffixNode.build_tree(text=self.test_text, delimiter_regex=compile_regex(self.delimiters))

        self.assertIsInstance(tree, SuffixNode)
        self.check_built_tree(tree, self.test_text)

    def test_get_suffix_tree(self):
        base_token_set = {'gabba', 'o', 'babab', 'ba', 'b', 'abab', 'a',
                          'y', 'ab', 'abba', ' ', 'bab', '\n', 'g', 'bba'}

        print("Testing base approach...")
        suffix_tree, _ = get_suffix_tree(text=self.test_text,
                                         threshold=self.threshold,
                                         delimiters=self.delimiters)
        token_set = set(suffix_tree.flat_tree_store.child_dict.keys())
        self.assertEqual(token_set, base_token_set)


class FlatTreeNodeTests(unittest.TestCase):
    def setUp(self):
        self.test_text = "abbabababba yogabbagabba"
        self.delimiters = {" ", "\n"}
        self.threshold = 2

    def test_tokenize(self):
        actual_tokenization = ['abba', 'babab', 'ba', ' ', 'y', 'o', 'gabba', 'gabba']

        print("Testing tokenization...")
        suffix_tree, _ = get_suffix_tree(text=self.test_text,
                                         threshold=self.threshold,
                                         delimiters=self.delimiters)
        tokenization = suffix_tree.flat_tree_store.tokenize(self.test_text, len(self.test_text) - 1)
        self.assertEqual(tokenization, actual_tokenization)


class CompositionDAGNodeTests(unittest.TestCase):
    def setUp(self):
        self.test_text = "abbabababba yogabbagabba"
        self.delimiters = {" ", "\n"}
        self.threshold = 2
        self.suffix_tree, _ = get_suffix_tree(text=self.test_text,
                                              threshold=self.threshold,
                                              delimiters=self.delimiters)

    def test_add_edge(self):
        pass

    def test_build_subgraph(self):
        pass

    def test_suffix_tree_to_dag(self):
        pass

    def test_dag_to_file(self):
        test_url = "https://courses.cs.washington.edu/courses/cse163/20wi/files/lectures/L04/bee-movie.txt"
        with url.urlopen(test_url) as f:
            text = f.read().decode('utf-8')
        self.test_text = text
        self.delimiters = {"\n"}
        self.threshold = 50
        self.suffix_tree, _ = get_suffix_tree(text=self.test_text,
                                              threshold=self.threshold,
                                              delimiters=self.delimiters)

        dag = CompositionDAGNode()
        # start_time = time.time()
        dag.suffix_tree_to_dag(self.suffix_tree)

        dag.export_dag("bee_movie.csv")


if __name__ == "__main__":
    unittest.main()
