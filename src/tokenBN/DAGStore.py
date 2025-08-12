class DAGStore:
    def __init__(self,
                 vertices=None,
                 edge_set=None,
                 token_index_map=None,
                 adjacency_matrix=None,
                 pattern_map=None):

        if vertices is None:
            vertices = dict()
        if edge_set is None:
            edge_set = set()

        self.vertices = vertices
        self.edge_set = edge_set
        self.token_index_map = token_index_map
        self.reversed_token_map = None
        # first dimension = outgoing token node
        # second dimension = incoming token node
        self.adjacency_matrix = adjacency_matrix

        if pattern_map is None:
            pattern_map = dict()
        self.pattern_map = pattern_map

    def add_edge(self, node, child):
        # Add an edge to the edge list, using the current token's position
        #   in the child token as the edge weight
        if node.token is not None and child.token is not None:
            self.edge_set.add((node.token, child.token, len(child.parents) - 1))
            self.adjacency_matrix[
                self.token_index_map[node.token], self.token_index_map[child.token]] = 1
        # else:
        #     print(f"Originating token: {node.token}\n Destination token: {child.token}")

    def add_pattern(self, pattern, token):
        if pattern in self.pattern_map:
            self.pattern_map[pattern].add(token)
        else:
            self.pattern_map[pattern] = set()
            self.pattern_map[pattern].add(token)
