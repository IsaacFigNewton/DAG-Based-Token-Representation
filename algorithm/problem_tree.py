# the root node is the frequency table of all 1-grams in the text
# the children of the root node are frequency tables of all possible 2-grams

from itertools import chain, combinations


class TokenSetNode:
    # keep track of the deepest child and the height of the tree to determine the best token set
    deepest_child = None
    height = 0

    def __init__(self, token_freqs, parent, depth):
        # a dictionary of different tokens' frequencies
        self.token_freqs = token_freqs
        # track the current node's parent, for later frequency table recomposition
        self.parent = None
        # children of the original token frequency table (n+1 gram variations)
        self.children = []
        # keep track of the current node's depth in the problem tree
        self.depth = 0


# Generate the powerset of the n+1-gram tokens (excluding the empty set)
def powerset(iterable):
    s = list(iterable)
    return chain.from_iterable(combinations(s, r) for r in range(1, len(s) + 1))

# recursively build the problem tree
def create_prob_tree(token_freqs, parent=None, depth=0, text=None):
    """
    Creates a problem tree from token frequencies.

    Args:
        token_freqs (dict): A dictionary of token frequencies.
        parent (TokenSetNode, optional): The parent node. Defaults to None.
        depth (int, optional): The current depth of the tree. Defaults to 0.
        text (str, optional): The original text. Defaults to None.

    Returns:
        TokenSetNode: The root of the problem tree.
    """

    # Initialize the root node with the current token frequencies, parent, and depth
    root = TokenSetNode(token_freqs, parent, depth)

    # Base case: if no token frequencies or all frequencies are 1, return the root
    if not token_freqs or max(token_freqs.values()) <= 1:
        return root

    # Get the length of the longest token
    max_token_length = max(len(token) for token in token_freqs)

    # Filter out tokens with the maximum length and frequency > 1
    base_set = {token for token in token_freqs if len(token) == max_token_length and token_freqs[token] > 1}

    # Create a set to hold the n+1-gram tokens
    n1_gram_tokens = set()

    # Iterate over each token in the base set
    for token in base_set:
        # Find all occurrences of the token in the text
        start = 0
        while True:
            start = text.find(token, start)
            if start == -1:
                break
            # Expand the token to the left and right by one character
            if start > 0:
                left_expanded = text[start - 1:start + len(token)]
                n1_gram_tokens.add(left_expanded)
            if start + len(token) < len(text):
                right_expanded = text[start:start + len(token) + 1]
                n1_gram_tokens.add(right_expanded)
            start += len(token)

    # Filter out tokens that intersect with another token that has frequency = 1
    n1_gram_tokens = {token for token in n1_gram_tokens if token_freqs.get(token, 0) > 1}


    for subset in powerset(n1_gram_tokens):
        # Count frequencies of n-gram and n+1-gram tokens in the subset
        n1_token_freqs = {token: text.count(token) for token in subset}

        # If the maximum frequency of an n+1-gram is 1
        if max(n1_token_freqs.values()) <= 1:
            # make a leaf node
            child = TokenSetNode(n1_token_freqs, root, depth + 1)

            # Check if this is the deepest leaf
            if depth + 1 > height:
                height = depth + 1
                deepest_child = child

            root.children.append(child)
        
        else:
            # Recursively build the tree for deeper levels
            child = create_prob_tree(n1_token_freqs, root, depth + 1, text)
            root.children.append(child)

    return root
