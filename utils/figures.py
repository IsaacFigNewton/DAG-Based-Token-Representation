from scipy.sparse.csgraph import connected_components
import scipy.sparse as sp
import tensorflow as tf
import math
import networkx as nx
import matplotlib.pyplot as plt
import seaborn as sns

from .vector_embedding import *


def plot_embeddings(embeddings, max_plots):
    if max_plots < 1:
        return

    i = 0
    for token, vector in embeddings.items():
        if i % max(len(embeddings) * int(i / max_plots), 1) == 0:
            print("Embedding for'" + token + "':")
            dense_vector = tensor_to_array(vector)
            # print("embedding string: ", vector)

            # Convert the vector to its dense representation and create the heatmap
            sns.heatmap(dense_vector, annot=False, cmap='viridis')

            # Display the heatmap
            plt.show()
            i += 1


def plot_dag(dag_store, A=None, scaling=50, edge_width=1, k=2):
    print("Adjacency matrix:\n", A)

    if A is None:
        print("Adjacency matrix was empty/not defined")

    # Create a directed graph from the adjacency matrix
    G = nx.from_numpy_array(A, create_using=nx.DiGraph)
    # Relabel the token nodes
    G = nx.relabel_nodes(G, dag_store.reversed_token_map)

    # # Draw the graph without edge labels
    # # Convert nodes to strings before calculating length
    # nx.draw(G, with_labels=True, node_size=[scaling * len(str(node)) for node in G.nodes()],
    #         width=edge_width, font_size=8)

    # Calculate figure size based on the number of nodes
    num_nodes = len(G.nodes)
    num_edges = len(G.edges)
    graph_size = (num_nodes) + (2 * num_edges)

    figsize = graph_size * scaling / 300
    font_size = 2 + math.sqrt(scaling) / 5
    # Calculate node sizes based on the length of the token text
    node_sizes = [scaling * len(node) for node in G.nodes()]

    # Position nodes using the spring layout
    pos = nx.spring_layout(G, seed=42, k=k / num_nodes)
    plt.figure(figsize=(figsize, figsize), dpi=300)

    # Draw nodes with sizes proportional to the length of their text
    nx.draw_networkx_nodes(G, pos, node_size=node_sizes)
    # Draw edges with widths based on edge weights
    nx.draw_networkx_edges(G,
                           pos,
                           width=edge_width,
                           arrowstyle='-|>',
                           connectionstyle="arc3,rad=0.2")
    # Draw node labels
    nx.draw_networkx_labels(G, pos, font_size=font_size, font_family="sans-serif")

    # # Draw edge weight labels
    # edge_labels = nx.get_edge_attributes(G, "weight")
    # nx.draw_networkx_edge_labels(G, pos, edge_labels)

    # Customize and show plot
    ax = plt.gca()
    ax.margins(0.08)
    plt.axis("off")
    plt.tight_layout()

    plt.show()
