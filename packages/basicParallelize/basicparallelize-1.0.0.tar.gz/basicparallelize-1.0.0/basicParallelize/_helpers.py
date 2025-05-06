import inspect
from typing import Callable


def _determineMapType(function: Callable) -> bool:
    """Find if function expects at least two parameters and should be sent to a starmap.

    Parameters
    ----------
    function : Callable
        The function to check the number of required parameters for.

    Returns
    -------
    bool
        True if the input arguments have at least two dimensions, false if the input arguments have one dimension.
    """
    return len(inspect.signature(function).parameters) > 1


def _fStar(function: Callable, args) -> Callable:
    """Starmap a function with provided arguments.
    Used with TQDM variants of multiThreading and parallelProcess

    Parameters
    ----------
    function : Callable
        The function to pass arguments to.
    args : Iterable
        The arguments to unpack.

    Returns
    -------
    function(*args) : Callable
        The specified function with arguments unpacked and passed to it.
    """
    return function(*args)
