import os
import sys
import re

from .FlatTreeStore import *

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import *
from utils.util import *


class SuffixNode:
    def __init__(self,
                 suffix=None,
                 token=None,
                 frequency=0,
                 parent=None,
                 keys_to_my_children=None,
                 flat_tree_store=None):
        self.suffix = suffix
        self.token = token
        self.frequency = frequency

        self.parent = parent

        # store tokens representing keys to children in the child_dict
        if keys_to_my_children is None:
            keys_to_my_children = set()
        self.keys_to_my_children = keys_to_my_children

        # store the child_dict separately
        if flat_tree_store is None:
            flat_tree_store = FlatTreeStore()
        self.flat_tree_store = flat_tree_store

    def __str__(self):
        return self.token

    def print_tree(self, indent=0):
        my_children = {self.flat_tree_store.child_dict[key] for key in self.keys_to_my_children}

        # Iterate over the child.suffixes (features) in the tree
        for child in my_children:
            print(' ' * indent + str(child.suffix) + ": " + str(child.frequency))
            # If the child is a SuffixNode, recursively print the subtree
            if isinstance(child, SuffixNode):
                child.print_tree(indent=indent + 4)
            else:
                print(' ' * (indent + 4) + "\"" + str(child.suffix) + "\": " + str(child.frequency))

    def set_token(self):
        if self.parent.token:
            self.token = self.parent.token + self.suffix
        else:
            self.token = self.suffix

    def split_edge(self, child, split_index, suffix):
        # Remove the previous/original child from current node's children
        self.keys_to_my_children.remove(child.token)
        del self.flat_tree_store.child_dict[child.token]

        # Calculate suffixes for the split
        old_suffix = child.suffix[split_index:]
        new_suffix = suffix[split_index:]

        # Create the split node with the matching part of the suffix
        split_node = SuffixNode(suffix=child.suffix[:split_index],
                                frequency=child.frequency,
                                parent=self,
                                flat_tree_store=self.flat_tree_store)
        split_node.set_token()

        # Add the split node to the current node's children
        self.keys_to_my_children.add(split_node.token)
        self.flat_tree_store.child_dict[split_node.token] = split_node

        # Create the old child (original suffix) under the split node
        old_child = SuffixNode(suffix=old_suffix,
                               frequency=child.frequency,
                               parent=split_node,
                               flat_tree_store=self.flat_tree_store,
                               keys_to_my_children=child.keys_to_my_children)
        old_child.set_token()

        # Create the new child (new suffix) under the split node
        new_child = SuffixNode(suffix=new_suffix,
                               frequency=1,
                               parent=split_node,
                               flat_tree_store=self.flat_tree_store)
        new_child.set_token()

        # Update children of the old split node
        for grandchild_key in child.keys_to_my_children:
            grandchild = self.flat_tree_store.child_dict[grandchild_key]
            grandchild.parent = old_child
            old_child.keys_to_my_children.add(grandchild_key)

        # Set up the split_node's children
        split_node.keys_to_my_children = {new_child.token, old_child.token}
        self.flat_tree_store.child_dict[new_child.token] = new_child
        self.flat_tree_store.child_dict[old_child.token] = old_child

    def add_suffix(self, suffix):
        if debugging and verbose["SuffixNode"]:
            print(f"Current suffix: '{suffix}'")
            print(f"Children: {self.keys_to_my_children}")

        # Iterate over each child to find the longest common prefix
        for child_token in self.keys_to_my_children:
            child = self.flat_tree_store.child_dict[child_token]

            # Find the longest common prefix
            min_len = min(len(suffix), len(child.suffix))
            i = 0
            while i < min_len and suffix[i] == child.suffix[i]:
                i += 1

            # If there is a common prefix
            if i > 0:
                if debugging and verbose["SuffixNode"]:
                    print(f"Child with shared suffix: '{child.token}'")
                # Update the frequency of the child node
                child.frequency += 1

                # If the common prefix matches the entire child suffix,
                #   and the new suffix would be non-empty,
                #   recurse on the remainder of the suffix
                if i == len(child.suffix) and len(suffix[i:]) > 0:
                    child.add_suffix(suffix[i:])
                # Otherwise, split the edge
                elif i < len(suffix):
                    self.split_edge(child, i, suffix)

                return

        # No matching suffix, create a new child
        if debugging and verbose["SuffixNode"]:
            print("No partial or complete suffix match detected, creating new child")
        new_child = SuffixNode(suffix=suffix,
                               frequency=1,
                               parent=self,
                               flat_tree_store=self.flat_tree_store)
        new_child.set_token()

        # Add the new child to the current node's children
        self.keys_to_my_children.add(new_child.token)
        self.flat_tree_store.child_dict[new_child.token] = new_child

        return

    def merge_trees(self, other):
        other_tree = other.flat_tree_store.child_dict

        shared_tokens = set(self.keys_to_my_children).intersection(set(other.keys_to_my_children))
        other_unique_tokens = set(other.keys_to_my_children).difference(set(self.keys_to_my_children))

        # combine children held in common between both suffix trees
        for token in shared_tokens:
            my_child = self.flat_tree_store.child_dict[token]
            other_child = other_tree[token]

            # combine the childrens' frequencies
            self.flat_tree_store.child_dict[token].frequency += other_child.frequency

            # recursively merge any grandchildren that might be held in common
            self.flat_tree_store.child_dict[token].merge_trees(other_child)

        # add the other tree's unique children to this tree
        for token in other_unique_tokens:
            other_child = other_tree[token]

            other_child.parent = self
            self.flat_tree_store.child_dict[other_child.token] = other_child

    def find_split_point(text, delimiters):
        if not delimiters:
            return len(text) // 2

        # Find all matches for the delimiter regex
        matches = list(re.finditer(delimiters, text))

        if not matches:
            return None

        # Find the match closest to the middle of the string
        mid = len(text) // 2
        best_match = min(matches, key=lambda m: abs(m.start() - mid))

        return best_match.start()

    # add the delimiter frequencies back into the suffix tree's storage
    def add_delimiters_to_tree(self, text="", delimiters=None):
        # # WARNING: THIS DEFEATS THE PURPOSE OF THE PARALLELIZATION, BRINGS T(n) TO O(n)
        # #   FIX BY INCLUDING DELIMITER COUNTING IN SUBTREES
        # delimiter_counts = count_occurrences(text, delimiters)
        delimiter_counts = {delimiter: 1 for delimiter in delimiters}

        self.keys_to_my_children.update(set(delimiter_counts.keys()))
        self.flat_tree_store.child_dict.update({
            key: SuffixNode(suffix=key,
                            token=key,
                            frequency=value,
                            parent=self,
                            flat_tree_store=self.flat_tree_store) \
            for key, value in delimiter_counts.items()
        })

    def base_build_tree(self, text="", delimiters=None, delimiter_regex=r"\n"):
        # split the text into blocks, where each block is an independent clause
        clauses = re.split(delimiter_regex, text)
        # print(set(clauses))

        if debugging and verbose["SuffixNode"]:
            print("Initial suffix tree (just alphabet):")
            self.print_tree()

        for string in clauses:
            if debugging:
                print(f"Building suffix tree for '{string}'...")

            # loop through the string, starting with the last character
            for i in range(0, len(string)):
                suffix = string[len(string) - i - 1:]

                # add the suffix to the tree
                self.add_suffix(suffix)

                if debugging and verbose["SuffixNode"]:
                    self.print_tree()
                    print()
                    print()

        self.add_delimiters_to_tree(text=text,
                                    delimiters=delimiters)

    def parallelized_build_tree(text, delimiters=None, delimiter_regex=r"\n"):
        if len(text) == 0:
            return SuffixNode()

        # Find the best split point using delimiters
        split_point = SuffixNode.find_split_point(text, delimiter_regex)

        if debugging:
            print(f"Split text: {[text[:split_point], text[split_point:]]}")

        # if the text has been split down to the size of a word
        if split_point == None or split_point == 0 or split_point == len(text) - 1:
            if debugging and verbose["SuffixNode"]:
                print("Leaf detected...")
            root = SuffixNode()

            if debugging and verbose["SuffixNode"]:
                print("Initial suffix tree (just alphabet):")
                root.print_tree()

            if debugging:
                print(f"Building suffix tree for '{text}'...")

            # loop through the string, starting with the last character
            for i in range(0, len(text)):
                suffix = text[len(text) - i - 1:]

                # add the suffix to the tree
                root.add_suffix(suffix)

                if debugging and verbose["SuffixNode"]:
                    root.print_tree()
                    print()

            return root

        left_half = text[:split_point]
        right_half = text[split_point + 1:]

        print(left_half)

        left_tree = SuffixNode.parallelized_build_tree(left_half,
                                                       delimiters=delimiters,
                                                       delimiter_regex=delimiter_regex)
        right_tree = SuffixNode.parallelized_build_tree(right_half,
                                                        delimiters=delimiters,
                                                        delimiter_regex=delimiter_regex)

        left_tree.merge_trees(right_tree)

        left_tree.add_delimiters_to_tree(text=text,
                                         delimiters=delimiters)

        print()

        return left_tree

    def prune_tree(self, threshold=2):
        # If the node has no children (ie it's a leaf), return
        if not self.keys_to_my_children:
            # print("no children")
            return

        children_to_kill = set()
        # Recursively prune the tree
        for child_token in self.keys_to_my_children:
            child = self.flat_tree_store.child_dict[child_token]

            if isinstance(child, SuffixNode):
                # if the child is above the threshold or it's a single character token node
                if child.frequency >= threshold or child.parent is None:
                    # print("not removed")
                    self.flat_tree_store.child_dict[child_token].prune_tree(threshold)
                else:
                    # print("removed")
                    children_to_kill.add(child_token)

        for child_token in children_to_kill:
            # if the token's frequency falls below the threshold, prune it
            self.keys_to_my_children.remove(child_token)
            del self.flat_tree_store.child_dict[child_token]

    # set all the suffix tree nodes' token properties
    # return an aggregated set of all the tokens
    def get_tokens(self, prev_token=""):
        tokens = set(self \
                     .flat_tree_store \
                     .child_dict \
                     .keys())

        return tokens


def get_suffix_tree(text,
                    threshold,
                    delimiters=None,
                    tree=None,
                    parallelize=True):
    # use the tree option in case a previous tree is to be pruned further
    suffix_tree = tree
    if suffix_tree is None:
        print("Building modified suffix tree...")

        # suffix_tree = SuffixNode(children = {SuffixNode(suffix=unique_char) for unique_char in set(text)})

        delimiter_regex = compile_regex(delimiters)

        if parallelize:
            print("Running SuffixNode.parallelized_build_tree()...")
            suffix_tree = SuffixNode.parallelized_build_tree(text,
                                                             delimiters=delimiters,
                                                             delimiter_regex=delimiter_regex)
            # set the root of the flat tree store to the initial SuffixNode pointing to it
            suffix_tree.flat_tree_store.root = suffix_tree

        else:
            print("Running suffix_tree.base_build_tree()...")
            # create a store for the tree nodes
            flat_tree_store = FlatTreeStore(child_dict={
                letter: SuffixNode(suffix=letter, token=letter) for letter in set(text)
            })

            # point all the internal tree stores back at the main one
            for key in flat_tree_store.child_dict.keys():
                flat_tree_store.child_dict[key].flat_tree_store = flat_tree_store

            suffix_tree = SuffixNode(flat_tree_store=flat_tree_store,
                                     keys_to_my_children=set(flat_tree_store.child_dict.keys()))
            # set the root of the flat tree store to the initial SuffixNode pointing to it
            suffix_tree.flat_tree_store.root = suffix_tree

            suffix_tree.base_build_tree(text,
                                        delimiters=delimiters,
                                        delimiter_regex=delimiter_regex)

        if debugging and verbose["SuffixNode"]:
            suffix_tree.print_tree()

    print("Pruning modified suffix tree...")
    suffix_tree.prune_tree(threshold=threshold)
    if debugging:
        suffix_tree.print_tree()

    print("Getting token set...")
    tokens = suffix_tree.get_tokens()
    if debugging:
        print(tokens)

    return suffix_tree, tokens
