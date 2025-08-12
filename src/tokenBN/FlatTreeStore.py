from tokenBN.config import DEBUG_VERBOSITY

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

        if DEBUG_VERBOSITY["FlatTreeStore"] > 1:
            print(f"Tokenizing {text}")

        if max_token_len < 1:
            if DEBUG_VERBOSITY["FlatTreeStore"] > 1:
                print(f"Text was too short")
            return [text]

        tokenization = []
        current_node = self.root

        # add the token to the tokenization list
        def add_token(token):
            nonlocal text, current_node, tokenization
            tokenization.append(token)
            text = text[len(token):]
            current_node = self.root

        prev_token = None
        while len(text) > 0:
            split_index, child_token = current_node.longest_common_prefix(text, doSuffix=False)
            if DEBUG_VERBOSITY["FlatTreeStore"] > 1:
                print(split_index, child_token)

            # if the max token length has been exceeded
            if split_index > max_token_len:
                # add the second-longest token
                add_token(prev_token)
            # if there's a child of the current node with a shared prefix
            elif split_index > 0:
                # move to the next child
                prev_token = child_token
                current_node = self.child_dict[child_token]
            # if there's no common prefix
            else:
                # add a token and reset the token pointers
                add_token(current_node.token)

        if DEBUG_VERBOSITY["FlatTreeStore"] > 1:
            print(tokenization)
            print()

        return tokenization
