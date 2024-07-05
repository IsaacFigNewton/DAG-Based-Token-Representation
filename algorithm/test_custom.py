from custom import *


def test_rw(filename):
    # Read the input file
    with open(filename + ".txt", "r") as file:
        data = file.read().strip()
    print("Original data:", data)

    # Encode the data
    encoded_data, huffman_codes = huffman_encoding(data)
    print("Encoded data:", encoded_data)
    print("Huffman Codes:", huffman_codes)

    # Write the encoded data to an output file
    with open(filename + "_out.txt", "w") as file:
        file.write(encoded_data)
        file.write("\n")
        file.write(codes_to_str(huffman_codes))

    # Read the encoded data from the output file
    with open(filename + "_out.txt", "r") as file:
        data = file.read()

    # Check the encoded data
    encoded_data, huffman_codes = extract_data(data)
    print("Encoded data:", encoded_data)
    print("Huffman Codes:", huffman_codes)

    # Decode the encoded data
    decoded_data = huffman_decoding(encoded_data, huffman_codes)
    print("Decoded data:", decoded_data)

def test1():
    data = "this is an example for huffman encoding"
    print("Original data:", data)

    encoded_data, huffman_codes = huffman_encoding(data)
    print("Encoded data:", encoded_data)
    print("Huffman Codes:", huffman_codes)

    decoded_data = huffman_decoding(encoded_data, huffman_codes)
    print("Decoded data:", decoded_data)


def test2():
    filename = "empty"

    test_rw(filename)


def test3():
    filename = "bee_movie"

    test_rw(filename, )


# Example usage
if __name__ == "__main__":
    print("Running test 1...")
    test1()

    print("\n")

    print("Running test 2...")
    test2()
    #
    # print("\n")
    #
    # print("Running test 3...")
    # test3()