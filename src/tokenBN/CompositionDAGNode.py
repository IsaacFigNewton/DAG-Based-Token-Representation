from collections import deque
import scipy.sparse as sp

from tokenBN.config import DEBUG_VERBOSITY

from .FlatTreeStore import *
from .DAGStore import *


class CompositionDAGNode:
    def __init__(self,
                 token=None,
                 frequency=0,
                 parents=None,
                 flat_tree_store=None,
                 dag_store=None,
                 pattern=None):
        self.token = token
        self.frequency = frequency
        self.pattern = pattern

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
        self.dag_store.add_edge(self, child)

    def get_pattern(self, tokenization):
        # map each token to a value based on its order of occurrence
        component_tokens = dict()
        i = 0
        for token in tokenization:
            if token not in component_tokens:
                component_tokens[token] = str(i)
                i += 1

        # add the pattern to the current node and the pattern store
        self.pattern = " ".join([component_tokens[token] for token in tokenization])
        self.dag_store.add_pattern(self.pattern, self.token)

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
                                                     frequency=suffix_node \
                                                     .flat_tree_store \
                                                     .child_dict[token] \
                                                     .frequency,
                                                     dag_store=self.dag_store)

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
        if DEBUG_VERBOSITY["DAGNode"] > -1:
            print("Building DAG from modified suffix tree...")

        all_tokens = suffix_tree.get_tokens()
        if DEBUG_VERBOSITY["DAGNode"] > -1:
            print(f"Token set: {str(all_tokens)[:100]}")

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

        suffix_node_queue = deque()
        suffix_node_queue.append(suffix_tree)

        while 0 < len(suffix_node_queue):
            if DEBUG_VERBOSITY["DAGNode"] > 1:
                print(f"SuffixNode DAG Queue state: {[node.token for node in suffix_node_queue]}")

            # get the next suffix node from the queue
            current_suffix_node = suffix_node_queue.popleft()
            if current_suffix_node.token is not None and current_suffix_node.token not in all_tokens:
                raise KeyError(f"{current_suffix_node.token} not in token set {all_tokens}")

            # create a dag vertex and add it to the set of vertices
            vert = CompositionDAGNode(token=current_suffix_node.token,
                                      frequency=current_suffix_node.frequency,
                                      dag_store=self.dag_store)
            vertices[vert.token] = vert

            # if it's the root of the base dag or one of the top-level tokens, just add it to the vertex dict
            if current_suffix_node.parent is None or current_suffix_node.parent.token is None:
                vert.get_pattern([vert.token])
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
                temp_vert.get_pattern(current_tokenization)

                vertices[vert.token] = temp_vert
                vertices.update(additional_vertices)

            # add all the current node's children to the queue
            for child_token in current_suffix_node.keys_to_my_children:
                if DEBUG_VERBOSITY["DAGNode"] > 1:
                    print(f"SuffixNode DAG Queue state: {[node.token for node in suffix_node_queue]}")
                suffix_node_queue.append(current_suffix_node.flat_tree_store.child_dict[child_token])

        if DEBUG_VERBOSITY["DAGNode"] > 1:
            print("lil adjacency matrix after processing: ", self.dag_store.adjacency_matrix)
        # convert the LIL adjacency matrix to CSR format for more efficient modification
        self.dag_store.adjacency_matrix = sp.csr_matrix(self.dag_store.adjacency_matrix)
        if DEBUG_VERBOSITY["DAGNode"] > 1:
            print("Sparse adjacency matrix:\n", self.dag_store.adjacency_matrix)

        self.dag_store.edge_set = {(pre, cum, pos) for pre, cum, pos in self.dag_store.edge_set if pre is not None}

    # converts the edge set and vertex set to a file format for Gephi
    def export_dag(self, filename, output):
        path = "graphs/" + filename
        # clear the file
        with open(path, 'w') as f:
            f.write("")

        vertices = self.dag_store.vertices
        lines = set()
        with open(path, 'a') as f:
            for edge in self.dag_store.edge_set:
                if output == "tokens":
                    lines.add("{edge[0]};{edge[1]}")
                else:
                    vert0 = vertices[edge[0]]
                    vert1 = vertices[edge[1]]
                    if output == "patterns":
                        lines.add(f"{vert0.pattern};{vert1.pattern}")

            f.write("\n".join(lines))
