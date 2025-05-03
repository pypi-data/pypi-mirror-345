import numpy as np
import pandas as pd
from .af_cluster import _run_dbscan


def gridsearch(
    df,
    query_seq,
    desired_clusters="max",
    min_eps=3,
    max_eps=20,
    step=0.5,
    min_samples=3,
    early_stop=-1,
    n_processes=1,
    mode="fast",
    **kwargs,
) -> float:
    """
    Perform a grid search to find the best epsilon value for DBSCAN from a given range.

    Parameters
    ----------
    df : pd.DataFrame
        The DataFrame containing the data to be clustered (must contain a "sequence" column)
    query_seq : str
        The query sequence to be used for clustering.
    desired_clusters : int or str, optional
        The desired number of clusters. If "max", the maximum number of clusters will be used.
    min_eps : float, optional
        The minimum epsilon value to start the search from. Default is 3.
    max_eps : float, optional
        The maximum epsilon value to end the search at. Default is 20.
    step : float, optional
        The step size for the epsilon values. Default is 0.5.
    min_samples : int, optional
        The minimum number of samples for a cluster to be accepted. Default is 3.
    n_processes : int, optional
        The number of processes to use for parallel processing. Default is 1 (no parallel processing).
    early_stop : int, optional
        Since DBSCAN converges to a single cluster for large eps values, this parameter allows you to stop the search if the number of clusters is 1 for this many consecutive eps values. Default is -1 (no early stopping).
    mode : str, optional
        The mode of grid search to perform. Can be "exhaustive" or "fast". Default is "exhaustive".
        Use "fast" for a faster search on large datasets that uses repeated sampling and averaging on a very small part of the data.
    **kwargs : additional keyword arguments
        Additional keyword arguments for the specific grid search method.

    Returns
    -------
    best_eps : float
        The best epsilon value found during the search.
    """

    if mode == "exhaustive":
        return gridsearch_exhaustive(
            df,
            query_seq,
            desired_clusters=desired_clusters,
            min_eps=min_eps,
            max_eps=max_eps,
            step=step,
            min_samples=min_samples,
            early_stop=early_stop,
            n_processes=n_processes,
            **kwargs,
        )

    elif mode == "fast":
        return gridsearch_fast(
            df,
            query_seq,
            desired_clusters=desired_clusters,
            min_eps=min_eps,
            max_eps=max_eps,
            step=step,
            min_samples=min_samples,
            n_processes=n_processes,
            early_stop=early_stop,
            **kwargs,
        )

    else:
        raise ValueError("Invalid mode. Choose 'exhaustive' or 'fast'.")


def gridsearch_exhaustive(
    df,
    query_seq,
    desired_clusters="max",
    min_eps=3,
    max_eps=20,
    step=0.5,
    min_samples=3,
    n_processes=1,
    early_stop=-1,
    **kwargs,
) -> float:
    """
    Perform an exhaustive grid search to find the best epsilon value for DBSCAN from a given range.

    Parameters
    ----------
    df : pd.DataFrame
        The DataFrame containing the data to be clustered (must contain a "sequence" column)
    query_seq : str
        The query sequence to be used for clustering.
    desired_clusters : int or str, optional
        The desired number of clusters. If "max", the maximum number of clusters will be used.
    min_eps : float, optional
        The minimum epsilon value to start the search from. Default is 3.
    max_eps : float, optional
        The maximum epsilon value to end the search at. Default is 20.
    step : float, optional
        The step size for the epsilon values. Default is 0.5.
    min_samples : int, optional
        The minimum number of samples for a cluster to be accepted. Default is 3.
    n_processes : int, optional
        The number of processes to use for parallel processing. Default is 1 (no parallel processing).
    early_stop : int, optional
        Since DBSCAN converges to a single cluster for large eps values, this parameter allows you to stop the search if the number of clusters is 1 for this many consecutive eps values. Default is -1 (no early stopping).

    Returns
    -------
    best_eps : float
        The best epsilon value found during the search.
    """
    return _core_gridsearch(
        df,
        query_seq,
        desired_clusters=desired_clusters,
        min_eps=min_eps,
        max_eps=max_eps,
        step=step,
        min_samples=min_samples,
        n_processes=n_processes,
        noise=0.0,
        early_stop=early_stop,
    )


def gridsearch_fast(
    df,
    query_seq,
    desired_clusters="max",
    min_eps=3,
    max_eps=20,
    step=0.5,
    min_samples=3,
    n_processes=1,
    noise=2,
    early_stop=3,
    fraction=0.05,
    alpha=1.5,
    n_repeats=15,
    **kwargs,
) -> float:
    """
    Perform a grid search to find the best epsilon value for DBSCAN from a given range, using a fraction of the data.
    This repeatedly samples a small fraction of the data and takes the average of the resulting epsilon values.
    To account for the downscaled data the epsilon value is multiplied by a factor (alpha) which is linked to the noise parameter
    and is empirical.

    Parameters
    ----------
    df : pd.DataFrame
        The DataFrame containing the data to be clustered (must contain a "sequence" column)
    query_seq : str
        The query sequence to be used for clustering.
    desired_clusters : int or str, optional
        The desired number of clusters. If "max", the maximum number of clusters will be used.
    min_eps : float, optional
        The minimum epsilon value to start the search from. Default is 3.
    max_eps : float, optional
        The maximum epsilon value to end the search at. Default is 20.
    step : float, optional
        The step size for the epsilon values. Default is 0.5.
    min_samples : int, optional
        The minimum number of samples for a cluster to be accepted. Default is 3
    n_processes : int, optional
        The number of processes to use for parallel processing. Default is 1 (no parallel processing).
    noise : float, optional
        The amount of noise to add to the epsilon values. Default is 0.0 (no noise).
    early_stop : int, optional
        Since DBSCAN converges to a single cluster for large eps values, this parameter allows you to stop the search if the number of clusters is 1 for this many consecutive eps values. Default is 3.
    fraction : float, optional
        The fraction of the data to sample for each iteration. Default is 0.05 (5% of the data).
    alpha : float, optional
        The factor to multiply the epsilon value by to account for the downscaled data. Default is 1.5.
    n_repeats : int, optional
        The number of times to repeat the sampling and epsilon calculation. Default is 15.

    Returns
    -------
    best_eps : float
        The best epsilon value found during the search.
    """

    eps_values = [0] * n_repeats
    for _ in range(n_repeats):
        _df = df.sample(frac=fraction)
        eps = _core_gridsearch(
            _df,
            query_seq,
            desired_clusters=desired_clusters,
            min_eps=min_eps,
            max_eps=max_eps,
            step=step,
            min_samples=min_samples,
            n_processes=n_processes,
            early_stop=early_stop,
            noise=noise,
        )
        eps *= alpha  # empirical is linked to the noise parameter
        eps_values[_] = eps
    eps = np.mean(eps_values)
    return eps


def _core_gridsearch(
    df,
    query_seq,
    desired_clusters="max",
    min_eps=3,
    max_eps=20,
    step=0.5,
    min_samples=3,
    n_processes=1,
    noise=0.0,
    early_stop=3,
):
    eps_values = np.arange(min_eps, max_eps + step, step)
    if noise > 0:
        eps_values += np.random.random(len(eps_values)) * (1 + noise)

    if n_processes > 1:
        from concurrent.futures import ThreadPoolExecutor, as_completed
        import os

        if n_processes > os.cpu_count():
            n_processes = os.cpu_count()
        if n_processes > len(eps_values):
            n_processes = len(eps_values)

        args = [(df, eps, min_samples, len(query_seq)) for eps in eps_values]

        def run_dbscan(args):
            df, eps, min_samples, query_length = args
            labels = _run_dbscan(
                df=df, eps=eps, min_samples=min_samples, query_length=query_length
            )
            return eps, np.unique(labels).shape[0]

        best_eps = None

        with ThreadPoolExecutor(max_workers=n_processes) as executor:
            futures_to_eps = {
                executor.submit(run_dbscan, arg): eps
                for arg, eps in zip(args, eps_values)
            }
            results = [(..., 9999)] * len(eps_values)
            got_only_one = 0
            for idx, future in enumerate(as_completed(futures_to_eps)):
                eps, num_clusters = future.result()
                results[idx] = (eps, num_clusters)
                if num_clusters == desired_clusters:
                    best_eps = eps
                    break
                if num_clusters == 1:
                    got_only_one += 1
                else:
                    got_only_one = 0

                if got_only_one == early_stop:
                    print(
                        f"Warning: {eps} resulted in only one cluster, aborting search for higher values..."
                    )
                    break

            executor.shutdown(cancel_futures=True, wait=True)

        if best_eps is not None:
            return best_eps
        results = [i[1] for i in results]
    else:
        got_only_one = 0
        results = [999] * len(eps_values)
        for idx, eps in enumerate(eps_values):
            labels = _run_dbscan(
                df=df, eps=eps, min_samples=min_samples, query_length=len(query_seq)
            )
            results[idx] = np.unique(labels).shape[0]

            if results[idx] == desired_clusters:
                return eps

            if results[idx] == 1:
                got_only_one += 1
            else:
                got_only_one = 0

            if got_only_one == early_stop and idx > len(eps_values) // 3:
                print(
                    f"Warning: {eps=} resulted in only one cluster, aborting search for higher values..."
                )
                break

    # Find the best epsilon value
    if desired_clusters == "max":
        best_eps_index = np.argmax(results)
    else:
        results = np.array(results)
        best_eps_index = np.argmin(np.abs(results - desired_clusters))
        if results[best_eps_index] == 1:
            raise ValueError(
                f"No clusters found for eps={eps_values[best_eps_index]}. Please try a different range of eps values."
            )
    best_eps = eps_values[best_eps_index]
    return best_eps
