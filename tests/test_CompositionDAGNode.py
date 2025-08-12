import unittest
import urllib.request as url

from tokenBN.SuffixNode import SuffixNode
from tokenBN.CompositionDAGNode import CompositionDAGNode

from tokenBN.utils.figures import plot_dag

class TestCompositionDAGNode(unittest.TestCase):
    def setUp(self):
        self.test_text = "abbabababba yogabbagabba"
        self.delimiters = {" ", "\n"}
        self.threshold = 2
        
        self.suffix_tree = SuffixNode.from_text(
            text=self.test_text,
            threshold=self.threshold,
            delimiters=self.delimiters
        )

    def test_add_edge(self):
        pass

    def test_build_subgraph(self):
        pass

    def test_suffix_tree_to_dag(self):
        pass

    def test_dag_to_file(self):
        test_url = "https://gist.githubusercontent.com/Niximacco/6ae63abd1834485811200daefc319b40/raw/2411e31293a35f3e565f61e7490a806d4720ea7e/bee%2520movie%2520script"
        with url.urlopen(test_url) as f:
            text = f.read().decode('utf-8')
        edge_ptr = ";"
        self.test_text = text.replace(edge_ptr, "")
        self.delimiters = {"\n"}
        self.threshold = 2
        self.suffix_tree = SuffixNode.from_text(
            text=self.test_text,
            threshold=self.threshold,
            delimiters=self.delimiters
        )

        dag = CompositionDAGNode()
        # start_time = time.time()
        dag.suffix_tree_to_dag(self.suffix_tree)

        # dag.export_dag(f"bee_movie min-freq={self.threshold}.csv")
        dag.export_dag(f"bee-movie text-patterns min-freq={self.threshold}.csv",
                       "patterns")

        if len(dag.dag_store.vertices.keys()) < 50:
            plot_dag(dag.dag_store,
                     A=dag.dag_store.adjacency_matrix,
                     k=4,
                     scaling=25)

        patterns_sample = {pattern: str(tokens)[:50]+"\n" for pattern, tokens in dag.dag_store.pattern_map.items()}
        print(f"Pattern set:\n{patterns_sample}")