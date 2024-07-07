from itertools import chain, combinations
from collections import Counter
import json

# whether or not to prune dead branches of the tree/save them for later printing/debugging
prune_tree = 1

# a dictionary of previously explored frequency tables at each depth
# Key:      problem tree depth
# Value:    set of frequency table dictionaries at that depth
token_freq_tables = dict()

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

def check_token_freq_tables(freq_table, depth):
    # convert the frequency table to a hashable type by treating it as json to be flattened
    json_str = json.dumps(freq_table, sort_keys=True)

    # if the set of tables at this depth has been defined
    if depth in token_freq_tables.keys():
        # if this branch has been previously explored
        if json_str in token_freq_tables[depth]:
            return True
        # otherwise, mark this branch as explored, but continue deeper
        else:
            token_freq_tables[depth].add(json_str)
            return False
    # otherwise, if nothing has been explored at this depth before
    else:
        # create a new entry for the branch at this depth
        token_freq_tables[depth] = set()
        # mark it as explored
        token_freq_tables[depth].add(json_str)
        # continue
        return False



def collect_n1_grams(base_set, text):
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

    return n1_gram_tokens


def count_substrings(string, substrings):
    # Initialize a Counter object
    counter = Counter()

    # Iterate through each substring
    for substring in substrings:
        # Count the occurrences of the substring in the main string
        count = string.count(substring)
        # Update the Counter object with the count
        counter[substring] = count

    return counter


def filter_n1_tokens(n1_tokens, text):
    # print("n + 1 gram tokens before filtering: ", n1_tokens)

    # TODO: implement this for n-grams larger than 1 in a time, space efficient manner
    n1_gram_tokens = {token for token in n1_tokens
                      if all(one_gram not in token for one_gram in TokenSetNode.one_grams_to_exclude)}

    n1_freqs = count_substrings(text, n1_gram_tokens)
    n1_gram_tokens = {token for token in n1_freqs if n1_freqs[token] > 1}

    # print("n + 1 gram tokens after filtering: ", n1_gram_tokens)
    # print()

    return n1_gram_tokens


# generate the powerset of the n+1-gram tokens (excluding the empty set)
def powerset(iterable):
    s = list(iterable)
    return chain.from_iterable(combinations(s, r) for r in range(1, len(s) + 1))


def prune_dead_branch(node):
    if prune_tree:
        if node is None:
            return

        # If the node is a leaf (has no children) and is not the current deepest child
        if len(node.children) == 0 and node != TokenSetNode.deepest_child:
            if node.parent:
                # Remove this node from its parent's children
                if node in node.parent.children:
                    node.parent.children.remove(node)
                # Recursively check the parent
                prune_dead_branch(node.parent)

    pass


def update_deepest_child(root, depth):
    new_child = TokenSetNode({}, root, depth + 1)

    # Prune the old deepest child if it exists and is different from the new one
    if TokenSetNode.deepest_child and TokenSetNode.deepest_child != new_child:
        old_deepest = TokenSetNode.deepest_child
        TokenSetNode.deepest_child = new_child
        prune_dead_branch(old_deepest)

    TokenSetNode.height = depth + 1
    TokenSetNode.deepest_child = new_child
    root.children.append(new_child)


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

    # check if this branch has been previously explored
    previously_explored = check_token_freq_tables(token_freqs, depth)
    # if it has, then stop here
    if previously_explored:
        return root
    # if no text was provided
    if len(text) <= 1:
        print("no text provided")
        return root
    # if no token frequencies were provided
    elif not token_freqs:
        print("no token frequencies provided")
        return root

    # get the length of the longest token
    max_token_length = max(len(token) for token in token_freqs)
    # filter out tokens with the maximum length and frequency > 1
    base_set = {token for token in token_freqs if len(token) == max_token_length and token_freqs[token] > 1}

    # if the frequencies of the largest tokens are all 1
    if len(base_set) == 0:
        return root

    # collect a set of n + 1 grams from the text
    n1_gram_tokens = collect_n1_grams(base_set, text)

    # filter tokens that intersect with a smaller token that has frequency = 1 or that only occur once
    n1_gram_tokens = filter_n1_tokens(n1_gram_tokens, text)
    token_powerset = {i for i in powerset(n1_gram_tokens)}
    # print("Power set length: ", len(token_powerset))
    # print("Power set contents: ", token_powerset)

    # if there were no valid n+1-gram tokens
    if len(token_powerset) == 0:

        update_deepest_child(root, depth)
        # print("Child depth: ", depth + 1)
        # print("Child token freqs: ", child.token_freqs)

        return root

    for subset in token_powerset:
        child_token_freqs = {token: text.count(token) for token in subset}

        # if the most frequent token occurs only once, this is a leaf
        if max(child_token_freqs.values()) <= 1:
            # if a new deepest child is found
            if depth + 1 > TokenSetNode.height:
                update_deepest_child(root, depth)

        else:
            child = create_prob_tree(child_token_freqs, text, root, depth + 1)
            if child is not None:
                root.children.append(child)

    return root


def accumulate_token_set(node):
    if isinstance(node, TokenSetNode):
        # get the current node's token set
        token_set = dict(node.token_freqs)

        # if this node has a parent, add on its token set and recurse
        if node.parent != None:
            token_set.update(accumulate_token_set(node.parent))
            return token_set

        # return the combined token set
        return token_set

    print("Token accumulation failed")
    return None


def print_tree(node, indent=0):
    if node.depth == TokenSetNode.height:
        print('\t' * indent, "Depth ", node.depth, ", Token Frequencies: ",node.token_freqs, "\t<---- Deepest child")
    else:
        print('\t' * indent, "Depth ", node.depth, ", Token Frequencies: ",node.token_freqs)

    for child in node.children:
        print_tree(child, indent + 1)


def get_best_token_set(text):
    one_gram_freqs = Counter(text)

    print("1-gram frequencies: ", one_gram_freqs)

    TokenSetNode.one_grams_to_exclude = {token: count for token, count in one_gram_freqs.items() if count < 2}

    print("1-gram tokens that didn't repeat: ", TokenSetNode.one_grams_to_exclude)

    problem_tree = create_prob_tree(one_gram_freqs, text)

    print()
    # print_tree(problem_tree)
    print()

    best_token_set = accumulate_token_set(TokenSetNode.deepest_child.parent)

    print("Optimal token set: ", best_token_set)
    print("\n")

    return best_token_set



if __name__ == "__main__":
    token_set = get_best_token_set("mary had a little lamb, little lamb")




