"""
AF Cluster to cluster and subsample MSAs

Code adapted from
https://github.com/HWaymentSteele/AF_Cluster/blob/main/scripts/ClusterMSA.py
"""

from typing import Iterable, List, Union
import numpy as np
import pandas as pd
from polyleven import levenshtein as _levenshtein
from sklearn.cluster import DBSCAN
from collections import Counter


def afcluster(
    msa: Union[List[str], pd.DataFrame, pd.Series],
    eps: float = None,
    min_samples: int = 3,
    columns: list = None,
    max_gap_frac: float = 0.25,
    resample: bool = False,
    resample_frac: float = 1.0,
    consensus_sequence: bool = True,
    levenshtein: bool = True,
    return_type: str = "dataframe",
    eps_range=(3, 20),
    eps_step=0.5,
    n_processes: int = 1,
    verbose: bool = False,
) -> Union[pd.DataFrame, List[pd.DataFrame]]:
    """
    Cluster an MSA using DBSCAN

    Parameters
    ----------
    msa : List or DataFrame or Series
        The MSA to cluster. This can be a list of (aligned) sequences, a pandas DataFrame with a "sequence" column, or a pandas Series containing sequences.
        In any case, the first sequence is interpreted as the query sequence.
    eps : float
        Epsilon value to use for DBSCAN.
        If none is provided, a gridsearch is performed to find the best value.
        For this, the eps_range and eps_step parameters are used.
    min_samples : int
        The minimum number of sequences in a cluster for the cluster to be accepted.
    columns : List[str]
        If a dataframe is passed, additional columns can also be included in the clustering.
        In these cases the columns must be numeric! By default, only the "sequence" column is used, any columns that are provided here are added to the clustering data.
    max_gap_frac : float
        Filter out sequences with more than this fraction of gaps.
        Set to 0 to remove all sequences with gaps, set to 1 to keep all sequences.
    resample : bool
        If True, resample the MSA with replacement.
    resample_frac : float
        If set to a value smaller than 1, the MSA will not only be resampled but also downscaled.
        Only used if resample is True.
    consensus_sequence : bool
        If True, compute the consensus sequence for each cluster and add it to the output dataframe as column "consensus_sequence".
    levenshtein : bool
        If True, compute the levenshtein distance to the query sequence and the consensus sequence for each cluster and add it to the output dataframe as columns "levenshtein_query" and "levenshtein_consensus".
    return_type : str
        The type of the return value. Can be "dataframe" or "list".
        If "dataframe", a single dataframe with all clusters is returned. Unclustered sequences have cluster_id -1.
        If "list", a list of dataframes, one for each cluster, is returned. Unclustered sequences are the final list element.
    eps_range : tuple
        The range of epsilon values to use for the gridsearch.
        Only used if eps is None.
    eps_step : float
        The step size for the gridsearch.
        Only used if eps is None.
    n_processes : int
        The number of processes to use for the gridsearch.
        Only used if eps is None.
    verbose : bool
        If True, print progress messages.
        If False, no messages are printed.

    Returns
    -------
    DataFrame or List
        The clustered MSA. If return_type is "dataframe", a single dataframe with all clusters is returned.
        If return_type is "list", a list of dataframes, one for each cluster, is returned.
    AFCluster : AFCluster
        The AFCluster object containing the clustering results. Which can be used to generate plots.
    """
    clusterer = AFCluster()

    if eps is None:
        eps = clusterer.gridsearch_eps(
            msa=msa,
            min_eps=eps_range[0],
            max_eps=eps_range[1],
            step=eps_step,
            data_frac=0.25,
            max_gap_frac=max_gap_frac,
            min_samples=min_samples,
            n_processes=n_processes,
        )
        if verbose:
            print(f"Best eps found: {eps}")

    out = clusterer.cluster(
        msa=msa,
        eps=eps,
        min_samples=min_samples,
        max_gap_frac=max_gap_frac,
        resample=resample,
        resample_frac=resample_frac,
        consensus_sequence=consensus_sequence,
        levenshtein=levenshtein,
        return_type=return_type,
        verbose=verbose,
    )

    return out, clusterer


class AFCluster:
    """
    Perform MSA Clustering using DBSCAN as described
    in [Wayment-Steele et al. (2024)](https://doi.org/10.1038/s41586-023-06832-9)
    """

    def __init__(self):
        self._eps = None
        self.df = None
        self.query = None

    def cluster(
        self,
        msa: Union[List[str], pd.DataFrame, pd.Series],
        eps: float = None,
        min_samples: int = 3,
        columns: List[str] = None,
        max_gap_frac: float = 0.25,
        resample: bool = False,
        resample_frac: float = 1.0,
        consensus_sequence: bool = True,
        levenshtein: bool = True,
        return_type: str = "dataframe",
        verbose: bool = False,
    ) -> Union[pd.DataFrame, List[pd.DataFrame]]:
        """
        Cluster an MSA using DBSCAN

        Parameters
        ----------
        msa : List or DataFrame or Series
            The MSA to cluster. This can be a list of (aligned) sequences, a pandas DataFrame with a "sequence" column, or a pandas Series containing sequences.
            In any case, the first sequence is interpreted as the query sequence.
        eps : float
            Epsilon value for DBSCAN clustering. If a search was done beforehand, the best value is remembered by the class.
        min_samples : int
            The minimum number of sequences in a cluster for the clsuter to be accepted.
        columns : List[str]
            If a dataframe is passed, additional columns can also be included in the clustering.
            In these cases the columns must be numeric!
        max_gap_frac : float
            The maximum fraction of gaps allowed in a sequence.
            Set to 0 to remove all sequences with gaps, set to 1 to keep all sequences.
        resample : bool
            If True, resample the MSA with replacement.
        resample_frac : float
            If set to a value smaller than 1, the MSA will not only be resampled but also downscaled.
            Only used if resample is True.
        consensus_sequence : bool
            If True, compute the consensus sequence for each cluster and add it to the output daraframe as column "consensus_sequence".
        levenshtein : bool
            If True, compute the levenshtein distance to the query sequence and the consensus sequence for each cluster and add it to the output dataframe as columns "levenshtein_query" and "levenshtein_consensus".
        return_type : str
            The type of the return value. Can be "dataframe" or "list".
            If "dataframe", a single dataframe with all clusters is returned. Unclustered sequences have cluster_id -1. The first row in the dataframe is the query sequence.
        If "list", a list of dataframes, one for each cluster, is returned. Unclustered sequences are the final list element. The first row in each cluster is the query sequence.

        Returns
        -------
        DataFrame or List
        """

        if verbose:
            report = print
        else:
            report = lambda *args, **kwargs: None

        if eps is None and self._eps is None:
            raise ValueError(
                "eps must be set. Either set it manually or use the gridsearch_eps method to find the best value."
            )
        elif eps is None:
            eps = self._eps

        report(f"Using eps={eps} for clustering")

        df = self._precheck_data(msa)
        old_len = len(df)
        query_seq, df = self._preprocess_data(
            df,
            max_gap_frac=max_gap_frac,
            resample=resample,
            resample_frac=resample_frac,
        )
        new_len = len(df)
        report(
            f"Resampled MSA from {old_len} to {new_len} sequences (resample={resample}, resample_frac={resample_frac}, max_gap_frac={max_gap_frac})"
        )

        if columns is not None:
            _df = df[["sequence"] + columns]
        else:
            _df = df[["sequence"]]

        labels = _run_dbscan(
            df=_df, eps=eps, min_samples=min_samples, query_length=len(query_seq)
        )
        df["cluster_id"] = labels

        report(f"Found {np.unique(labels).shape[0]-1} clusters")
        report(
            f"Found {np.sum(labels == -1)} unclustered sequences({np.sum(labels == -1) / len(labels) * 100:.2f}%)"
        )
        report(
            f"Found {np.sum(labels != -1)} clustered sequences ({np.sum(labels != -1) / len(labels) * 100:.2f}%)"
        )

        # insert the query sequence back as first row
        query_df = pd.DataFrame({"sequence": [query_seq], "cluster_id": [-1]})
        if "header" in df.columns:
            query_df["header"] = ["101"]

        df = pd.concat([query_df, df], ignore_index=True)
        df = df.reset_index(drop=True)

        if consensus_sequence:
            df = _make_consesus_sequences(df)

        if levenshtein:
            df = _compute_levenshtein_distance(clustered_df=df, query_seq=query_seq)

        self.query = query_seq
        self.df = df
        self._eps = eps
        return self.get(return_type=return_type)

    def get(self, return_type="dataframe"):
        """
        Get the clustering results

        Parameters
        ----------
        return_type : str
            The type of the return value. Can be "dataframe" or "list".
            If "dataframe", a single dataframe with all clusters is returned. Unclustered sequences have cluster_id -1. The first row in the dataframe is the query sequence.
            If "list", a list of dataframes, one for each cluster, is returned. Unclustered sequences are the final list element.
            The first row in each cluster is the query sequence.

        Returns
        -------
        DataFrame or List
            The clustered MSA. If return_type is "dataframe", a single dataframe with all clusters is returned.
            If return_type is "list", a list of dataframes, one for each cluster, is returned.
        """
        if self.df is None:
            raise ValueError("No clustering results to return, run `cluster` first!")
        if return_type not in ["dataframe", "list"]:
            raise ValueError(
                f"return_type must be 'dataframe' or 'list', got {return_type}"
            )

        if return_type == "dataframe":
            return self.df

        elif return_type == "list":
            df = self.df

            consensus_sequence = "consensus_sequence" in df.columns
            levenshtein = "levenshtein_query" in df.columns
            query_seq = self.query

            # Create a list of dataframes, one for each cluster
            clustered = df[df["cluster_id"] != -1]
            not_clustered = df[df["cluster_id"] == -1]

            clusters = []
            for cluster, cluster_df in clustered.groupby("cluster_id"):
                cluster_df = cluster_df.reset_index(drop=True)

                _query_df = pd.DataFrame(
                    {"sequence": [query_seq], "cluster_id": [cluster]}
                )

                if consensus_sequence:
                    _query_df["consensus_sequence"] = [
                        cluster_df["consensus_sequence"].values[0]
                    ]

                if levenshtein:
                    _query_df["levenshtein_query"] = 1
                    if consensus_sequence:
                        _query_df["levenshtein_consensus"] = [
                            1
                            - _levenshtein(
                                query_seq, cluster_df["consensus_sequence"].values[0]
                            )
                            / len(query_seq)
                        ]

                # add the query sequence as first row
                cluster_df = pd.concat(
                    [_query_df, cluster_df],
                    ignore_index=True,
                )
                cluster_df = cluster_df.reset_index(drop=True)
                clusters.append(cluster_df)

            # Add the unclustered sequences as the last element
            clusters.append(not_clustered)
            return clusters

    def gridsearch_eps(
        self,
        msa: Union[List[str], pd.DataFrame, pd.Series],
        desired_clusters: Union[str, int] = "max",
        min_eps: float = 3,
        max_eps: float = 20,
        step: float = 0.5,
        data_frac: float = 0.25,
        max_gap_frac: float = 0.25,
        min_samples: int = 3,
        n_processes: int = 1,
        mode: str = "fast",
    ) -> float:
        """
        Perform a grid search to find the best epsilon value for DBSCAN clustering.

        Parameters
        ----------
        msa : List or DataFrame or Series
            The MSA to cluster. This can be a list of (aligned) sequences, a pandas DataFrame with a "sequence" column, or a pandas Series containing sequences.
            In any case, the first sequence is interpreted as the query sequence.
        desired_clusters : str or int
            The desired number of clusters to obtain with the best epsilon value.
            If "max", the epsilon value that yields the maximum number of clusters is returned.
            If an integer is given, the epsilon value that yields this number of clusters (or the closest to it) is returned.
        min_eps : float
            The minimum epsilon value to test.
        max_eps : float
            The maximum epsilon value to test.
        step : float
            The step size for the grid search.
        data_frac : float
            The fraction of the data to use for the grid search.
        max_gap_frac : float
            The maximum fraction of gaps allowed in a sequence.
        min_samples : int
            The minimum number of sequences in a cluster for the cluster to be accepted.
        n_processes: int
            If a number bigger than 1 is given, the grid search is performed using
            multiprocessing. Otherwise, the grid search is performed using a single process.
        mode : str, optional
            The mode of grid search to perform. Can be "exhaustive" or "fast". Default is "exhaustive".
            Use "fast" for a faster search on large datasets that uses repeated sampling and averaging on a very small part of the data.

        Returns
        -------
        float
            The best epsilon value found during the grid search. This value is also stored in the class instance for later use with the cluster method.
        """
        from .search_eps import gridsearch

        df = self._precheck_data(msa)
        query_seq, df = self._preprocess_data(
            df, max_gap_frac=max_gap_frac, resample=False, resample_frac=0.0
        )
        # now take only every n-th row so that the df becomes size * data_frac
        if data_frac < 1:
            df = df[:: int(1 / data_frac)]

        if len(df) < 2:
            raise ValueError(
                "The MSA must contain at least 2 sequences to perform clustering."
            )
        if min_eps > max_eps:
            raise ValueError(
                "min_eps must be smaller than max_eps. Please check the values."
            )
        if step <= 0:
            raise ValueError("step must be greater than 0. Please check the value.")
        best_eps = gridsearch(
            df=df,
            query_seq=query_seq,
            min_eps=min_eps,
            max_eps=max_eps,
            step=step,
            desired_clusters=desired_clusters,
            min_samples=min_samples,
            n_processes=n_processes,
            mode=mode,
        )
        self._eps = best_eps
        return best_eps

    def pca(
        self,
        max_clusters_to_plot: int = 10,
        cmap: str = "tab10",
        size: int = 10,
        ax=None,
        figsize=None,
        inplace: bool = False,
        **kwargs,
    ):
        """
        Plot PCA of the clustering results.

        Parameters
        ----------
        max_clusters_to_plot : int, optional
            The maximum number of clusters to plot. If the number of clusters
            exceeds this, only the first `max_clusters_to_plot` clusters will be plotted individually, while all others are considered as "other".
        cmap : str, optional
            The colormap to use for the clusters.
        size : int, optional
            The size of the points in the plot.
        ax : matplotlib.axes.Axes, optional
            The axes to plot on. If None, a new figure and axes will be created.
        figsize : tuple, optional
            If a new figure is created, optionally specify the figure size.
        inplace : bool, optional
        If False, make a copy of the dataframe before computing PCA.
        **kwargs
            Additional keyword arguments to pass to the PCA function.
            See sklearn.decomposition.PCA for more details.

        Returns
        -------
        ax : matplotlib.axes.Axes
            The axes with the PCA plot.
        """
        if self.df is None:
            raise ValueError("No clustering results to plot, run `cluster` first!")
        from afcluster.visuals import pca

        return pca(
            self,
            max_clusters_to_plot=max_clusters_to_plot,
            cmap=cmap,
            size=size,
            ax=ax,
            figsize=figsize,
            inplace=inplace,
            **kwargs,
        )

    def tsne(
        self,
        max_clusters_to_plot: int = 10,
        cmap: str = "tab10",
        size: int = 10,
        ax=None,
        figsize=None,
        inplace: bool = False,
        **kwargs,
    ):
        """
        Plot t-SNE of the clustering results.

        Parameters
        ----------
        max_clusters_to_plot : int, optional
            The maximum number of clusters to plot. If the number of clusters
            exceeds this, only the first `max_clusters_to_plot` clusters will be plotted individually, while all others are considered as "other".
        cmap : str, optional
            The colormap to use for the clusters.
        size : int, optional
            The size of the points in the plot.
        ax : matplotlib.axes.Axes, optional
            The axes to plot on. If None, a new figure and axes will be created.
        figsize : tuple, optional
            If a new figure is created, optionally specify the figure size.
        inplace : bool, optional
        If False, make a copy of the dataframe before computing t-SNE.
        **kwargs
            Additional keyword arguments to pass to the t-SNE function.
            See sklearn.manifold.TSNE for more details.

        Returns
        -------
        ax : matplotlib.axes.Axes
            The axes with the t-SNE plot.
        """
        if self.df is None:
            raise ValueError("No clustering results to plot, run `cluster` first!")
        from afcluster.visuals import tsne

        return tsne(
            self,
            max_clusters_to_plot=max_clusters_to_plot,
            cmap=cmap,
            size=size,
            ax=ax,
            figsize=figsize,
            inplace=inplace,
            **kwargs,
        )

    def write_a3m(
        self,
        directory: str,
        prefix: str = "cluster_",
    ):
        """
        Write the clustered sequences to A3M files.

        Parameters
        ----------
        directory : str
            The directory to write the A3M files to.
        prefix : str
            The prefix for the A3M files.
        """
        from afcluster.utils import write_clusters_to_a3m

        if self.df is None:
            raise ValueError("No clustering results to write, run `cluster` first!")

        write_clusters_to_a3m(
            clusterer=self,
            directory=directory,
            prefix=prefix,
        )

    def write_cluster_table(
        self,
        filename: str,
    ):
        """
        Write the clustered sequences to a CSV file.

        Parameters
        ----------
        filename : str
            The name of the CSV file to write to.
        """
        from afcluster.utils import write_cluster_table

        if self.df is None:
            raise ValueError("No clustering results to write, run `cluster` first!")

        write_cluster_table(
            clusterer=self,
            filename=filename,
        )

    @staticmethod
    def _precheck_data(msa):
        if not isinstance(msa, (list, pd.DataFrame, pd.Series)):
            raise TypeError(
                f"msa must be of type list, DataFrame or Series, got ({type(msa)})"
            )
        if isinstance(msa, list):
            if not all(isinstance(seq, str) for seq in msa):
                raise TypeError(
                    "If msa is a list, it must contain only strings (sequences)."
                )
            df = pd.DataFrame({"sequence": msa})

        elif isinstance(msa, pd.DataFrame):
            if "sequence" not in msa.columns:
                raise ValueError(
                    "If msa is a DataFrame, it must contain a 'sequence' column."
                )
            df = msa
        elif isinstance(msa, pd.Series):
            if not all(isinstance(seq, str) for seq in msa):
                raise TypeError(
                    "If msa is a Series, it must contain only strings (sequences)."
                )
            df = pd.DataFrame({"sequence": msa})

        if len(df) < 3:
            raise ValueError(
                "The MSA must contain at least 2 sequences to perform clustering."
            )
        return df

    @staticmethod
    def _preprocess_data(df, max_gap_frac, resample, resample_frac):
        q = df.iloc[:1]["sequence"].values[0]
        df = df.iloc[1:]

        # remove insertions (lowercase)
        sequence_col_index = df.columns.get_loc("sequence")
        df.iloc[:, sequence_col_index] = df.iloc[:, sequence_col_index].str.replace(
            r"[a-z]", "", regex=True
        )

        if resample:
            df = df.sample(frac=resample_frac)

        # filter out gapped sequences
        if max_gap_frac < 1:
            gaps_fracs = df["sequence"].str.count("-") / len(q)
            df = df[gaps_fracs < max_gap_frac]
            df = df.reset_index(drop=True)

        if len(df) < 2:
            raise ValueError(
                "The MSA must contain at least 2 sequences to perform clustering."
            )
        return q, df

    __call__ = cluster

    def __repr__(self):
        return f"AFCluster(eps={self._eps})"


def _make_consesus_sequences(clustered_df):
    clustered_df["consensus_sequence"] = None
    for cluster, cluster_df in clustered_df.groupby("cluster_id"):
        consensus = _consensus_sequence(cluster_df["sequence"])
        clustered_df.loc[cluster_df.index, "consensus_sequence"] = consensus

    return clustered_df


def _compute_levenshtein_distance(clustered_df, query_seq):
    seq_length = len(query_seq)
    clustered_df["levenshtein_query"] = clustered_df["sequence"].apply(
        lambda x: 1 - _levenshtein(x, query_seq) / seq_length
    )

    if "consensus_sequence" in clustered_df.columns:
        clustered_df["levenshtein_consensus"] = None
        for cluster, cluster_df in clustered_df.groupby("cluster_id"):
            consensus = cluster_df["consensus_sequence"].iloc[0]
            distances = cluster_df["sequence"].apply(
                lambda x: 1 - _levenshtein(x, consensus) / seq_length
            )
            clustered_df.loc[cluster_df.index, "levenshtein_consensus"] = distances

    return clustered_df


DEFAULT_ENCODING = "onehot"
"""
The encoding method to use to turn the sequences into numeric vectors.
Can be "onehot" or "numvec".

"onehot" : One-hot encoding
    Each amino acid is represented by a vector of length 20, with a 1 in the position of the amino acid and 0s elsewhere.
    The sequence is padded with zeros to the right to make it of length max_len.
    The resulting array has shape (n_sequences, max_len * 20).
"numvec" : Numeric vector encoding
    Each amino acid is represented by a number from 1 to 20, with 21 for gaps, 0 for unknown/empty.
    The sequence is padded with zeros to the right to make it of length max_len.
    The resulting array has shape (n_sequences, max_len).
"""


def encode_clustering_data(
    df: pd.DataFrame,
    sequence_max_len: int = 108,
    sequence_encoding_method: str = None,
):
    """
    Encode the clustering data using the specified method.

    Parameters
    ----------
    df : pd.DataFrame
        The dataframe containing the sequences to encode.
    sequence_max_len : int
        The maximum length of the sequences.
    sequence_encoding_method : str
        The encoding method to use. Can be "onehot" or "numvec".
        The `DEFAULT_ENCODING` constant is used if method is None.

    Returns
    -------
    np.ndarray
        The encoded sequences.
    """
    encoded_sequences = encode_sequences(
        df["sequence"].values,
        max_len=sequence_max_len,
        method=sequence_encoding_method,
    )
    for col in df.columns:
        if col not in ("sequence", "cluster_id", "consensus_sequence", "header"):
            encoded_sequences = np.column_stack((encoded_sequences, df[col].values))
    return encoded_sequences


def encode_sequences(
    sequences: Iterable[str],
    max_len: int = 108,
    method: str = None,
):
    """
    Encode sequences using the specified method.

    Parameters
    ----------
    sequences : iterable of str
        The sequences to encode.
    max_len : int
        The maximum length of the sequences.
    method : str
        The encoding method to use. Can be "onehot" or "numvec".
        The `DEFAULT_ENCODING` constant is used if method is None.

    Returns
    -------
    np.ndarray
        The encoded sequences.
    """
    if method is None:
        method = DEFAULT_ENCODING
    if method == "onehot":
        return _seqs_to_onehot(sequences, max_len=max_len)
    elif method == "numvec":
        return _seqs_to_numvec(sequences, max_len=max_len)
    else:
        raise ValueError(f"Unknown encoding method: {method}")


def _run_dbscan(df, eps, min_samples, query_length) -> np.ndarray:
    encoded = encode_clustering_data(
        df,
        sequence_max_len=query_length,
    )

    clustering = DBSCAN(eps=eps, min_samples=min_samples or 2 * len(encoded[0])).fit(
        encoded,
    )

    return clustering.labels_


__amino_acid_alphabet__ = "ACDEFGHIKLMNPQRSTVWY-"


def _seqs_to_numvec(seqs, max_len=108):
    # Create a mapping of characters to indices
    char_to_index = {char: idx for idx, char in enumerate(__amino_acid_alphabet__)}

    # Initialize the one-hot encoded array
    arr = np.zeros((len(seqs), max_len), dtype=np.float32)

    for j, seq in enumerate(seqs):
        for i, char in enumerate(seq):
            if i >= max_len:
                break
            if char in char_to_index:
                arr[j, i] = char_to_index[char] + 1

    return arr


def _seqs_to_onehot(seqs, max_len=108):
    # Create a mapping of characters to indices
    char_to_index = {char: idx for idx, char in enumerate(__amino_acid_alphabet__)}

    # Initialize the one-hot encoded array
    arr = np.zeros((len(seqs), max_len, len(__amino_acid_alphabet__)), dtype=np.float32)

    for j, seq in enumerate(seqs):
        for i, char in enumerate(seq):
            if i >= max_len:
                break
            if char in char_to_index:
                arr[j, i, char_to_index[char]] = 1

    arr = arr.reshape(len(seqs), max_len * len(__amino_acid_alphabet__))
    return arr


def _consensus_sequence(seqs: pd.Series) -> str:
    """
    Compute the consensus sequence from a list of sequences.

    Parameters
    ----------
    seqs : pd.Series
        A pandas Series containing the sequences.

    Returns
    -------
    str
        The consensus sequence.
    """
    seqs = zip(*seqs)
    consensus = "".join(Counter(seq).most_common(1)[0][0] for seq in seqs)
    return consensus
