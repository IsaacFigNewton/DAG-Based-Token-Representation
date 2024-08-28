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
        return f"SuffixNode: {self.token}"

    def print_tree(self, indent=0):
        my_children = {self.flat_tree_store.child_dict[key] for key in self.keys_to_my_children}

        # Iterate over the child.suffixes (features) in the tree
        for child in my_children:
            if any(debugging_verbosity["SuffixNode"]) > 0:
                print(f"{' ' * indent} '{child.suffix}', '{child.token}', {child.frequency}")
            else:
                print(f"{' ' * indent} '{child.suffix}': {child.frequency}")
            # If the child is a SuffixNode, recursively print the subtree
            if isinstance(child, SuffixNode):
                child.print_tree(indent=indent + 4)
            else:
                if any(debugging_verbosity["SuffixNode"]) > 0:
                    print(f"{' ' * (indent + 4)} '{child.suffix}', '{child.token}', {child.frequency}")
                else:
                    print(f"{' ' * (indent + 4)} '{child.suffix}': {child.frequency}")

    def set_token(self):
        if self.parent.token:
            self.token = self.parent.token + self.suffix
        else:
            self.token = self.suffix

    def add_child(self, suffix):
        if debugging_verbosity["SuffixNode"]["general"] > 1:
            print(f"Creating a new child with suffix '{suffix}'")

        child = SuffixNode(suffix=suffix,
                           token=suffix,
                           frequency=1,
                           parent=self,
                           flat_tree_store=self.flat_tree_store)

        child.set_token()

        # Add the new child to the current node's children
        self.keys_to_my_children.add(child.token)
        self.flat_tree_store.child_dict[child.token] = child

    def create_split_nodes(self, child, old_suffix, new_suffix, split_node):
        # Create the old child (original suffix) under the split node
        old_child = SuffixNode(suffix=old_suffix,
                               frequency=child.frequency - 1,
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

        return old_child, new_child

    def split_edge(self, child, split_index, suffix):
        if debugging_verbosity["SuffixNode"]["general"] > 1:
            print(f"Splitting on {child.token}")

        # Remove the previous/original child from current node's children
        try:
            self.keys_to_my_children.remove(child.token)
        except:
            raise KeyError(
                f"Couldn't remove '{child.token}' from '{self.token}''s children: {self.keys_to_my_children}")

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

        old_child, new_child = self.create_split_nodes(child, old_suffix, new_suffix, split_node)

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
        if debugging_verbosity["SuffixNode"]["general"] > 1:
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
                if debugging_verbosity["SuffixNode"]["general"] > 1:
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

        # if it's an unseen character
        #   (like in the case of a divide-and-conquer approach)
        if suffix[0] not in self.flat_tree_store.root.keys_to_my_children:
            # No matching suffix, create a new child
            if debugging_verbosity["SuffixNode"]["general"] > 1:
                print("Unrecognized character, adding to alphabet...")

            # add the new character to the alphabet child set

            self.flat_tree_store.child_dict[suffix[0]] = SuffixNode(
                suffix=suffix[0],
                token=suffix[0],
                frequency=1,
                parent=self.flat_tree_store.root,
                flat_tree_store=self.flat_tree_store
            )
            self \
                .flat_tree_store \
                .root \
                .keys_to_my_children \
                .add(suffix[0])

            # if there's still suffix left, add a child to the current node,
            #   consisting of the remainder
            if len(suffix) > 1:
                child = self.flat_tree_store.child_dict[suffix[0]]
                child.add_child(suffix[1:])

                if debugging_verbosity["SuffixNode"]["general"] > 1:
                    print(self.get_tokens())

        else:
            # No matching suffix, create a new child
            self.add_child(suffix)

            if debugging_verbosity["SuffixNode"]["general"] > 1:
                print(self.get_tokens())

        return

    def add_all_suffixes(self, word):
        # loop through the word, starting with the last character
        for i in range(0, len(word)):
            suffix = word[len(word) - i - 1:]

            # add the suffix to the tree
            self.add_suffix(suffix)

    def merge_trees(self, other, indent=0):
        # combine the roots' frequencies
        self.frequency += other.frequency

        other_tree = other.flat_tree_store.child_dict
        shared_tokens = set(self.keys_to_my_children).intersection(set(other.keys_to_my_children))
        other_unique_tokens = set(other.keys_to_my_children).difference(set(self.keys_to_my_children))

        if debugging_verbosity["SuffixNode"]["parallel"] > 1:
            print(f"{' ' * indent}Shared tokens for subtrees '{self.token}' and '{other.token}': {shared_tokens}")
            print(f"{' ' * indent}Tokens unique to '{other.token}': {other_unique_tokens}")

        # combine children held in common between both suffix trees
        for token in shared_tokens:
            my_child = self.flat_tree_store.child_dict[token]
            other_child = other_tree[token]
            # recursively merge any grandchildren that might be held in common
            my_child.merge_trees(other_child, indent + 4)
            self.flat_tree_store.child_dict[token] = my_child

        if debugging_verbosity["SuffixNode"]["parallel"] > 1:
            print(
                f"{' ' * indent}Tokens unique to '{other.token}' before combining with '{self.token}': {other_unique_tokens}")
            print(other_tree)
        # recursively add all the other tree's unique subtrees to this one
        self.merge_unique_subtrees(self, other_tree, other_unique_tokens)

    def merge_unique_subtrees(self, parent, other_tree_dict, other_unique_tokens):
        if not isinstance(other_tree_dict, dict):
            raise TypeError(f"other_tree is not a dictionary: {other_tree_dict}")

        # add the other tree's unique children to this tree
        for token in other_unique_tokens:
            other_child = other_tree_dict[token]

            # the adoptive parent may be different from self,
            #    which is especially true for unique subtrees starting at the alphabet level
            other_child.parent = parent
            parent.keys_to_my_children.add(other_child.token)
            # self.flat_tree_store.child_dict[other_child.token] = other_child

        # add all children to the main tree store
        temp = {token: grandchild for token, grandchild in other_tree_dict.items() if token in other_unique_tokens}
        if debugging_verbosity["SuffixNode"]["parallel"] > 1:
            print(f"All SuffixNodes to be added to main tree: {temp}")
        self.flat_tree_store.child_dict.update(temp)

        if debugging_verbosity["SuffixNode"]["parallel"] > 1:
            print(f"Merging grandchildren: {other_tree_dict.keys()}")
            print(other_tree_dict)
            print()
        # add the grandchildren to the main tree
        for token, grandchild in temp.items():
            self.merge_unique_subtrees(grandchild, other_tree_dict, grandchild.keys_to_my_children)

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
                            frequency=1,
                            parent=self,
                            flat_tree_store=self.flat_tree_store)
            for key in delimiter_counts.keys()
        })

    def base_build_tree(self, text="", delimiter_regex=r"\n"):
        # split the text into blocks, where each block is an independent clause
        clauses = re.split(delimiter_regex, text)
        # print(set(clauses))

        if debugging_verbosity["SuffixNode"]["series"] > 1:
            print("Initial suffix tree (just alphabet):")
            self.print_tree()

        for string in clauses:
            if debugging_verbosity["SuffixNode"]["series"] > 0:
                print(f"Building suffix tree for '{string}'...")

            self.add_all_suffixes(string)

        if debugging_verbosity["SuffixNode"]["series"] > 1:
            print(self.get_tokens())

    def parallelized_build_tree(text, delimiters=None, delimiter_regex=r"\n"):
        if len(text) == 0:
            return SuffixNode()

        # Find the best split point using delimiters
        split_point = SuffixNode.find_split_point(text, delimiter_regex)

        if debugging_verbosity["SuffixNode"]["parallel"] > 0:
            print(f"Split text: {[text[:split_point], text[split_point:]]}")

        # if the text has been split down to the size of a word
        if split_point == None or split_point == 0 or split_point == len(text) - 1:
            if debugging_verbosity["SuffixNode"]["parallel"] > 1:
                print("Leaf detected...")
            root = SuffixNode()
            # set the root of the flat tree store to the initial SuffixNode pointing to it
            root.flat_tree_store.root = root

            if debugging_verbosity["SuffixNode"]["parallel"] > 0:
                print(f"Building suffix tree for '{text}'...")

            root.add_all_suffixes(text)

            return root

        left_half = text[:split_point]
        right_half = text[split_point + 1:]

        if debugging_verbosity["SuffixNode"]["parallel"] > 0:
            print(f"left_half: {left_half}")
            print(f"left_half: {right_half}")

        left_tree = SuffixNode.parallelized_build_tree(left_half,
                                                       delimiters=delimiters,
                                                       delimiter_regex=delimiter_regex)
        right_tree = SuffixNode.parallelized_build_tree(right_half,
                                                        delimiters=delimiters,
                                                        delimiter_regex=delimiter_regex)

        left_tree.merge_trees(right_tree, 0)

        if debugging_verbosity["SuffixNode"]["parallel"] > 1:
            print()

        return left_tree

    def prune_tree(self, threshold=2, indent=0):
        # If the node has no children (ie it's a leaf), return
        if not self.keys_to_my_children:
            if debugging_verbosity["SuffixNode"]["pruning"] > 1:
                print(f"{' ' * (indent + 4)}No children for {self.token}")
            return self, set()

        children_to_kill = set()
        dead_children = set()
        # Recursively prune the tree
        for child_token in self.keys_to_my_children:
            child = self.flat_tree_store.child_dict[child_token]

            if debugging_verbosity["SuffixNode"]["pruning"] > 1:
                print(f"{' ' * indent}{child.suffix}:\tToken:\t{child.token}")
                if child.parent is not None:
                    print(f"{' ' * indent}\tParent:\t{child.parent.token}")
                else:
                    print(f"{' ' * indent}\tChild is orphan")

                print(f"{' ' * indent}\tChildren:")

            if isinstance(child, SuffixNode):
                # if the child is above the threshold or it's a single character token node
                if child.parent is None or ((child.frequency >= threshold
                                             or child.parent.token is None)
                                            and (child.token in child.parent.keys_to_my_children)):
                    # print("not removed")
                    child, zombie_children = child.prune_tree(threshold, indent=4)
                    self.flat_tree_store.child_dict[child_token] = child
                    dead_children = dead_children.union(zombie_children)
                else:
                    # print("removed")
                    children_to_kill.add(child_token)

        # remove zombie children from the token set at this level
        #   this is really only an issue if the parallelized approach is used
        for child_token in dead_children:
            if child_token in self.flat_tree_store.child_dict.keys():
                del self.flat_tree_store.child_dict[child_token]

        for child_token in children_to_kill:
            # if the token's frequency falls below the threshold, prune it
            self.keys_to_my_children.remove(child_token)
            del self.flat_tree_store.child_dict[child_token]
            dead_children.add(child_token)

        if debugging_verbosity["SuffixNode"]["pruning"] > 1:
            print(self.get_tokens())

        return self, dead_children

    # return an aggregated set of all the tokens
    def get_tokens(self):
        return set(self
                   .flat_tree_store
                   .child_dict
                   .keys())


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

            suffix_tree.base_build_tree(text, delimiter_regex=delimiter_regex)

        if debugging_verbosity["SuffixNode"]["general"] > 1:
            suffix_tree.print_tree()

    print("Pruning modified suffix tree...")
    suffix_tree.prune_tree(threshold=threshold)
    print(suffix_tree.get_tokens())
    suffix_tree.add_delimiters_to_tree(delimiters=delimiters)

    if debugging_verbosity["SuffixNode"]["pruning"] > 0:
        suffix_tree.print_tree()

    if debugging_verbosity["SuffixNode"]["general"] > 0:
        print("Getting token set...")
    tokens = suffix_tree.get_tokens()

    return suffix_tree, tokens