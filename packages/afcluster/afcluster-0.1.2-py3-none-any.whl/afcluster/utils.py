"""
Other utility functions for the afcluster package.
"""

from .af_cluster import AFCluster, _consensus_sequence
import pandas as pd
from pathlib import Path


def read_a3m(filename: str) -> pd.DataFrame:
    """
    Read an A3M file and return a DataFrame with the sequences.

    Parameters
    ----------
    filename : str
        The name of the A3M file to read.

    Returns
    -------
    pd.DataFrame
        A DataFrame containing the sequences from the A3M file.
    """
    seqs = []
    headers = []
    with open(filename, "r") as f:
        for line in f:
            if line.startswith(">"):
                headers.append(line.strip())
            else:
                seqs.append(line.strip())
    return pd.DataFrame({"header": headers, "sequence": seqs})


def write_cluster_table(
    clusterer: AFCluster,
    filename: str,
):
    """
    Write the cluster table to a file. This will contain averaged
    data for each cluster, including the consensus sequence and
    Levenshtein distances (if computed). One row per cluster.

    Parameters
    ----------
    clusterer : AFCluster
        The AFCluster object containing the clustering results.
    filename : str
        The name of the file to write the cluster table to.
    """
    if clusterer.df is None:
        raise ValueError("No clustering results to write, run `cluster` first!")

    final = {colname: [] for colname in clusterer.df.columns}
    final["size"] = []
    final.pop("sequence")
    has_consensus = "consensus_sequence" in clusterer.df.columns
    has_levenshtein_query = "levenshtein_query" in clusterer.df.columns
    has_levenshtein_consensus = "levenshtein_consensus" in clusterer.df.columns

    for cluster_id, group in clusterer.df.groupby("cluster_id"):
        final["cluster_id"].append(cluster_id)
        final["size"].append(len(group))

        if not has_consensus:
            consensus = _consensus_sequence(group["sequence"].values)
        else:
            consensus = group["consensus_sequence"].values[0]
        final["consensus_sequence"].append(consensus)

        if has_levenshtein_query:
            final["levenshtein_query"].append(group["levenshtein_query"].mean())
        if has_levenshtein_consensus:
            final["levenshtein_consensus"].append(group["levenshtein_consensus"].mean())

        for colname in group.columns:
            if colname in (
                "size",
                "cluster_id",
                "consensus_sequence",
                "sequence",
                "levenshtein_query",
                "levenshtein_consensus",
            ):
                continue
            col = group[colname]
            if col.dtype == "object":
                final[colname].append(col.values[0])
            else:
                final[colname].append(col.mean())

    # write
    final = pd.DataFrame(final)
    final.to_csv(filename, index=False)


def write_clusters_to_a3m(
    clusterer: AFCluster,
    directory: str,
    prefix: str = "cluster_",
):
    """
    Write the clusters to a directory in A3M format. Each cluster will be
    written to a separate file, with the filename being the cluster ID.

    Parameters
    ----------
    clusterer : AFCluster
        The AFCluster object containing the clustering results.
    directory : str
        The directory to write the A3M files to.
    prefix : str, optional
        The prefix for the filenames. Default is "cluster_".
    """
    if clusterer.df is None:
        raise ValueError("No clustering results to write, run `cluster` first!")

    Path(directory).mkdir(parents=True, exist_ok=True)

    query = clusterer.df.iloc[:1]
    query_str = f">query\n{query['sequence'].values[0]}\n"
    df = clusterer.df.iloc[1:]

    for cluster_id, group in df.groupby("cluster_id"):
        if cluster_id == -1:
            cluster_id = "outliers"
        with open(f"{directory}/{prefix}{cluster_id}.a3m", "w") as f:
            f.write(query_str)
            for sdx, seq in enumerate(group["sequence"].values):
                f.write(f">{sdx}\n{seq}\n")
