import numpy as np
import tensorflow as tf
from scipy.sparse.csgraph import connected_components


def calculate_distances_for_subgraph(labels, adjacency_matrix, subgraph_id):
    """
    Calculate Manhattan distances for nodes in a specific subgraph and update the distance matrix.

    Parameters:
    labels (numpy array): Array of subgraph labels for each node.
    adjacency_matrix (CSR matrix): A sparse adjacency matrix of the graph.
    subgraph_id (int): ID of the subgraph to process.
    """
    # extract a list of all the subgraph vertices in the current subgraph
    subgraph_vertices = np.where(labels == subgraph_id)[0]

    n = adjacency_matrix.shape[0]

    indices = []
    values = []
    # for each seed node
    for i in subgraph_vertices:
        # for each outgoing node in the subgraph
        for x in subgraph_vertices:
            # for each incoming node in the subgraph
            for y in subgraph_vertices:
                # if the entry, when double-checked, is found to be nonzero
                if adjacency_matrix[x, y] != 0 or i == x and x == y:
                    # calculate inverted Manhattan distance, kind of
                    #   since a node in the same row or column as the seed
                    #   must have a distance of 1 from the seed,
                    #   determine the shortest distance to either the row or column
                    #   this is a heuristic since it would take too long to re-traverse the dag from scratch

                    # if the entry represents the seed node
                    if i == x and x == y:
                        inverse_manhattan_distance = 1
                    else:
                        #   numerator is 0.75 to discount weight of non-self nodes
                        inverse_manhattan_distance = 0.75 / np.maximum(min(np.abs(x - i), np.abs(y - i)), 1)

                    # Store indices and values in lists
                    indices.append([i, x, y])
                    values.append(inverse_manhattan_distance)

    if not indices:
        print("Error, the entry for the seed node was not created in the tensor")
        return None

    # return for recombination with the entire graph's tensor
    return indices, values


def vectorize_adjacency_matrix(adjacency_matrix, low_mem=True):
    """
    Vectorize the adjacency matrix by calculating Manhattan distances for each subgraph.

    Parameters:
    adjacency_matrix (CSR matrix): Adjacency matrix of the graph.

    Returns:
    sparse CSR matrix: 3D distance matrix.
    """
    n = adjacency_matrix.shape[0]

    # Identify subgraphs and their labels
    num_subgraphs, labels = connected_components(adjacency_matrix, directed=False, return_labels=True)
    indices = []
    values = []

    if low_mem:
        # Calculate distances for each subgraph in series
        for subgraph_id in range(num_subgraphs):
            subgraph_distance_tensor = calculate_distances_for_subgraph(labels, \
                                                                        adjacency_matrix, \
                                                                        subgraph_id)

            # if there's a subgraph distance tensor to combine the original with...
            if subgraph_distance_tensor is not None:
                # Recombine the partial vectorizations given by the subgraphs into
                #   a single vectorization for the entire graph
                subgraph_indices, subgraph_values = calculate_distances_for_subgraph(labels,
                                                                                     adjacency_matrix,
                                                                                     subgraph_id)
                indices = indices + subgraph_indices
                values = values + subgraph_values
    else:
        # Calculate distances for each subgraph in parallel
        # Create and start threads for each subgraph
        threads = []
        # for subgraph_id in range(num_subgraphs):
        #     thread = Thread(target=calculate_distances_for_subgraph,
        #                     args=(labels,
        #                           adjacency_matrix,
        #                           subgraph_id))
        #     thread.start()
        #     threads.append(thread)

        # # Wait for all threads to complete
        # for thread in threads:
        #     thread.join()
        pass

    # print(indices, values)

    # Return a sparse tensor for storing the tokens' distance tensors/embeddings
    return tf.sparse.SparseTensor(indices=indices,
                                  values=values,
                                  dense_shape=[n, n, n])


def tensor_to_array(tensor):
    return tf.sparse.to_dense(tensor).numpy()


def get_tensor_slice(tensor, slice_index):
    # print("Getting slice for token ", slice_index)
    indices = tensor.indices.numpy()
    values = tensor.values.numpy()
    n = tensor.dense_shape.numpy()[0]
    new_indices = []
    new_values = []

    for i, index in enumerate(indices):
        if index[0] == slice_index:
            new_indices.append([index[1], index[2]])
            new_values.append(values[i])

    # print(new_indices, new_values)
    return tf.sparse.SparseTensor(indices=new_indices,
                                  values=new_values,
                                  dense_shape=[n, n])


def vectorize(adjacency_matrix, reversed_token_map, token_set):
    n = len(token_set)
    token_tensor = vectorize_adjacency_matrix(adjacency_matrix)

    # create a dictionary of all the tokens and their respective tensor embedding slices
    # print(token_tensor)
    token_vector_mappings = {reversed_token_map[i]: get_tensor_slice(token_tensor, i) for i in range(n)}

    for token in token_set:
        tok_vect_tensor = token_vector_mappings[token]

    # print(token_vector_mappings)

    return token_vector_mappings
