# the root node is the frequency table of all 1-grams in the text
# the children of the root node are frequency tables of all possible 2-grams

from itertools import chain, combinations
from collections import Counter

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
        self.parent = None
        # children of the original token frequency table (n+1 gram variations)
        self.children = []
        # keep track of the current node's depth in the problem tree
        self.depth = 0

def filter_n1_tokens(n1_tokens):
    print("n + 1 gram tokens before filtering...")
    print(n1_tokens)

    # TODO: implement this for n-grams larger than 1 in a time, space efficient manner
    n1_gram_tokens = {token for token in n1_tokens
                      if all(one_gram not in token for one_gram in TokenSetNode.one_grams_to_exclude)}

    print("n + 1 gram tokens after filtering...")
    print(n1_gram_tokens)

    return n1_gram_tokens


# generate the powerset of the n+1-gram tokens (excluding the empty set)
def powerset(iterable):
    s = list(iterable)
    return chain.from_iterable(combinations(s, r) for r in range(1, len(s) + 1))


# recursively build the problem tree
def create_prob_tree(token_freqs, text="", parent=None, depth=0):
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
    # initialize the root node with the current token frequencies, parent, and depth
    root = TokenSetNode(token_freqs, parent, depth)

    # if no text was provided
    if len(text) <= 1:
        print("no text provided")
        return root
    # if no token frequencies were provided
    elif (not token_freqs):
        print("no token frequencies provided")
        return root

    # get the length of the longest token
    max_token_length = max(len(token) for token in token_freqs)
    # filter out tokens with the maximum length and frequency > 1
    base_set = {token for token in token_freqs if len(token) == max_token_length and token_freqs[token] > 1}

    # if the frequencies of the largest tokens are all 1
    if len(base_set) == 0:
        return root

    # create a set to hold the n+1-gram tokens
    n1_gram_tokens = set()

    # iterate over each token in the base set
    for token in base_set:
        # find all occurrences of the token in the text
        start = 0
        while True:
            # get the index of the next token
            start = text.find(token, start)

            # quit if no token found
            if start == -1:
                break

            # expand the token to the left by one character
            if start > 0:
                left_expanded = text[start - 1:start + len(token)]
                n1_gram_tokens.add(left_expanded)

            # expand the token to the right by one character
            if start + len(token) < len(text):
                right_expanded = text[start:start + len(token) + 1]
                n1_gram_tokens.add(right_expanded)

            # move to the next appearance
            start += len(token)


    # filter out tokens that intersect with a smaller token that has frequency = 1
    n1_gram_tokens = filter_n1_tokens(n1_gram_tokens)
    token_powerset = powerset(n1_gram_tokens)
    powerset_length = sum(1 for i in token_powerset)
    print("Power set length ", powerset_length)

    # if there were no valid n+1-gram tokens
    if powerset_length == 0:
        child = TokenSetNode({}, root, depth + 1)

        print(depth + 1)
        print(child.token_freqs)
        TokenSetNode.height = depth + 1
        TokenSetNode.deepest_child = child
        root.children.append(child)

        return root

    for subset in token_powerset: #.union(base_set)):
        # count frequencies of n-gram and n+1-gram tokens in the subset
        child_token_freqs = {token: text.count(token) for token in subset}

        # # get frequencies of just n+1-gram tokens in the subset
        # child_token_n1_freqs = {token: freq for token, freq in child_token_freqs.items() if token in n1_gram_tokens}


        # if the maximum frequency of an n+1-gram is 1 or the
        if max(child_token_freqs.values()) <= 1:
            # make a leaf node
            child = TokenSetNode(child_token_freqs, root, depth + 1)

            # check if this is the deepest leaf
            if depth + 1 > height:
                print(depth + 1)
                print(child.token_freqs)
                TokenSetNode.height = depth + 1
                TokenSetNode.deepest_child = child

            root.children.append(child)
        
        else:
            # recursively build the tree for deeper levels
            child = create_prob_tree(child_token_freqs, text, root, depth + 1)
            root.children.append(child)

    return root


def accumulate_token_set(node):
    # get the current node's token set
    token_set = node.token_freqs

    # if this node has a parent, add on its token set and recurse
    if node.parent != None:
        token_set.update(accumulate_token_set(node.parent))
        return token_set

    # return the combined token set
    return token_set


def get_best_token_set(text):
    one_gram_freqs = Counter(text)

    print("1-gram frequencies...")
    print(one_gram_freqs)

    TokenSetNode.one_grams_to_exclude = {token: count for token, count in one_gram_freqs.items() if count < 2}

    print("1-gram tokens that didn't repeat...")
    print(TokenSetNode.one_grams_to_exclude)

    problem_tree = create_prob_tree(one_gram_freqs, text)
    best_token_table = accumulate_token_set(TokenSetNode.deepest_child)

    print(best_token_table)

if __name__ == "__main__":
    get_best_token_set("abczabc")