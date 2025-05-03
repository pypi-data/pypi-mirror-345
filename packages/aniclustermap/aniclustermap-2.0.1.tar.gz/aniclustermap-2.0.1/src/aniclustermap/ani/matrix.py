from __future__ import annotations

import csv
import re
from pathlib import Path

import pandas as pd
from seaborn.matrix import ClusterGrid


def parse_ani_matrix(matrix_file: str | Path) -> pd.DataFrame:
    """Parse ANI matrix as Dataframe

    Parameters
    ----------
    matrix_file : str | Path
        fastANI or skani all-vs-all ANI matrix file

    Returns
    -------
    df : pd.DataFrame
        Dataframe of ANI matrix
    """
    names: list[str] = []
    ani_values_list: list[list[float]] = []
    with open(matrix_file) as f:
        reader = csv.reader(f, delimiter="\t")
        genome_num = int(next(reader)[0].rstrip("\n"))
        for row in reader:
            name = Path(row[0]).with_suffix("").name
            name = re.sub("\\.fna$", "", name)
            names.append(name)
            ani_values = list(map(lambda d: 0.0 if d == "NA" else float(d), row[1:]))
            ani_values.extend([0] * (genome_num - len(ani_values)))
            ani_values_list.append(ani_values)

    df = pd.DataFrame(data=ani_values_list, columns=names, index=names, dtype="float64")
    for i in range(genome_num):
        df.iat[i, i] = 100
    for i, name in enumerate(names):
        for j, d in enumerate(df[name][i:]):
            df.iat[i, i + j] = d
    return df


def get_clustered_matrix(original_df: pd.DataFrame, g: ClusterGrid) -> pd.DataFrame:
    """Get clustered ANI matrix

    Parameters
    ----------
    original_df : pd.DataFrame
        Original dataframe before clustering
    g : ClusterGrid
        Cluster grid (`clustermap` return value)

    Returns
    -------
    df : pd.DataFrame
        Clustered matrix dataframe
    """
    clustered_row_index = original_df.index[g.dendrogram_row.reordered_ind]
    clustered_col_index = original_df.columns[g.dendrogram_col.reordered_ind]
    return original_df.loc[clustered_row_index, clustered_col_index]  # type: ignore
