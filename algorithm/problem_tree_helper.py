from itertools import chain, combinations
from collections import Counter
import json

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

    n1_freqs = count_substrings(text, n1_tokens)
    n1_gram_tokens = {token for token in n1_freqs if n1_freqs[token] > 1}

    # print("n + 1 gram tokens after filtering: ", n1_gram_tokens)
    # print()

    return n1_gram_tokens


# generate the powerset of the n+1-gram tokens (excluding the empty set)
def powerset(iterable):
    s = list(iterable)
    return chain.from_iterable(combinations(s, r) for r in range(1, len(s) + 1))




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