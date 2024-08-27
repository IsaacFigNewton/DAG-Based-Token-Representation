class DAGStore:
    def __init__(self,
                 vertices=None,
                 edge_set=None,
                 token_index_map=None,
                 adjacency_matrix=None):

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
