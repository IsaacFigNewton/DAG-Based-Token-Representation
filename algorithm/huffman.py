import heapq
from collections import defaultdict, Counter

class HuffmanNode:
    def __init__(self, char, freq):
        # Character represented by this node
        self.char = char
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
        if node.char is not None:
            # Assign the current prefix as the code for the character
            codebook[node.char] = prefix
        # Traverse left with '0' added to the prefix
        build_codes(node.left, prefix + "0", codebook)
        # Traverse right with '1' added to the prefix
        build_codes(node.right, prefix + "1", codebook)
    return codebook


def codes_to_str(codebook):
    string = ""
    for key, value in codebook.items():
        string = " ".join([string, key, value])

    return string[1:]


def str_to_codes(string):
    codebook = dict()
    str_items = string.split(" ")
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


def test1():
    data = "this is an example for huffman encoding"
    print("Original data:", data)

    encoded_data, huffman_codes = huffman_encoding(data)
    print("Encoded data:", encoded_data)
    print("Huffman Codes:", huffman_codes)

    decoded_data = huffman_decoding(encoded_data, huffman_codes)
    print("Decoded data:", decoded_data)

def test2():
    # Read the input file
    with open("abcdabcd.txt", "r") as file:
        data = file.read().strip()
    print("Original data:", data)

    # Encode the data
    encoded_data, huffman_codes = huffman_encoding(data)
    print("Encoded data:", encoded_data)
    print("Huffman Codes:", huffman_codes)

    # Write the encoded data to an output file
    with open("abcdabcd_out.txt", "w") as file:
        file.write(encoded_data)
        file.write("\n")
        file.write(codes_to_str(huffman_codes))

    # Read the encoded data from the output file
    with open("abcdabcd_out.txt", "r") as file:
        data = file.read()

    # Check the encoded data
    data = data.split("\n")
    encoded_data = data[0]
    huffman_codes = str_to_codes(data[1])
    print("Encoded data:", encoded_data)
    print("Huffman Codes:", huffman_codes)

    # Decode the encoded data
    decoded_data = huffman_decoding(encoded_data, huffman_codes)
    print("Decoded data:", decoded_data)

# Example usage
if __name__ == "__main__":
    print("Running test 1...")
    test1()

    print("\n")

    print("Running test 2...")
    test2()