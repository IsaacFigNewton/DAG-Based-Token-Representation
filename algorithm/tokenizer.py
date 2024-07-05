from problem_tree import *


class TokenNode:
    def __init__(self, token_set=dict(), parent_token_set=dict(), children=None):
        self.token_set = token_set
        self.parent_token_set = parent_token_set
        self.children = children if children is not None else []

def tokenize(text, token_set, parent_token_set=dict()):
    # Base case 1: if the text is empty, then the whole text has been tokenized, return None
    if not text:
        return None
    # Base case 2: if the text is NOT an empty string but the token set is empty,
    #               then something is wrong, so print an error and return None
    if text and not token_set:
        print("Error: Either text or token set is empty, but not both.")
        return None

    root = TokenNode(token_set.copy(), parent_token_set)
    new_token_set = {}

    # Sort the tokens based on the length of the first element in each tuple
    sorted_token_set = sorted(token_set.keys(), key=lambda x: -len(x))

    print("Optimal token set: ", sorted_token_set)

    for token in sorted_token_set:

        # Find all occurrences of the token in the text
        start = 0
        while True:
            print("Text: ", text)

            start = text.find(token, start)
            if start == -1:
                break

            # Subtract 1 from the frequency of each token from their entries in the token set
            # make this subtraction proportional to the number of occurrences of the parent token/text
            occurrences = parent_token_set.get(text, 1)
            token_set[token] -= occurrences
            if token_set[token] <= 0:
                del token_set[token]
            print("Old token set: ", token_set)

            # Add the token to the new_token_set
            if token in new_token_set:
                new_token_set[token] += occurrences
            else:
                new_token_set[token] = occurrences
            print("New token set: ", new_token_set)

            # Remove the associated text from consideration
            text = text[:start] + text[start + len(token):]

            print()

    # Recursively perform this tokenization process on each token in new_token_set using the remainder of token_set
    for token in new_token_set:
        child_node = tokenize(token, token_set, new_token_set)
        if child_node:
            root.children.append(child_node)

    return root


if __name__ == "__main__":
    text = "abczabc"

    token_set = get_best_token_set(text)

    print()

    token_tree = tokenize(text, token_set)

    print("Level 1: ", token_tree.token_set)
    print("Level 2: ", [child.token_set for child in token_tree.children])