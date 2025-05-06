"""Wrappers for the multiprocessing module's Pool and ThreadPool classes
Includes an implementation of TQDM progress bars for both wrappers.
"""

__all__ = ["parallelProcess", "parallelProcessTQDM", "multiThread", "multiThreadTQDM"]
__version__ = "1.0.0"
__author__ = "Joshua Beale <jbeale2023@gmail.com>"

from ._parallelize import multiThread
from ._parallelize import parallelProcess

from ._parallelizeTQDM import multiThreadTQDM
from ._parallelizeTQDM import parallelProcessTQDM
