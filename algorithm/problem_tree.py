# Use a thread-safe dictionary for memoization
from concurrent.futures import ThreadPoolExecutor, as_completed
from multiprocessing import Process, Manager, cpu_count
from threading import Lock
from TokenSetNode import TokenSetNode
from problem_tree_helper import *

# since it would probably be too expensive to store a full token frequency table in each node
# I'm just storing any 1-gram tokens that only appear once in this master set
one_grams_to_exclude = set()

# whether or not to prune dead branches of the tree/save them for later printing/debugging
prune_tree = 1

# create a manager and a memoization dictionary to be shared among all processes
# a dictionary of previously explored frequency tables at each depth
# Key:      problem tree depth
# Value:    set of frequency table dictionaries at that depth
manager = None
token_freq_tables = None

# keep track of the deepest child and the height of the tree to determine the best token set
deepest_child = None
deepest_child_lock = None
height = 0


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

def prune_dead_branch(node):
    # a switch in case someone doesn't want to prune the tree
    if prune_tree:
        if node is None:
            return

        # If the node is a leaf (has no children) and is not the current deepest child
        if len(node.children) == 0 and node != deepest_child:
            if node.parent:
                # Remove this node from its parent's children
                if node in node.parent.children:
                    node.parent.children.remove(node)
                # Recursively check the parent
                prune_dead_branch(node.parent)

    pass


def update_deepest_child(root, depth):
    global deepest_child, height
    new_child = TokenSetNode({}, root, depth + 1)

    # Prune the old deepest child if it exists and is different from the new one
    if deepest_child and deepest_child != new_child:
        old_deepest = deepest_child
        deepest_child = new_child
        prune_dead_branch(old_deepest)

    height = depth + 1
    deepest_child = new_child
    root.children.append(new_child)


def process_subset(subset, text, root, depth):
    # print("Spun off child to deal with subset ", subset)
    child_token_freqs = {token: text.count(token) for token in subset}

    if check_token_freq_tables(child_token_freqs, depth + 1):
        return None

    if max(child_token_freqs.values()) <= 1:
        print("Child found leaf")
        with deepest_child_lock:
            # if it's a new deepest child, update the deepest child
            if depth + 1 > height:
                update_deepest_child(root, depth)

            # otherwise, it's a short deadend, so just remove it
            prune_dead_branch(root)

        return None

    return create_prob_tree(child_token_freqs, text, root, depth + 1)


def create_prob_tree(token_freqs, text="", parent=None, depth=0):
    root = TokenSetNode(token_freqs, parent, depth)

    if check_token_freq_tables(token_freqs, depth):
        return None

    if len(text) <= 1:
        print("no text provided")
        return None
    elif not token_freqs:
        print("no token frequencies provided")
        return None

    max_token_length = max(len(token) for token in token_freqs)
    base_set = {token for token in token_freqs if len(token) == max_token_length and token_freqs[token] > 1}

    if len(base_set) == 0:
        return None

    n1_gram_tokens = collect_n1_grams(base_set, text)
    n1_gram_tokens = filter_n1_tokens(n1_gram_tokens, text)
    token_powerset = {i for i in powerset(n1_gram_tokens)}
    # # sort the powerset in descending order of subset length and descending order of the first subset elements
    # # this helps ensure consistency in testing
    # token_powerset = sorted([sorted(list(i)) for i in powerset(n1_gram_tokens)],
    #                         key = lambda x: (len(x), x[0]))

    # if there are no valid n+1-gram token subsets
    if len(token_powerset) == 0:
        with deepest_child_lock:
            update_deepest_child(root, depth)
        return None

    # Parallel processing of subsets
    with ThreadPoolExecutor(max_workers=cpu_count()) as executor:
        future_to_subset = {executor.submit(process_subset, subset, text, root, depth): subset for subset in
                            token_powerset}

        for future in as_completed(future_to_subset):
            child = future.result()
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
    if node.depth == height:
        print('\t' * indent, "Depth ", node.depth, ", Token Frequencies: ",node.token_freqs, "\t<---- Deepest child")
    else:
        print('\t' * indent, "Depth ", node.depth, ", Token Frequencies: ",node.token_freqs)

    for child in node.children:
        print_tree(child, indent + 1)


def get_best_token_set(text):
    one_gram_freqs = Counter(text)

    print("1-gram frequencies: ", one_gram_freqs)

    one_grams_to_exclude = {token: count for token, count in one_gram_freqs.items() if count < 2}

    print("1-gram tokens that didn't repeat: ", one_grams_to_exclude)

    problem_tree = create_prob_tree(one_gram_freqs, text)

    print()
    print_tree(problem_tree)
    print()

    best_token_set = accumulate_token_set(deepest_child.parent)

    print("Optimal token set: ", best_token_set)
    print("\n")

    return best_token_set



if __name__ == "__main__":
    manager = Manager()
    token_freq_tables = manager.dict()

    deepest_child_lock = Lock()

    token_set = get_best_token_set("abracadabradabra")