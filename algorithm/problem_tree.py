# the root node is the frequency table of all 1-grams in the text
# the children of the root node are frequency tables of all possible 2-grams

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




# recursively build the problem tree
def create_prob_tree(token_freqs, parent=None, depth=0):
    root = TokenSetNode(token_freqs, parent, depth)

    # get the max token length
    # if the frequency of said longest token n-gram > 1:
    #       create children corresponding to all variations of n+1 gram frequency tables:
    #           determine which tokens are of the same length as the longest token and create a set,
    #           let this be called the baseSet
    #           each n-gram in the baseSet can be expanded to the left or right by 1 character
    #           therefore, double the size of this baseSet by creating 2 variations on each token,
    #           one expanded to the left and one expanded to the right
    #           (drop tokens that intersect with another token that has frequency = 1)
    #
    #           create a powerset of the baseSet
    #           for each element of this powerset:
    #               n1_token_freqs = count frequencies of n and n+1 grams and put these in a frequency table (dictionary)
    #
    #               if the maximum depth on this branch has been reached
    #               if (max frequency of an n+1 gram is 1):
    #                   make a leaf
    #                   child = TokenSetNode(n1_token_freqs, root, depth + 1)
    #
    #                   if this child is the new deepest
    #                   if (child.depth > height):
    #                       deepest_child = child
    #                       update the height of the tree
    #                       height = child.depth
    #
    #               if the tree goes deeper
    #               else:
    #                   child = create_prob_tree(n1_token_freqs, root, depth + 1)
    #
    #               add the child to the parent's list of children
    #               root.children.append(child)

    return root