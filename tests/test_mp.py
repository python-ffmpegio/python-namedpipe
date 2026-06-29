import multiprocessing as mp
from time import sleep

import namedpipe as npipe


# 1. The worker function executed by the child process
def worker_npopen(i):
    try:
        with npipe.NPopen() as pipe:
            sleep(1)
            return pipe.path
    except Exception as e:
        return e  # Pass exceptions back to the main process


# 2. The pytest function
def test_multiprocessing_npopen():
    # Use 'spawn' context to remain safe across OS platforms (Windows/macOS/Linux)
    ctx = mp.get_context("spawn")

    # Initialize the process
    nworkers = 4
    with ctx.Pool(nworkers) as pool:
        results = pool.map(worker_npopen, range(nworkers))

        # If the worker encountered an exception, reraise it in the test
        if result := next(
            (result for result in results if isinstance(result, Exception)), None
        ):
            raise result

        assert len(set(results)) == nworkers
