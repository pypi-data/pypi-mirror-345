from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import scipy.cluster.hierarchy as hc


def to_newick_tree(
    ani_matrix_df: pd.DataFrame,
    linkage: np.ndarray,
    newick_file: str | Path,
):
    """Convert ANI cluster result to newick tree

    Parameters
    ----------
    ani_matrix_df : pd.DataFrame
        ANI matrix dataframe
    linkage : np.ndarray
        Cluster linkage
    newick_file : str | Path
        Output newick file
    """
    tree = hc.to_tree(linkage)
    if isinstance(tree, hc.ClusterNode):
        with open(newick_file, "w") as f:
            leaf_names = list(map(str, ani_matrix_df.columns))
            f.write(dendrogram2newick(tree, tree.dist, leaf_names))
    else:
        raise ValueError("Invalid hierarchy cluster detected!!")


def dendrogram2newick(
    node: hc.ClusterNode, parent_dist: float, leaf_names: list[str], newick: str = ""
) -> str:
    """Convert scipy dendrogram tree to newick format tree

    Parameters
    ----------
    node : ClusterNode
        Tree node
    parent_dist : float
        Parent distance
    leaf_names : list[str]
        Leaf names
    newick : str, optional
        Newick format string (Used in recursion)

    Returns
    -------
    newick : str
        Newick format tree
    """
    if node.is_leaf():
        return f"{leaf_names[node.id]}:{(parent_dist - node.dist):.2f}{newick}"
    else:
        if len(newick) > 0:
            newick = f"):{(parent_dist - node.dist):.2f}{newick}"
        else:
            newick = ");"
        if node.left is None or node.right is None:
            raise ValueError
        newick = dendrogram2newick(node.left, node.dist, leaf_names, newick)
        newick = dendrogram2newick(node.right, node.dist, leaf_names, f",{newick}")
        newick = f"({newick}"
        return newick
