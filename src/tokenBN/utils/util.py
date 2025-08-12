import re


def count_occurrences(text, delimiters=None):
    if not delimiters:
        delimiters = set()

    # Initialize a dictionary to keep track of occurrences
    occurrences = {s: 0 for s in delimiters}

    # For each delimiter, count occurrences using regex search
    for s in delimiters:
        # Use re.findall to count occurrences of each delimiter in the text
        occurrences[s] = len(re.findall(re.escape(s), text))

    return occurrences


def compile_regex(delimiters=None):
    if not delimiters:
        delimiters = set()

    # Join the strings with '|' and escape special characters
    regex_pattern = "|".join(re.escape(s) for s in delimiters)

    # Enclose the pattern in parentheses to group it
    return f"({regex_pattern})"
