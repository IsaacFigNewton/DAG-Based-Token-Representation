class TokenSetNode:
    # keep track of the deepest child and the height of the tree to determine the best token set
    deepest_child = None
    height = 0
    # since it would probably be too expensive to store a full token frequency table in each node
    # I'm just storing any 1-gram tokens that only appear once in this master set
    one_grams_to_exclude = set()

    def __init__(self, token_freqs, parent, depth):
        # a dictionary of different tokens' frequencies
        self.token_freqs = token_freqs
        # track the current node's parent, for later frequency table recomposition
        self.parent = parent
        # children of the original token frequency table (n+1 gram variations)
        self.children = []
        # keep track of the current node's depth in the problem tree
        self.depth = depth

    # T(n) = TokenSetNode.deepest_child
    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.token_freqs == other.token_freqs\
                and self.depth == other.depth\
                and self.parent == other.parent
        return False

    def __lt__(self, other):
        if isinstance(other, self.__class__):
            return self.depth < other.depth
        return False