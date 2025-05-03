"""Very high level benchmarking contextmanager."""

import time
from collections import defaultdict
from contextlib import contextmanager
from statistics import mean, stdev
from typing import TYPE_CHECKING
from typing_extensions import deprecated

if TYPE_CHECKING:
    import pandas as pd


@deprecated("StopUhr is deprecated. Use Chronometer instead.")
class StopUhr:
    """Very high level benchmarking contextmanager.

    Example:
        Use a stateful timer to measure the time taken in a loop.
        This also supports the `printer` and `res` arguments.
        The `log` argument of each call can be used to suppress the output.

        .. code-block:: python

            >>> from stopuhr import StopUhr

            >>> stopuhr = StopUhr()

            >>> for i in range(5):
            >>>     with stopuhr("Sleeping", log=False):
            >>>         time.sleep(0.2)

            >>> # Print a summary with the mean and standard deviation of the durations.
            >>> stopuhr.summary()
            Sleeping took 0.20 ± 0.00 s (n=5 -> total=1.00s)

        The `reset`` command resets the state of the timer, note that this function is happening in-place.

        .. code-block:: python

            >>> stopuhr.reset()

        The previous behavior can be achieved with the `start` and `stop` methods.
        Here, the `stop` method also supports the `log` and `res` arguments.

        .. code-block:: python

            >>> for i in range(5):
            >>>     stopuhr.start("Sleeping")
            >>>     time.sleep(0.2)
            >>>     stopuhr.stop("Sleeping", log=False)

            >>> stopuhr.summary()
            Sleeping took 0.20 ± 0.00 s (n=5 -> total=1.00s)


        The stateful timer can also measure multiple durations at once.

        .. code-block:: python

            >>> stopuhr.reset()

            >>> # Single duration
            >>> with stopuhr("A (single 0.2s sleep)", log=False):
            >>>     time.sleep(0.2)

            >>> for i in range(5):
            >>>     with stopuhr("B (multiple 0.2s sleeps)", log=False):
            >>>         time.sleep(0.2)
            >>>     with stopuhr("C (multiple 0.1s sleeps)", log=False):
            >>>         time.sleep(0.1)

            >>> stopuhr.summary()
            A (single 0.2s sleep) took 0.20 s
            B (multiple 0.2s sleeps) took 0.20 ± 0.00 s (n=5 -> total=1.00s)
            C (multiple 0.1s sleeps) took 0.10 ± 0.00 s (n=5 -> total=0.50s)

    """

    def __init__(self, printer: callable = print):
        """StopUhr: a very high level benchmarking contextmanager.

        Args:
            printer (callable, optional): The function to print with. Defaults to print.

        """
        self.printer = printer
        self.reset()

    def reset(self):
        """Reset the durations."""
        self.durations: dict[str, list[float]] = defaultdict(list)
        self.idling_starts: dict[str, list[float]] = defaultdict(list)

    def export(self) -> "pd.DataFrame":
        """Export the durations as a pandas DataFrame.

        Returns:
            pd.DataFrame: A pandas DataFrame with the durations.

        """
        import pandas as pd

        # bring durations to same length
        durations = {}
        max_len = max(len(v) for v in self.durations.values())
        for key, values in self.durations.items():
            durations[key] = values + [pd.NA] * (max_len - len(values))

        return pd.DataFrame(durations)

    def summary(self, res: int = 2):
        """Print a summary of the durations.

        Args:
            res (int, optional): The number of decimal places to round to. Defaults to 2.

        """
        for key, values in self.durations.items():
            if not values:
                self.printer(f"{key} has no durations recorded")
                continue

            if len(values) == 1:
                self.printer(f"{key} took {values[0]:.{res}f}s")
                continue

            n = len(values)
            total = sum(values)
            mean_val = mean(values)
            stdev_val = stdev(values)
            self.printer(f"{key} took {mean_val:.{res}f} ± {stdev_val:.{res}f}s (n={n} -> {total=:.{res}f}s)")

    def start(self, msg: str):
        """Start the timer for a msg.

        Args:
            msg (str): The msg / key to store the start time under.

        """
        self.idling_starts[msg].append(time.perf_counter())

    def stop(self, key: str, res: int = 2, log: bool = True):
        """Stop the timer for a key.

        Args:
            key (str): The key to store the duration under.
            res (int, optional): The number of decimal places to round to. Defaults to 2.
            log (bool, optional): Whether to log the duration. Defaults to True.

        """
        end = time.perf_counter()
        try:
            start = self.idling_starts[key].pop(0)
        except IndexError as e:
            raise ValueError(f"Key '{key}' not started!") from e
        duration = end - start
        self.durations[key].append(duration)
        if log:
            self.printer(f"{key} took {duration:.{res}f}s")

    @contextmanager
    def __call__(self, key: str, res: int = 2, log: bool = True):
        """Context manager to measure the time taken in a block.

        Args:
            key (str): The key to store the duration under.
            res (int, optional): The number of decimal places to round to. Defaults to 2.
            log (bool, optional): Whether to log the duration. Defaults to True.

        """
        start = time.perf_counter()
        yield
        duration = time.perf_counter() - start
        self.durations[key].append(duration)
        if log:
            self.printer(f"{key} took {duration:.{res}f}s")


@contextmanager
@deprecated("stopuhr is deprecated. Use stopwatch instead.")
def stopuhr(msg: str, printer: callable = print, res: int = 2):
    """Context manager to measure the time taken in a block.

    Example:
        Stop the time with a simple context manager and print the duration.

        .. code-block:: python

            >>> import time

            >>> from stopuhr import stopuhr

            >>> with stopuhr("Sleeping"):
            >>>     time.sleep(0.1)
            Sleeping took 0.10s

        Instead of printing, one can pass any callable to the `printer` argument, e.g. a logger.

        .. code-block:: python

            >>> import logging

            >>> logger = logging.getLogger(__name__)
            >>> logger.setLevel(logging.INFO)
            >>> handler = logging.StreamHandler()
            >>> handler.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
            >>> logger.addHandler(handler)

            >>> with stopuhr("Sleeping", printer=logger.info):
            >>>     time.sleep(0.1)
            2025-03-27 19:11:10,912 - __main__ - INFO - Sleeping took 0.10s

        By default, the output is rounded to two decimal places. This can be changed with the `res` argument.

        .. code-block:: python

            >>> with stopuhr("Sleeping", res=3):
            >>>     time.sleep(0.16189)
            Sleeping took 0.162 s

    Args:
        msg (str): The message to print.
        printer (callable, optional): The function to print with. Defaults to print.
        res (int, optional): The number of decimal places to round to. Defaults to 2.

    """
    start = time.perf_counter()
    yield
    duration = time.perf_counter() - start
    printer(f"{msg} took {duration:.{res}f}s")


__all__ = ["StopUhr", "stopuhr"]
