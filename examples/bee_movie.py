import time
import urllib.request as url
from typing import Dict, List, Optional, Tuple, Any

import pandas as pd
import matplotlib.pyplot as plt

from tokenBN.config import DEBUG_VERBOSITY

from tokenBN.SuffixNode import SuffixNode
from tokenBN.CompositionDAGNode import CompositionDAGNode
from tokenBN.utils.figures import plot_dag

# Constants
TEST_URL = "https://gist.githubusercontent.com/Niximacco/6ae63abd1834485811200daefc319b40/raw/2411e31293a35f3e565f61e7490a806d4720ea7e/bee%2520movie%2520script"
TEST_TEXT_LENGTH = 200
MAX_VERTICES_FOR_PLOTTING = 100
DAG_PLOT_SCALING = 20
DAG_PLOT_K = 4
# freq_range for full script = range(50, 1050, 50)
FREQ_RANGE = range(2, 4, 2)
FOLDS = 2
NUM_GRAPHS_TO_PLOT = 1
MAX_VECTOR_PLOTS = 0
# currently only works with single-character delimiters
DELIMITERS = {" ", "\n"}

# Global state
tokenizations: Dict[Tuple[str, int], Any] = {}
test_results: Dict[str, List] = {
    "min frequency": [],
    "test number": [],
    "mean time": [],
}

def get_tests() -> List[str]:
    """Download and prepare test text data.
    
    Returns:
        List of test text strings.
    """
    try:
        with url.urlopen(TEST_URL) as f:
            text = f.read().decode('utf-8')
        
        text = text[:TEST_TEXT_LENGTH]
        tests = [text]
        
        print(f"Test text preview: {text[:50]}...")
        return tests
    except Exception as e:
        print(f"Error downloading test data: {e}")
        return ["Sample test text for fallback."]


def run_test(
    text: str,
    min_freq: int,
    delimiters: Optional[set] = None,
    suffix_tree: Optional[SuffixNode] = None,
    num_graphs_to_plot: int = 1
) -> Tuple[float, Any, Optional[SuffixNode]]:
    """Run a single test on the given text with specified parameters.
    
    Args:
        text: Input text to process
        min_freq: Minimum frequency threshold for tokens
        delimiters: Set of delimiter characters
        suffix_tree: Previously constructed tree to build upon
        num_graphs_to_plot: Number of DAG visualizations to generate
        
    Returns:
        Tuple of (execution_time, suffix_tree, token_vector_mappings)
    """
    start_time = time.time()
    if not suffix_tree:
        suffix_tree = SuffixNode.from_text(
            text=text,
            threshold=min_freq,
            delimiters=delimiters
        )
    else:
        suffix_tree.clean()
    tokenizations[(text, min_freq)] = suffix_tree.get_tokens()

    if DEBUG_VERBOSITY["SuffixNode"]["general"] > 0:
        elapsed = time.time() - start_time
        print(f"Modified suffix tree composed in {elapsed:.4f} seconds.")
        suffix_tree.print_tree()

    composition_dag = CompositionDAGNode()
    composition_dag.suffix_tree_to_dag(suffix_tree)

    if (
        num_graphs_to_plot > 0 
        and len(composition_dag.dag_store.vertices.keys()) < MAX_VERTICES_FOR_PLOTTING
    ):
        plot_dag(
            composition_dag.dag_store,
            A=composition_dag.dag_store.adjacency_matrix,
            k=DAG_PLOT_K,
            scaling=DAG_PLOT_SCALING
        )
        num_graphs_to_plot -= 1

    # Note: Vector embedding functionality is currently disabled
    # TODO: Re-enable vector embeddings when needed
    end_time = 0
    token_vector_mappings = None

    return end_time, suffix_tree, token_vector_mappings


def run_tests(tests: List[str]) -> None:
    """Run all tests across different frequency thresholds.
    
    Args:
        tests: List of test text strings to process
    """
    num_graphs_to_plot = 1
    prev_trees: Dict[int, Optional[Any]] = {}

    for min_freq in FREQ_RANGE:
        print(f"Testing minimum frequency: {min_freq}")

        for test_idx, test_text in enumerate(tests):
            if test_idx not in prev_trees:
                prev_trees[test_idx] = None

            total_time = 0.0
            for fold in range(FOLDS):
                execution_time, prev_trees[test_idx], _ = run_test(
                    text=test_text,
                    min_freq=min_freq,
                    delimiters=DELIMITERS,
                    suffix_tree=prev_trees[test_idx],
                    num_graphs_to_plot=num_graphs_to_plot
                )
                num_graphs_to_plot = max(0, num_graphs_to_plot - 1)
                total_time += execution_time

            mean_time = total_time / FOLDS
            test_results["min frequency"].append(min_freq)
            test_results["test number"].append(test_idx)
            test_results["mean time"].append(mean_time)

    print("\nAll tests completed.")


def plot_results() -> None:
    """Generate and display performance plots from test results."""
    if not test_results["min frequency"]:
        print("No test results to plot.")
        return
        
    tests_df = pd.DataFrame.from_dict(test_results)
    print("\nTest Results Summary:")
    print(tests_df.head())

    plt.figure(figsize=(10, 6))
    plt.plot(
        tests_df["min frequency"],
        tests_df["mean time"],
        marker='o',
        linewidth=2,
        markersize=6
    )
    
    plt.xscale('log')
    plt.yscale('log')
    plt.grid(True, alpha=0.3)
    
    plt.xlabel('Min Frequency (log scale)')
    plt.ylabel('Mean Time (log scale)')
    plt.title('Tokenization Performance vs Frequency Threshold')
    plt.tight_layout()
    plt.show()


def main() -> None:
    """Main execution function."""
    print("Starting DAG-based tokenization tests...")
    
    tests = get_tests()
    if not tests:
        print("No test data available. Exiting.")
        return
        
    run_tests(tests)
    plot_results()
    
    print("\nTokenization analysis complete.")


if __name__ == "__main__":
    main()