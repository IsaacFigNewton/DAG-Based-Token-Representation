import sys
import os
import importlib

debugging_verbosity = {
    "SuffixNode": {
        "general": 0,
        "parallel": 0,
        "series": 0,
        "pruning": 1
    },
    "DAGNode": 0,
    "FlatTreeStore": 2
}

# freq_range = range(50, 1050, 50)
freq_range = range(2, 4, 2)
folds = 1
num_graphs_to_plot = 1
max_vector_plots = 0

# currently only works with single-character delimiters
delimiters = {" ", "\n"}   #r"\n",     #r"\n\n|.\n|\)\n|:|\.\.\."