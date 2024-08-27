import sys
import os
import importlib

debugging = True
verbose = {
    "SuffixNode": False,
    "DAGNode": False,
    "FlatTreeStore": False
}

# freq_range = range(50, 1050, 50)
freq_range = range(2, 4, 2)
folds = 1
num_graphs_to_plot = 1
max_vector_plots = 0
tokenizations = dict()
test_results = {
    "min frequency": [],
    "test number": [],
    "mean time": [],
}

# currently only works with single-character delimiters
delimiters = {" ", "\n"}   #r"\n",     #r"\n\n|.\n|\)\n|:|\.\.\."
parallelize_composition = False