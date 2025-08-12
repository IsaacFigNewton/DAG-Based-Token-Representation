from tokenBN.utils.figures import plot_embeddings, plot_dag
from tokenBN.utils.util import count_occurrences, compile_regex
from tokenBN.utils.vector_embedding import (
    calculate_distances_for_subgraph,
    vectorize_adjacency_matrix,
    tensor_to_array,
    get_tensor_slice,
    vectorize
)