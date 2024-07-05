from problem_tree import *

class TokenNode:
    def __init__(self, token_set = dict(), children=[]):
        self.token_set = token_set
        self.children = children

def tokenize(text, token_set):
    #       base case 1: if the text or the token set is empty but not both, print an error and return None
    #       base case 2: if the text is an empty string and the token set is empty, return None

    root = TokenNode(token_set)
    new_token_set = {}
    # sort the tokens based on the length of the first element in each tuple
    sorted_token_set = sorted(token_set, key=lambda x: len(x[0]))

    print("Optimal token set: ", sorted_token_set)

    # tokenize the text based on the tokens provided,
    #       start with the first token in sorted_token_set and end with the last,
    #       remove the associated text from consideration after each token is read,
    #       subtract 1 from the frequency of each token from their entries in the token set,
    #       if the frequency of a token drops to 0, remove it from the token set
    #       for each token that was parsed from the text, in new_token_set, add a new entry if none exists and add 1 to the frequency,
    # once all tokens have been read from the text:
    #       recursively perform this tokenization process on each token in new_token_set using the remainder of token_set,
    #       create a TokenNode child for each token from new_token_set that was recursively tokenized in this process
    #       append each child to root.children

    return root


if __name__ == "__main__":
    text = "abczabc"

    token_set = list(get_best_token_set(text).items())