import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import *


class FlatTreeStore:
    def __init__(self, child_dict=None, root=None):

        # a flattened tree of nodes,
        #   so that a node's tree membership can be checked more easily
        if child_dict is None:
            child_dict = dict()
        self.child_dict = child_dict
        self.root = root

    def tokenize(self, text, max_token_len):
        if self.root is None:
            raise ValueError("No root node provided to FlatTreeStore object")

        if debugging_verbosity["FlatTreeStore"] > 1:
            print(f"Tokenizing {text}")

        if max_token_len < 1:
            if debugging_verbosity["FlatTreeStore"] > 1:
                print(f"Text was too short")
            return [text]

        tokenization = []
        current_node = self.root

        # add the token to the tokenization list
        def add_token():
            nonlocal text, current_node, tokenization
            tokenization.append(current_node.token)
            text = text[len(current_node.token):]
            current_node = self.root

        while len(text) > 0:
            split_index, child_token = current_node.longest_common_prefix(text, doSuffix=False)
            print(split_index, child_token)

            # if there's a child of the current node with a shared prefix
            if split_index > 0:
                # move to the next child
                current_node = self.child_dict[child_token]
            # if there's no common prefix
            else:
                # add a token and reset the token pointers
                add_token()

        if debugging_verbosity["FlatTreeStore"] > 1:
            print(tokenization)
            print()

        return tokenization
