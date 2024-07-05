from problem_tree import *

class TokenNode:
    def __init__(self, token_set, children=[]):
        self.token_set = token_set
        self.children = children

def tokenize(text, token_set):
    #       base case 1: if the text or the token set is empty but not both, print an error and return None
    #       base case 2: if the text is an empty string and the token set is empty, return None

    root = TokenNode(token_set)

    # sort the tokens based on the length of the first element in each tuple
    sorted_token_set = sorted(token_set, key=lambda x: len(x[0]))

    print("Optimal token set: ", sorted_token_set)

    # tokenize the text based on the tokens provided,
    # starting with the first token and ending with the last,
    # removing the associated text from consideration after each token is read
    # once all tokens have been read from the text:
    #       subtract the frequency of each token from their entries in the token set
    #       if the frequency of a token drops to 0, remove it from the token set
    #       recursively perform this tokenization process on each remaining token using the remainder of the token set,
    #       create a TokenNode child for each token tokenized this tokenizable token
    #       append each child to root.children

    return root


if __name__ == "__main__":
    text = "abczabc"

    token_set = list(get_best_token_set(text).items())