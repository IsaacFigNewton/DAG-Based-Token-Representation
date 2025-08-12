import re
from typing import List

from tokenBN.config import DEBUG_VERBOSITY

from tokenBN.FlatTreeStore import FlatTreeStore
from tokenBN.utils.util import *


class SuffixNode:
    def __init__(self,
            suffix=None,
            token=None,
            frequency:int=0,
            parent=None,
            keys_to_my_children=None,
            flat_tree_store=None,
            delimiters: Set[str] = set(),
            threshold: int = 2,
        ):
        self.suffix = suffix
        self.token = token
        self.frequency = frequency
        self.delimiters = delimiters
        self.threshold = threshold

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

    @classmethod
    def from_text(cls,
            text: str,
            threshold: int,
            delimiters: List[str]
        ) -> 'SuffixNode':
        if DEBUG_VERBOSITY["SuffixNode"]["general"] > -1:
            print("Running suffix_tree.build_tree()...")
        tree = SuffixNode.build_tree(
            text=text,
            delimiters=delimiters,
            threshold=threshold
        )

        if DEBUG_VERBOSITY["SuffixNode"]["general"] > 1:
            tree.print_tree()
        
        tree.clean()
        return tree
    
    @classmethod
    def build_tree(cls,
            text: str,
            delimiters: Set[str],
            threshold: int,
        ) -> 'SuffixNode':

        # create a store for the tree nodes
        flat_tree_store = FlatTreeStore()
        # child_dict={
        #     letter: SuffixNode(suffix=letter, token=letter) for letter in set(text)
        # })

        # point all the internal tree stores back at the main one
        for key in flat_tree_store.child_dict.keys():
            flat_tree_store.child_dict[key].flat_tree_store = flat_tree_store

        suffix_tree = SuffixNode(
            flat_tree_store=flat_tree_store,
            keys_to_my_children=set(flat_tree_store.child_dict.keys()),
            delimiters=delimiters,
            threshold=threshold
        )
        # set the root of the flat tree store to the initial SuffixNode pointing to it
        suffix_tree.flat_tree_store.root = suffix_tree

        # split the text into blocks, where each block is an independent clause
        clauses = re.split(compile_regex(delimiters), text)
        # print(set(clauses))

        if DEBUG_VERBOSITY["SuffixNode"]["general"] > 1:
            print("Initial suffix tree (just alphabet):")
            suffix_tree.print_tree()

        for string in clauses:
            if DEBUG_VERBOSITY["SuffixNode"]["general"] > 0:
                print(f"Building suffix tree for '{string}'...")

            suffix_tree.add_all_suffixes(string)

        if DEBUG_VERBOSITY["SuffixNode"]["general"] > 1:
            print(suffix_tree.get_tokens())

        return suffix_tree

    def clean(self):
        if DEBUG_VERBOSITY["SuffixNode"]["general"] > -1:
            print("Pruning modified suffix tree...")
        self.prune_tree()
        self.add_delimiters_to_tree(self.delimiters)

        if DEBUG_VERBOSITY["SuffixNode"]["pruning"] > 0:
            self.print_tree()

        if DEBUG_VERBOSITY["SuffixNode"]["general"] > 0:
            print("Getting token set...")

    def print_tree(self, indent:int=0):
        my_children = {self.flat_tree_store.child_dict[key] for key in self.keys_to_my_children}

        # Iterate over the child.suffixes (features) in the tree
        for child in my_children:
            if any(DEBUG_VERBOSITY["SuffixNode"]) > 0:
                print(f"{' ' * indent} '{child.suffix}', '{child.token}', {child.frequency}")
            else:
                print(f"{' ' * indent} '{child.suffix}': {child.frequency}")
            # If the child is a SuffixNode, recursively print the subtree
            if isinstance(child, SuffixNode):
                child.print_tree(indent=indent + 4)
            else:
                if any(DEBUG_VERBOSITY["SuffixNode"]) > 0:
                    print(f"{' ' * (indent + 4)} '{child.suffix}', '{child.token}', {child.frequency}")
                else:
                    print(f"{' ' * (indent + 4)} '{child.suffix}': {child.frequency}")

    def set_token(self):
        if self.parent.token:
            self.token = self.parent.token + self.suffix
        else:
            self.token = self.suffix

    def add_child(self, suffix):
        if DEBUG_VERBOSITY["SuffixNode"]["general"] > 1:
            print(f"Creating a new child with suffix '{suffix}'")

        child = SuffixNode(
            suffix=suffix,
            token=suffix,
            frequency=1,
            parent=self,
            flat_tree_store=self.flat_tree_store
        )

        child.set_token()

        # Add the new child to the current node's children
        self.keys_to_my_children.add(child.token)
        self.flat_tree_store.child_dict[child.token] = child

    def create_split_nodes(self,
            child,
            old_suffix,
            new_suffix,
            split_node
        ):
        # Create the old child (original suffix) under the split node
        old_child = SuffixNode(
            suffix=old_suffix,
            frequency=child.frequency - 1,
            parent=split_node,
            flat_tree_store=self.flat_tree_store,
            keys_to_my_children=child.keys_to_my_children
        )
        old_child.set_token()

        # Create the new child (new suffix) under the split node
        new_child = SuffixNode(
            suffix=new_suffix,
            frequency=1,
            parent=split_node,
            flat_tree_store=self.flat_tree_store
        )
        new_child.set_token()

        return old_child, new_child

    def split_edge(self, child, split_index, suffix):
        if DEBUG_VERBOSITY["SuffixNode"]["general"] > 1:
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
        split_node = SuffixNode(
            suffix=child.suffix[:split_index],
            frequency=child.frequency,
            parent=self,
            flat_tree_store=self.flat_tree_store
        )
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

    def longest_common_prefix(self, suffix, doSuffix):
        # Iterate over each child to find the longest common prefix
        for child_token in self.keys_to_my_children:
            child = self.flat_tree_store.child_dict[child_token]

            # Find the longest common prefix
            if doSuffix:
                child_suffix = child.suffix
            else:
                child_suffix = child.token

            min_len = min(len(suffix), len(child_suffix))
            i = 0
            while i < min_len and suffix[i] == child_suffix[i]:
                i += 1

            # If there is a common prefix
            if doSuffix and i > 0:
                return i, child_token
            elif self.token is None\
                    and not doSuffix\
                    and i > 0:
                return i, child_token
            elif self.token is not None\
                    and not doSuffix\
                    and i > len(self.token):
                return i, child_token

        return -1, None

    def add_suffix(self, suffix):
        if DEBUG_VERBOSITY["SuffixNode"]["general"] > 1:
            print(f"Current suffix: '{suffix}'")
            print(f"Children: {self.keys_to_my_children}")

        index, child_token = self.longest_common_prefix(suffix=suffix, doSuffix=True)
        # If there is a common prefix
        if index > 0:
            child = self.flat_tree_store.child_dict[child_token]

            if DEBUG_VERBOSITY["SuffixNode"]["general"] > 1:
                print(f"Child with shared suffix: '{child.token}'")
            # Update the frequency of the child node
            child.frequency += 1

            # If the common prefix matches the entire child suffix,
            #   and the new suffix would be non-empty,
            #   recurse on the remainder of the suffix
            if index == len(child.suffix) and len(suffix[index:]) > 0:
                child.add_suffix(suffix[index:])
            # Otherwise, split the edge
            elif index < len(suffix):
                self.split_edge(child, index, suffix)

            return

        # if it's an unseen character
        #   (like in the case of a divide-and-conquer approach)
        if suffix[0] not in self.flat_tree_store.root.keys_to_my_children:
            # No matching suffix, create a new child
            if DEBUG_VERBOSITY["SuffixNode"]["general"] > 1:
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

                if DEBUG_VERBOSITY["SuffixNode"]["general"] > 1:
                    print(self.get_tokens())

        else:
            # No matching suffix, create a new child
            self.add_child(suffix)

            if DEBUG_VERBOSITY["SuffixNode"]["general"] > 1:
                print(self.get_tokens())

        return

    def add_all_suffixes(self, word):
        # loop through the word, starting with the last character
        for i in range(0, len(word)):
            suffix = word[len(word) - i - 1:]

            # add the suffix to the tree
            self.add_suffix(suffix)

    # add the delimiter frequencies back into the suffix tree's storage
    def add_delimiters_to_tree(self, delimiters:List[str]):
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

    def prune_tree(self, threshold=2, indent=0):
        # If the node has no children (ie it's a leaf), return
        if not self.keys_to_my_children:
            if DEBUG_VERBOSITY["SuffixNode"]["pruning"] > 1:
                print(f"{' ' * (indent + 4)}No children for {self.token}")
            return self

        children_to_kill = set()
        dead_children = set()
        # Recursively prune the tree
        for child_token in self.keys_to_my_children:
            child = self.flat_tree_store.child_dict[child_token]

            if DEBUG_VERBOSITY["SuffixNode"]["pruning"] > 1:
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
                    child = child.prune_tree(threshold, indent=4)
                    self.flat_tree_store.child_dict[child_token] = child
                else:
                    # print("removed")
                    children_to_kill.add(child_token)

        for child_token in children_to_kill:
            # if the token's frequency falls below the threshold, prune it
            self.keys_to_my_children.remove(child_token)
            del self.flat_tree_store.child_dict[child_token]
            dead_children.add(child_token)

        if DEBUG_VERBOSITY["SuffixNode"]["pruning"] > 1:
            print(self.get_tokens())

        return self

    # return an aggregated set of all the tokens
    def get_tokens(self):
        return set(self
                   .flat_tree_store
                   .child_dict
                   .keys())
