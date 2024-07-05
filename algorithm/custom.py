import heapq
from collections import defaultdict, Counter

sep = "`"


class HuffmanNode:
    def __init__(self, token, freq):
        # Character represented by this node
        self.token = token
        # Frequency of the character
        self.freq = freq
        # Left child in the Huffman Tree
        self.left = None
        # Right child in the Huffman Tree
        self.right = None

    # Less than operator for heapq to compare nodes by frequency
    def __lt__(self, other):
        return self.freq < other.freq

def build_huffman_tree(frequency):
    """
    Builds the Huffman Tree based on character frequencies.
    """
    # Create a priority queue (min-heap) from the frequency dictionary
    heap = [HuffmanNode(char, freq) for char, freq in frequency.items()]
    heapq.heapify(heap)

    # Merge nodes until there's only one node left (the root of the Huffman Tree)
    while len(heap) > 1:
        # Pop the two nodes with the smallest frequency
        node1 = heapq.heappop(heap)
        node2 = heapq.heappop(heap)
        # Merge these nodes
        merged = HuffmanNode(None, node1.freq + node2.freq)
        merged.left = node1
        merged.right = node2
        # Push the merged node back into the heap
        heapq.heappush(heap, merged)

    # The remaining node is the root of the Huffman Tree
    return heap[0]

def build_codes(node, prefix="", codebook=0):
    """
    Recursively builds the Huffman Codes by traversing the Huffman Tree.
    """
    # if no codebook was provided, create a new one
    if type(codebook) == int:
        codebook = {}

    if node is not None:
        if node.token is not None:
            # Assign the current prefix as the code for the character
            codebook[node.token] = prefix
        # Traverse left with '0' added to the prefix
        build_codes(node.left, prefix + "0", codebook)
        # Traverse right with '1' added to the prefix
        build_codes(node.right, prefix + "1", codebook)
    return codebook


def extract_data(data):
    index_of_newline = data.find(sep)
    data = [data[0:index_of_newline], data[index_of_newline:]]
    # first get the encoded data
    encoded_data = data[0]
    # all the rest should be the huffman codebook
    # this approach is resilient against newline characters being in the codebook
    huffman_codes = str_to_codes(data[1])

    return encoded_data, huffman_codes

def codes_to_str(codebook):
    string = ""
    for key, value in codebook.items():
        string += sep + str(key) + sep + str(value)

    return string


def str_to_codes(string):
    codebook = dict()

    print(string)
    string = string[len(sep):]
    str_items = string.split(sep)

    # ensure that there is stuff to decode from the codebook
    if len(str_items) >= 2:
        for i in range(0, len(str_items), 2):
            codebook[str_items[i]] = str_items[i + 1]

    return codebook


def huffman_encoding(data):
    """
    Encodes the given data using Huffman Coding.
    """
    # Return empty results for empty input
    if not data:
        return "", {}

    # Count the frequency of each character in the data
    frequency = Counter(data)
    # Build the Huffman Tree
    huffman_tree = build_huffman_tree(frequency)
    # Generate Huffman Codes
    huffman_codes = build_codes(huffman_tree)

    # Encode the data using the generated codes
    encoded_data = ''.join(huffman_codes[char] for char in data)
    return encoded_data, huffman_codes



def huffman_decoding(encoded_data, codebook):
    """
    Decodes the encoded data using the given Huffman Codes.
    """
    # Reverse the codebook to map codes back to characters
    reversed_codebook = {v: k for k, v in codebook.items()}
    current_code = ""
    decoded_output = []

    # Decode the data by matching codes
    for bit in encoded_data:
        current_code += bit
        if current_code in reversed_codebook:
            decoded_output.append(reversed_codebook[current_code])
            current_code = ""

    return ''.join(decoded_output)