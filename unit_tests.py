import unittest
from modules.SuffixNode import *
from modules.CompositionDAGNode import *


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

    def test_merge_trees(self):
        tree1 = SuffixNode()
        tree1.flat_tree_store.root = tree1
        tree1.add_all_suffixes("abc")
        tree1.add_all_suffixes("def")

        tree2 = SuffixNode()
        tree2.flat_tree_store.root = tree2
        tree2.add_all_suffixes("abc")
        tree2.add_all_suffixes("ghi")

        tree1.merge_trees(tree2)

        # Check merged structure
        for character in set("abcdefghi"):
            self.assertIn(character, tree1.keys_to_my_children)
            self.assertIn(character, tree1.flat_tree_store.child_dict)

        # Check frequencies
        for character in set("abc"):
            self.assertEqual(tree1.flat_tree_store.child_dict[character].frequency, 2)
        for character in set("defghi"):
            self.assertEqual(tree1.flat_tree_store.child_dict[character].frequency, 1)

    def test_prune_tree(self):
        root = SuffixNode()
        root.flat_tree_store.root = root
        root.add_all_suffixes("abc")
        root.add_all_suffixes("abcd")

        root.print_tree()
        root, _ = root.prune_tree(threshold=2)

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

    def test_find_split_point(self):
        text = "Hello world! This is a test."
        test_delimiters = r"[.!?]"
        split_point = SuffixNode.find_split_point(text, test_delimiters)
        self.assertEqual(split_point, 11)  # Index of '!'

        # Test with no delimiters
        text = "abcdefghijklmnop"
        split_point = SuffixNode.find_split_point(text, "")
        self.assertEqual(split_point, 8)  # Middle of the string

    def test_add_delimiters_to_tree(self):
        root = SuffixNode()
        root.flat_tree_store.root = root
        root.add_delimiters_to_tree(delimiters={" ", "\n"})

        self.assertIn(" ", root.keys_to_my_children)
        self.assertIn("\n", root.keys_to_my_children)
        self.assertIn(" ", root.flat_tree_store.child_dict)
        self.assertIn("\n", root.flat_tree_store.child_dict)

        # Check delimiter nodes
        space_node = root.flat_tree_store.child_dict[" "]
        self.assertEqual(space_node.suffix, " ")
        self.assertEqual(space_node.token, " ")
        self.assertEqual(space_node.frequency, 1)

    def test_parallelized_build_tree(self):
        text = "abcdefabcdef"
        tree = SuffixNode.parallelized_build_tree(text)

        self.assertIsInstance(tree, SuffixNode)
        self.assertIn("a", tree.keys_to_my_children)
        self.assertIn("d", tree.keys_to_my_children)
        self.assertIn("a", tree.flat_tree_store.child_dict)
        self.assertIn("d", tree.flat_tree_store.child_dict)

        # Check some frequencies
        self.assertEqual(tree.flat_tree_store.child_dict["a"].frequency, 2)
        self.assertEqual(tree.flat_tree_store.child_dict["d"].frequency, 2)


    def test_get_suffix_tree(self):
        base_token_set = {'gabba', 'o', 'babab', 'ba', 'b', 'abab', 'a', 'y', 'ab', 'abba', ' ', 'bab', '\n', 'g',
                          'bba'}

        print("Testing base approach...")
        series_suffix_tree, _ = get_suffix_tree(text=self.test_text,
                                                threshold=self.threshold,
                                                delimiters=self.delimiters,
                                                parallelize=False)
        token_set = set(series_suffix_tree.flat_tree_store.child_dict.keys())
        self.assertEqual(token_set, base_token_set)

        print("\nTesting parallelized approach...")
        parallel_suffix_tree, _ = get_suffix_tree(text=self.test_text, threshold=self.threshold,
                                                  delimiters=self.delimiters,
                                                  parallelize=True)
        token_set = set(parallel_suffix_tree.flat_tree_store.child_dict.keys())
        self.assertEqual(token_set, base_token_set)


if __name__ == "__main__":
    unittest.main()
