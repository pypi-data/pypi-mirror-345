"""
PCA and t-SNE visualizations for clustering results.
"""

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE

from .af_cluster import AFCluster, _seqs_to_onehot


def pca(
    clusterer: AFCluster,
    max_clusters_to_plot: int = 10,
    cmap: str = "tab10",
    size: int = 10,
    ax=None,
    figsize=None,
    inplace: bool = False,
    **kwargs,
) -> plt.Axes:
    """
    Plot PCA of the clustering results.

    Parameters
    ----------
    clusterer : AFCluster
        The AFCluster object containing the clustering results.
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

    if ax is None:
        new_figure = True
        fig, ax = plt.subplots(figsize=figsize)
    else:
        new_figure = False

    # plot PCA
    ax = _plot_pca(
        clusterer.df.copy() if not inplace else clusterer.df,
        ax=ax,
        max_clusters_to_plot=max_clusters_to_plot,
        cmap=cmap,
        size=size,
        **kwargs,
    )

    if new_figure:
        fig.tight_layout()
        sns.despine(trim=True, ax=ax)
    return ax


def tsne(
    clusterer: AFCluster,
    max_clusters_to_plot: int = 10,
    cmap: str = "tab10",
    size: int = 10,
    ax=None,
    figsize=None,
    inplace: bool = False,
    **kwargs,
) -> plt.Axes:
    """
    Plot t-SNE of the clustering results.

    Parameters
    ----------
    clusterer : AFCluster
        The AFCluster object containing the clustering results.
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

    if ax is None:
        new_figure = True
        fig, ax = plt.subplots(figsize=figsize)
    else:
        new_figure = False
    # plot t-SNE
    ax = _plot_tsne(
        clusterer.df.copy() if not inplace else clusterer.df,
        ax=ax,
        max_clusters_to_plot=max_clusters_to_plot,
        cmap=cmap,
        size=size,
        **kwargs,
    )

    if new_figure:
        fig.tight_layout()
        sns.despine(trim=True, ax=ax)
    return ax


def _plot_pca(
    df,
    ax=None,
    max_clusters_to_plot: int = 10,
    cmap: str = "tab10",
    size: int = 10,
    **kwargs,
):
    # prepare sequences
    query = df.iloc[:1]
    df = df.iloc[1:]
    seqs_onehot = _seqs_to_onehot(
        df["sequence"].values,
        max_len=len(query["sequence"].values[0]),
    )

    # PCA
    kwargs.pop("random_state", None)
    kwargs.setdefault("n_components", 2)
    pca = PCA(random_state=42, **kwargs)
    embedding = pca.fit_transform(seqs_onehot)

    df["PC 1"] = embedding[:, 0]
    df["PC 2"] = embedding[:, 1]

    query_onehot = _seqs_to_onehot(
        query["sequence"].values,
        max_len=len(query["sequence"].values[0]),
    )
    query_embedding = pca.transform(query_onehot)
    query["PC 1"] = query_embedding[:, 0]
    query["PC 2"] = query_embedding[:, 1]

    # plot
    if ax is None:
        new_figure = True
        fig, ax = plt.subplots()
    else:
        new_figure = False

    unclustered = df[df["cluster_id"] == -1]
    clustered = df[df["cluster_id"] != -1]

    ax.scatter(
        unclustered["PC 1"],
        unclustered["PC 2"],
        color="lightgray",
        marker="x",
        label="unclustered",
        s=size,
    )

    # get the top max_clusters_to_plot clusteres
    cluster_sizes = clustered["cluster_id"].value_counts()
    cluster_sizes.sort_values(ascending=False, inplace=True)
    clusters_to_plot = cluster_sizes[:max_clusters_to_plot]
    clusters_to_plot = clusters_to_plot.index

    other_clustered = clustered[~clustered["cluster_id"].isin(clusters_to_plot)]

    ax.scatter(
        other_clustered["PC 1"],
        other_clustered["PC 2"],
        color="darkgray",
        marker="x",
        label="other clusters",
        s=size,
    )

    # plot clusters
    clustered = clustered[clustered["cluster_id"].isin(clusters_to_plot)]

    sns.scatterplot(
        x="PC 1",
        y="PC 2",
        hue="cluster_id",
        data=clustered,
        palette=cmap,
        ax=ax,
        s=size,
    )
    ax.scatter(
        query["PC 1"],
        query["PC 2"],
        color="red",
        marker="*",
        s=size * 5,
        label="query",
    )
    ax.legend(bbox_to_anchor=(1, 1), frameon=False)
    ax.set(
        xlabel="PC 1",
        ylabel="PC 2",
    )
    if new_figure:
        fig.tight_layout()
        sns.despine(trim=True, ax=ax)
    return ax


def _plot_tsne(
    df,
    ax=None,
    max_clusters_to_plot: int = 10,
    cmap: str = "tab10",
    size: int = 10,
    **kwargs,
):
    if ax is None:
        new_figure = True
        fig, ax = plt.subplots()
    else:
        new_figure = False

    # prepare sequences
    seqs_onehot = _seqs_to_onehot(
        df["sequence"].values,
        max_len=len(df["sequence"].values[0]),
    )
    # t-SNE
    kwargs.pop("random_state", None)
    tsne = TSNE(random_state=42, **kwargs)

    embedding = tsne.fit_transform(seqs_onehot)
    df["t-SNE 1"] = embedding[:, 0]
    df["t-SNE 2"] = embedding[:, 1]

    query = df.iloc[:1]
    df = df.iloc[1:]

    # plot
    unclustered = df[df["cluster_id"] == -1]
    clustered = df[df["cluster_id"] != -1]

    ax.scatter(
        unclustered["t-SNE 1"],
        unclustered["t-SNE 2"],
        color="lightgray",
        marker="x",
        label="unclustered",
        s=size,
    )

    # get the top max_clusters_to_plot clusteres
    cluster_sizes = clustered["cluster_id"].value_counts()
    cluster_sizes.sort_values(ascending=False, inplace=True)
    clusters_to_plot = cluster_sizes[:max_clusters_to_plot]
    clusters_to_plot = clusters_to_plot.index

    other_clustered = clustered[~clustered["cluster_id"].isin(clusters_to_plot)]
    ax.scatter(
        other_clustered["t-SNE 1"],
        other_clustered["t-SNE 2"],
        color="darkgray",
        marker="x",
        label="other clusters",
        s=size,
    )

    # plot clusters
    clustered = clustered[clustered["cluster_id"].isin(clusters_to_plot)]

    sns.scatterplot(
        x="t-SNE 1",
        y="t-SNE 2",
        hue="cluster_id",
        data=clustered,
        palette=cmap,
        ax=ax,
        s=size,
    )

    ax.scatter(
        query["t-SNE 1"],
        query["t-SNE 2"],
        color="red",
        marker="*",
        s=size * 5,
        label="query",
    )
    ax.legend(bbox_to_anchor=(1, 1), frameon=False)
    ax.set(
        xlabel="t-SNE 1",
        ylabel="t-SNE 2",
    )

    if new_figure:
        fig.tight_layout()
        sns.despine(trim=True, ax=ax)
    return ax
