import multiprocessing
import multiprocessing.pool
import functools
from typing import Any, Callable, Iterable, List

import tqdm

from ._helpers import _determineMapType
from ._helpers import _fStar


def parallelProcessTQDM(
    function: Callable,
    args: Iterable[Any] | Iterable[Iterable[Any]],
    nJobs: int | None = None,
    chunkSize: int | None = None,
    overrideCPUCount: bool = False,
    description: str | None = None,
) -> List[Any]:
    """Creates a parallel pool with up to 'nJobs' processes to run a provided function on each element of an iterable.
    Displays a TQDM progress bar.

    Parameters
    ----------
    function: Callable
        The function to run in parallel.
    args: Iterable[Any] | Iterable[Iterable[Any]]
        An iterable of parameters to pass to the function.
        If the function requires more than one parameter, they must be provided in the form of an iterable of Iterables.
    nJobs: int | None
        The number of processes to start simultaneously.
        Capped by system CPU count and 61 to avoid bottlenecking and Windows errors respectively.
        See https://github.com/python/cpython/issues/71090 with respect to the possible Windows error.
        If unspecified, defaults to system logical CPU count.
    chunkSize: int | None
        The number of function executions on the iterable to pass to each process.
        If unspecified, defaults to heuristic calculation of divmod(len(args), nJobs * 4).
    overrideCPUCount: bool
        If set to True, the user provided nJobs is used as the number of threads to start simultaneously.
        This is done regardless of system resources available or possible Windows errors.
        Defaults to False.
    description: str | None
        If present, sets the string to display on the TQDM progress bar.

    Returns
    -------
    List
        The outputs of the specified function across the iterable, in the provided order.
    """

    if nJobs is None:
        nJobs: int = multiprocessing.cpu_count()
    if overrideCPUCount is True:
        nj: int = nJobs
    else:
        nj: int = min(nJobs, multiprocessing.cpu_count(), 61)

    if chunkSize is None:
        chunkSize, extra = divmod(len(args), nj * 4)
        if extra:
            chunkSize += 1

    with multiprocessing.Pool(processes=nj) as pool:
        print(f"Starting parallel pool with {nj} processes.".format(nj=nj))
        if _determineMapType(function) is True:
            result: List[Any] = list(
                tqdm.tqdm(
                    pool.imap(
                        func=functools.partial(_fStar, function),
                        iterable=args,
                        chunksize=chunkSize,
                    ),
                    total=len(args),
                    desc=description,
                )
            )
        else:
            result: List[Any] = list(
                tqdm.tqdm(
                    pool.imap(func=function, iterable=args, chunksize=chunkSize),
                    total=len(args),
                    desc=description,
                )
            )
    return result


def multiThreadTQDM(
    function: Callable,
    args: Iterable[Any] | Iterable[Iterable[Any]],
    nJobs: int | None = None,
    chunkSize: int | None = None,
    overrideCPUCount: bool = False,
    description: str | None = None,
) -> List[Any]:
    """Creates a parallel pool with up to 'nJobs' threads to run a provided function on each element of an iterable.
    Displays a TQDM progress bar.

    Parameters
    ----------
    function: Callable
        The function to run in parallel.
    args: Iterable[Any] | Iterable[Iterable[Any]]
        An iterable of parameters to pass to the function.
        If the function requires more than one parameter, they must be provided in the form of an iterable of Iterables.
    nJobs: int | None
        The number of threads to start simultaneously.
        Capped by system CPU count and 61 to avoid bottlenecking and Windows errors respectively.
        See https://github.com/python/cpython/issues/71090 with respect to the possible Windows error.
        If unspecified, defaults to system logical CPU count.
    chunkSize: int | None
        The number of function executions on the iterable to pass to each thread.
        If unspecified, defaults to heuristic calculation of divmod(len(args), nJobs * 4).
    overrideCPUCount: bool
        If set to True, the user provided nJobs is used as the number of threads to start simultaneously.
        This is done regardless of system resources available or possible Windows errors.
        Defaults to False.
    description: str | None
        If present, sets the string to display on the TQDM progress bar.

    Returns
    -------
    List
        The outputs of the specified function across the iterable, in the provided order.
    """

    if nJobs is None:
        nJobs: int = multiprocessing.cpu_count()

    if overrideCPUCount is True:
        nj: int = nJobs
    else:
        nj: int = min(nJobs, multiprocessing.cpu_count(), 61)
    if chunkSize is None:
        chunkSize, extra = divmod(len(args), nj * 4)
        if extra:
            chunkSize += 1

    with multiprocessing.pool.ThreadPool(processes=nj) as pool:
        print(f"Starting parallel pool with {nj} threads.".format(nj=nj))
        if _determineMapType(function) is True:
            result: List[Any] = list(
                tqdm.tqdm(
                    pool.imap(
                        func=functools.partial(_fStar, function),
                        iterable=args,
                        chunksize=chunkSize,
                    ),
                    total=len(args),
                    desc=description,
                )
            )
        else:
            result: List[Any] = list(
                tqdm.tqdm(
                    pool.imap(func=function, iterable=args, chunksize=chunkSize),
                    total=len(args),
                    desc=description,
                )
            )
    return result
