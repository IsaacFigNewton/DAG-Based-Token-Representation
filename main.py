import time
import warnings

import pandas as pd

from config import *
from modules.SuffixNode import *
from modules.CompositionDAGNode import *
from utils.util import *
from utils.figures import *
from utils.vector_embedding import *

def get_tests():
    # test_url = "https://courses.cs.washington.edu/courses/cse163/20wi/files/lectures/L04/bee-movie.txt"
    # with url.urlopen(test_url) as f:
    #     text = f.read().decode('utf-8')
    # # previously 454:500
    # text = text[454:500]
    # # text = text[0:500]
    text = "black. Yellow, black.\n :\nOoh, black and yellow"
    text = "abbabababba yogabbagabba"
    tests = [text]

    print(text[:50])
    return tests


def run_test(text,
             min_freq,
             delimiters=None,
             tree=None,
             parallelize=True,
             num_graphs_to_plot=1):

    start_time = time.time()
    suffix_tree, tokenizations[(text, min_freq)] = get_suffix_tree(text,
                                                                   min_freq,
                                                                   delimiters=delimiters,
                                                                   tree=tree,
                                                                   parallelize=parallelize)

    if debugging_verbosity["SuffixNode"]["general"] > 0:
        print("Modified suffix tree composed in ", time.time() - start_time, " seconds.")
        suffix_tree.print_tree()

    composition_dag = CompositionDAGNode()
    # start_time = time.time()
    composition_dag.suffix_tree_to_dag(suffix_tree)
    # end_time = time.time() - start_time
    # print("dag composed in ", end_time, " seconds.")

    if num_graphs_to_plot > 0:
        plot_dag(composition_dag.dag_store,
                 A=composition_dag.dag_store.adjacency_matrix,
                 k=4,
                 scaling=25)

        num_graphs_to_plot -= 1

    # get tensor embeddings for all vertices
    start_time = time.time()
    token_vector_mappings = vectorize(composition_dag.dag_store.adjacency_matrix,
                                      composition_dag.dag_store.reversed_token_map,
                                      tokenizations[(text, min_freq)])
    end_time = time.time() - start_time

    # return {(pre, cum, pos+1) for pre, cum, pos in composition_dag.dag_store.edge_set if pre is not None}
    return end_time, suffix_tree, token_vector_mappings, num_graphs_to_plot


def run_tests():
    num_graphs_to_plot = 1
    prev_trees = dict()

    for min_freq in freq_range:
        print("minimum frequency: ", min_freq)

        for i in range(len(tests)):
            # print("test ", i)
            # if there's no previous tree stored for this test
            if i not in prev_trees.keys():
                prev_trees[i] = None

            mean_time = 0
            for fold in range(folds):
                new_time = 0
                new_time, prev_trees[i], token_vector_mappings, _ = run_test(text=tests[i],
                                                                          min_freq=min_freq,
                                                                          delimiters=delimiters,
                                                                          tree=prev_trees[i],
                                                                          parallelize=parallelize_composition,
                                                                          num_graphs_to_plot=num_graphs_to_plot)
                num_graphs_to_plot -= 1
                mean_time += new_time

            # plot_embeddings(token_vector_mappings, max_vector_plots)

            test_results["min frequency"].append(min_freq)
            test_results["test number"].append(i)
            test_results["mean time"].append(mean_time / folds)

    print()


if __name__ == "__main__":
    # warnings.filterwarnings('ignore')

    tests = get_tests()
    run_tests()

    tests_df = pd.DataFrame.from_dict(test_results)
    print(tests_df.head())

    plt.plot(tests_df["min frequency"],
             tests_df["mean time"]
             )

    plt.xscale('log')
    plt.yscale('log')

    plt.xlabel('Min Frequency (log scale)')
    plt.ylabel('Mean Time (log scale)')
    # plt.show()