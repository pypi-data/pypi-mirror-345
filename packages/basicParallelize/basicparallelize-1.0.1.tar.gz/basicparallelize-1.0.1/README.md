# basicParallelize: A Basic Wrapper for Multiprocessing
***

``basicParallelize`` is designed to provide a user friendly wrapper for Python's multiprocessing library, including support for progress bars from [tqdm](https://github.com/tqdm/tqdm).

```python
    # Wrapper for multiprocessing.pool.ThreadPool
    from basicParallelize import multiThread
    output = multiThread(function, parameters)
```


```python
    # Wrapper for multiprocessing.Pool
    from basicParallelize import parallelProcess
    output = multiProcess(function, parameters)
```

Both core functions can be run with a built in progress bars by instead using `multiThreadTQDM` or `parallelProcessTQDM` respectively.

# Installation
------------
A recent version of Python 3 (3.8 or above) is required. You can probably run it or easily adapt it for older versions of Python, but I don't support any end-of-life Python versions. Beyond that, the only dependency is the `tqdm` library.

## Latest stable version on PyPi
`pip install basicParallelize`

## Latest stable version on GitHub
`pip install git+https://github.com/jBeale23/parallelize.git@stable`
