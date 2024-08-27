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
        i = 0
        j = 1

        # add the token to the tokenization list
        def add_token():
            nonlocal i, j, current_node, tokenization
            tokenization.append(current_node.token)
            i = j - 1
            j = i + 1
            current_node = self.root

        # while the end of the text hasn't been reached
        #   and the max token length hasn't been reached
        while j < len(text) + 1:
            current_token = text[i:j]
            if debugging_verbosity["FlatTreeStore"] > 1:
                print(f"Current token: {current_token}")

            # if the max token size is reached, store this token and move on
            if j - i > max_token_len:

                if debugging_verbosity["FlatTreeStore"] > 1:
                    print(f"Adding current token to tokenization list...")

                add_token()

            # otherwise, get the next largest token
            else:
                # if the current token is a child of the current_node
                if current_token in current_node.keys_to_my_children:
                    current_node = current_node.flat_tree_store.child_dict[current_token]
                    j += 1
                # otherwise, if the current token isn't in the token set,
                #   add the current node's token to the tokenization,
                #   get the new text as 1 character before this issue
                #   and set the current node to the root
                else:
                    if debugging_verbosity["FlatTreeStore"] > 1:
                        print(f"No child match found, adding previous token to tokenization list...")

                    add_token()

        if len(current_token) > 0:
            if debugging_verbosity["FlatTreeStore"] > 1:
                print(f"Adding last token to tokenization list...")
            tokenization.append(current_node.token)

        if debugging_verbosity["FlatTreeStore"] > 1:
            print(tokenization)
            print()

        return tokenization
