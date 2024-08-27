import os
import sys
from queue import Queue
import scipy.sparse as sp

from .FlatTreeStore import *
from .DAGStore import *


class CompositionDAGNode:
    def __init__(self,
                 token=None,
                 frequency=0,
                 parents=None,
                 flat_tree_store=None,
                 dag_store=None):
        self.token = token
        self.frequency = frequency

        if parents is None:
            parents = list()
        self.parents = parents

        if flat_tree_store is None:
            flat_tree_store = FlatTreeStore()
        self.flat_tree_store = flat_tree_store

        if dag_store is None:
            dag_store = DAGStore()
        self.dag_store = dag_store

    def __str__(self):
        child_tokens = {child.token for child in self.flat_tree_store.child_dict.values()}
        parent_tokens = {parent.token for parent in self.parents}
        return f"Token: {self.token}\nParents: {parent_tokens}\nChildren: {child_tokens}"

    # make an edge between the current token and a successor
    def add_edge(self, child):
        # Add the larger token as a child of this token
        # print(self.flat_tree_store.child_dict)
        self.flat_tree_store.child_dict[child.token] = child

        # Add this token to the list of parents composing the larger token
        child.parents.append(self)

        # Add an edge to the edge list, using the current token's position
        #   in the child token as the edge weight
        self.dag_store.edge_set.add((self.token, child.token, len(child.parents) - 1))
        if self.token is not None and child.token is not None:
            self\
                .dag_store\
                .adjacency_matrix[self.dag_store.token_index_map[self.token], self.dag_store.token_index_map[child.token]] = 1


    # since this is recursively saving smaller tokens, it's basically depth-first
    def build_subgraph(self, suffix_node=None, suffix_tokenization=[]):
      vertices = self.dag_store.vertices

      for token in suffix_tokenization:

        # if the predecessor token is not in the vertex store,
        #   recursively build a sub-graph of suffix tokens
        if token not in vertices.keys():
            # create a new dag node for the current token
            #   and put it in the vertex store
            vertices[token] = CompositionDAGNode(token=token,
                                                 frequency=suffix_node\
                                                              .flat_tree_store\
                                                              .child_dict[token]\
                                                              .frequency,
                                                 dag_store = self.dag_store)

            # break the missing token into even smaller tokens using the largest available smaller tokens
            curr_suffix_tokenization = suffix_node.flat_tree_store.tokenize(text=token,
                                                max_token_len=len(token) - 1)
            # build a subgraph from the smaller tokens
            temp_vert = vertices[token]
            temp_vert, additional_vertices = temp_vert.build_subgraph(suffix_node, curr_suffix_tokenization)
            vertices.update(additional_vertices)

            vertices[token] = temp_vert

        # base case: if the predecessor is in the vertex store
        #   add an edge from the current node's predecessor to it
        vertices[token].add_edge(self)

      return self, vertices


    # do breadth-first accumulation of the suffix tree into the dag
    def suffix_tree_to_dag(self, suffix_tree):
        print("Building DAG from modified suffix tree...")

        all_tokens = suffix_tree.get_tokens()
        print(f"Token set: {all_tokens}")

        # create a dict for mapping tokens to indices in the adjacency matrix
        token_list = list(all_tokens)
        self.dag_store.token_index_map = {token_list[i]: i for i in range(len(token_list))}
        self.dag_store.reversed_token_map = {v: k for k, v in self.dag_store.token_index_map.items()}
        # initialize the adjacency matrix in LIL format
        #   for more efficient memory usage during composition and later modifications
        self.dag_store.adjacency_matrix = sp.lil_matrix((len(all_tokens), len(all_tokens)))

        # print("lil adjacency matrix:\n", self.dag_store.adjacency_matrix)

        vertices = self.dag_store.vertices
        vertices[self.token] = self

        suffix_node_queue = Queue()
        suffix_node_queue.put(suffix_tree)

        while not suffix_node_queue.empty():
            # get the next suffix node from the queue
            current_suffix_node = suffix_node_queue.get()

            if current_suffix_node.token is not None and current_suffix_node.token not in all_tokens:
                raise KeyError("current_suffix_node.token not in all_tokens")

            # create a dag vertex and add it to the set of vertices
            vert = CompositionDAGNode(token=current_suffix_node.token,
                                      frequency=current_suffix_node.frequency,
                                      dag_store = self.dag_store)
            vertices[vert.token] = vert

            # if it's the root of the base dag or one of the top-level tokens, just add it to the vertex dict
            if current_suffix_node.parent is None or current_suffix_node.parent.token is None:
                vertices[current_suffix_node.token] = vert
                # add an edge from the base graph's root to the top-level token
                self.add_edge(vert)

            # otherwise, add edges
            else:
                # tokenize the current token using the largest available smaller tokens
                current_tokenization = current_suffix_node.flat_tree_store.tokenize(current_suffix_node.token,
                                                                    len(current_suffix_node.token) - 1)

                temp_vert = vert
                temp_vert, additional_vertices = temp_vert.build_subgraph(current_suffix_node, current_tokenization)
                vertices[vert.token] = temp_vert
                vertices.update(additional_vertices)

            # add all the current node's children to the queue
            for child_token in current_suffix_node.keys_to_my_children:
                suffix_node_queue.put(current_suffix_node.flat_tree_store.child_dict[child_token])

        if debugging and verbose["DAGNode"]:
            print("lil adjacency matrix after processing: ", self.dag_store.adjacency_matrix)

        # convert the LIL adjacency matrix to CSR format for more efficient modification
        self.dag_store.adjacency_matrix = sp.csr_matrix(self.dag_store.adjacency_matrix)

        if debugging and verbose["DAGNode"]:
            print("Sparse adjacency matrix:\n", self.dag_store.adjacency_matrix)

        self.dag_store.edge_set = {(pre, cum, pos) for pre, cum, pos in self.dag_store.edge_set if pre is not None}