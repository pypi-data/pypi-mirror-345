"""Very high level benchmarking contextmanager."""

import time
from collections import defaultdict
from collections.abc import Callable
from contextlib import contextmanager
from inspect import Signature, signature
from statistics import mean, stdev
from typing import TYPE_CHECKING, Any, Literal

if TYPE_CHECKING:
    import pandas as pd


# Pritner signature
Printer = Callable[[str], None]


def _get_bound_args(sig: Signature, *args, **kwargs) -> dict[str, Any]:
    # Create a dictionary to store parameter bindings
    bound_args = {}

    # Bind positional arguments
    for arg_name, arg_value in zip(sig.parameters.keys(), args):
        bound_args[arg_name] = arg_value

    # Add keyword arguments
    for key, value in kwargs.items():
        if key in sig.parameters:
            bound_args[key] = value

    # Fill in default values for missing parameters
    for param_name, param in sig.parameters.items():
        if param_name not in bound_args and param.default != param.empty:
            bound_args[param_name] = param.default

    return bound_args


class Chronometer:
    """Very high level benchmarking contextmanager and decorator.

    Example:
        Measure the time taken in a code block.

        .. code-block:: python

            >>> import stopuhr

            >>> timer = stopuhr.Chronometer()
            >>> with timer("Sleeping"):
            >>>     time.sleep(0.2)

        Instead of printing, one can pass any callable to the `printer` argument, e.g. a logger.

        .. code-block:: python

            >>> import logging

            >>> logger = logging.getLogger(__name__)
            >>> logger.setLevel(logging.INFO)
            >>> handler = logging.StreamHandler()
            >>> handler.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
            >>> logger.addHandler(handler)

            >>> timer = stopuhr.Chronometer(printer=logger.info)
            >>> with timer("Sleeping"):
            >>>     time.sleep(0.1)
            2025-03-27 19:11:10,912 - __main__ - INFO - Sleeping took 0.10s

        The printer can be overridden for each call.

        .. code-block:: python

            >>> timer = stopuhr.Chronometer(printer=logger.info)
            >>> with timer("Sleeping", printer=logger.debug):
            >>>     time.sleep(0.1)
            2025-03-27 19:11:10,912 - __main__ - DEBUG - Sleeping took 0.10s

        By default, the output is rounded to two decimal places. This can be changed with the `res` argument.
        The `res` argument can also be overridden for each call.

        .. code-block:: python

            >>> timer = stopuhr.Chronometer(res=3)
            >>> with timer("Sleeping"):
            >>>     time.sleep(0.16189)
            Sleeping took 0.162 s

            >>> with timer("Sleeping", res=2):
            >>>     time.sleep(0.16189)
            Sleeping took 0.16 s

        The chronometer is stateful and can be used to measure functions inside a loop.
        The `log` argument of each call can be used to suppress the output.
        It can also be set individually for each call.

        .. code-block:: python

            >>> timer = stopuhr.Chronometer(log=False)

            >>> for i in range(5):
            >>>     with timer("Sleeping"):
            >>>         time.sleep(0.2)

            >>> # Print a summary with the mean and standard deviation of the durations.
            >>> timer.summary()
            Sleeping took 0.20 ± 0.00 s (n=5 -> total=1.00s)

        The `reset` command resets the state of the timer, note that this function is happening in-place.

        .. code-block:: python

            >>> timer.reset()

        The previous behavior can be achieved with the `start` and `stop` methods.
        Here, the `stop` method also supports the `log` and `res` arguments.

        .. code-block:: python

            >>> for i in range(5):
            >>>     timer.start("Sleeping")
            >>>     time.sleep(0.2)
            >>>     timer.stop("Sleeping", log=False)

            >>> timer.summary()
            Sleeping took 0.20 ± 0.00 s (n=5 -> total=1.00s)


        The stateful timer can also measure multiple durations at once.

        .. code-block:: python

            >>> timer.reset()

            >>> # Single duration
            >>> with timer("A (single 0.2s sleep)", log=False):
            >>>     time.sleep(0.2)

            >>> for i in range(5):
            >>>     with timer("B (multiple 0.2s sleeps)", log=False):
            >>>         time.sleep(0.2)
            >>>     with timer("C (multiple 0.1s sleeps)", log=False):
            >>>         time.sleep(0.1)

            >>> timer.summary()
            A (single 0.2s sleep) took 0.20 s
            B (multiple 0.2s sleeps) took 0.20 ± 0.00 s (n=5 -> total=1.00s)
            C (multiple 0.1s sleeps) took 0.10 ± 0.00 s (n=5 -> total=0.50s)

        The `export` method can be used to export the durations as a pandas DataFrame.

        .. code-block:: python

            >>> import pandas as pd

            >>> timer.reset()

            >>> for i in range(5):
            >>>     with timer("Sleeping", log=False):
            >>>         time.sleep(0.2)
            >>> for i in range(3):
            >>>     with timer("Sleeping-2", log=False):
            >>>         time.sleep(0.2)

            >>> df = timer.export()
            >>> print(df)
              Sleeping-2  Sleeping
            0  0.2         0.2
            1  0.2         0.2
            2  0.2         0.2
            3  0.2
            4  0.2

    """

    def __init__(self, printer: Printer = print, res: int = 2, log: bool = True):
        """StopUhr: a very high level benchmarking contextmanager.

        Args:
            printer (Callable[[str], None], optional): The objects default function to print to.
                This can be a logger function, e.g. `logger.info`, the normal `print` statement,
                or any other function which receives exactly one string as input.
                Output methods may overwrite this default.
                Defaults to print.
            res (int, optional): The default number of decimal places to round to in the output.
                Output methods may overwrite this default.
                Defaults to 2.
            log (bool, optional): Whether to log the duration at occurence.
                Setting this to `False` will not output anything,
                it will only add the message and the duration to the objects state as usual.
                Output methods may overwrite this default.
                Defaults to True.

        """
        self.printer = printer
        self.res = res
        self.log = log
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

    def merge(self, other: "Chronometer"):
        """Merge the durations of another Chronometer into this one.

        This is handy for multiprocessing situations.

        Does not merge the idling_starts, only the durations.

        Args:
            other (Chronometer): The Chronometer to merge with.
                This Chronometer will be modified in-place.
                The other Chronometer will not be modified.

        """
        assert isinstance(other, Chronometer), "other must be a Chronometer"

        for key, values in other.durations.items():
            self.durations[key].extend(values)

    @staticmethod
    def combine(*timers: "Chronometer") -> "Chronometer":
        """Combine multiple Chronometers into one.

        This is handy for multiprocessing situations.

        Args:
            *timers (Chronometer): The Chronometers to combine.
                The new Chronometer will be created with the same printer, res and log settings as the first one.

        Returns:
            Chronometer: A new Chronometer with the combined durations.

        """
        # Check if the first input is a list of Chronometers
        if isinstance(timers[0], list):
            timers = timers[0]
        assert all(isinstance(t, Chronometer) for t in timers), "all timers must be Chronometers"
        assert len(timers) > 0, "at least one timer must be provided"

        combined = Chronometer(printer=timers[0].printer, res=timers[0].res, log=timers[0].log)
        for timer in timers:
            combined.merge(timer)

        return combined

    def summary(self, res: int | None = None, printer: Printer | None = None):
        """Print a summary of the durations.

        Args:
            res (int | None, optional): Override the objects default number of decimal places to round to if not None.
                Defaults to None.
            printer (Callable[[str], None] | None, optional): Override the objects function to print with if not None.
                 Defaults to None.

        """
        res = res or self.res
        printer = printer or self.printer
        for key, values in self.durations.items():
            if not values:
                printer(f"{key} has no durations recorded")
                continue

            if len(values) == 1:
                printer(f"{key} took {values[0]:.{res}f}s")
                continue

            n = len(values)
            total = sum(values)
            mean_val = mean(values)
            stdev_val = stdev(values)
            printer(f"{key} took {mean_val:.{res}f} ± {stdev_val:.{res}f}s (n={n} -> {total=:.{res}f}s)")

    def start(self, key: str):
        """Start the timer for a msg.

        Args:
            key (str): The msg / key to store the start time under.

        """
        self.idling_starts[key].append(time.perf_counter())

    def stop(self, key: str, res: int | None = None, log: bool | None = None, printer: Printer | None = None):
        """Stop the timer for a key.

        Args:
            key (str): The key to store the duration under.
            res (int | None, optional): Override the objects default number of decimal places to round to if not None.
                Defaults to None.
            log (bool | None, optional): Override the objects default log setting if not None.
                Defaults to None.
            printer (Callable[[str], None] | None, optional): Override the objects function to print with if not None.
                 Defaults to None.

        """
        res = res or self.res
        log = log if log is not None else self.log
        printer = printer or self.printer
        end = time.perf_counter()
        try:
            start = self.idling_starts[key].pop(0)
        except IndexError as e:
            raise ValueError(f"Key '{key}' not started!") from e
        duration = end - start
        self.durations[key].append(duration)
        if log:
            printer(f"{key} took {duration:.{res}f}s")

    def f(
        self,
        key: str,
        res: int | None = None,
        log: bool | None = None,
        printer: Printer | None = None,
        print_kwargs: list[str] | Literal["all"] | None = "all",
    ):
        """Advanced decorator to also print the function arguments.

        Instead of just passing the normal `{key} took {duration:.{res}f}s` message,
        this decorator will also add the function arguments to the message.

        This behaviour is not possible to implement with the `@contextmanager` decorator,
        hence the need for this separate decorator.

        Args:
            key (str): The key to store the duration under.
            res (int | None, optional): Override the objects default number of decimal places to round to if not None.
                Defaults to None.
            log (bool | None, optional): Override the objects default log setting if not None.
                Defaults to None.
            printer (Callable[[str], None] | None, optional): Override the objects function to print with if not None.
                 Defaults to None.
            print_kwargs (list[str] | bool, optional): The arguments to be added to the `key`.
                If a list, only the arguments in the list will be added to the message.
                If True, all arguments will added. If False, no arguments will be added.
                Additions to the message will have the form: f"{key} (with {arg1=val1, arg2=val2, ...})".
                Defaults to False.

        Raises:
            ValueError: If any of the print_kwargs are not in the functions signature.

        """
        res = res or self.res
        log = log if log is not None else self.log
        printer = printer or self.printer

        def _decorator(func):
            func_signature = signature(func)
            # Check if any of the print_kwargs are not in the functions signature and raise an error if so
            if isinstance(print_kwargs, list) and any(
                k not in func_signature.parameters for k in print_kwargs if isinstance(print_kwargs, list)
            ):
                raise ValueError(
                    f"Not all {print_kwargs=} found in {func_signature.parameters=} of function {func.__name__}"
                )

            def _inner(*args, **kwargs):
                _inner_key = key

                if isinstance(print_kwargs, list):
                    bound_args = _get_bound_args(func_signature, *args, **kwargs)
                    # Check if any of the print_kwargs are not in bound_args and raise an error if so
                    if any(k not in bound_args for k in print_kwargs):
                        raise ValueError(f"Not all {print_kwargs=} found in {bound_args=} of function {func.__name__}")

                    # Filter by print_kwargs
                    bound_args = {k: bound_args[k] for k in print_kwargs if k in bound_args}
                    # Make a string of it and add it to the message
                    bound_args_msg = ", ".join(f"{k}={v}" for k, v in bound_args.items())
                    _inner_key += f" (with {bound_args_msg})"
                elif print_kwargs:
                    bound_args = _get_bound_args(func_signature, *args, **kwargs)
                    # Make a string of it and add it to the message
                    bound_args_msg = ", ".join(f"{k}={v}" for k, v in bound_args.items())
                    _inner_key += f" (with {bound_args_msg})"

                with self(_inner_key, res=res, log=log):
                    return func(*args, **kwargs)

            return _inner

        return _decorator

    @contextmanager
    def __call__(
        self,
        key: str,
        res: int | None = None,
        log: bool | None = None,
        printer: Printer | None = None,
    ):
        """Context manager and decorator to measure the time taken in a block or function.

        Args:
            key (str): The key to store the duration under.
            res (int | None, optional): Override the objects default number of decimal places to round to if not None.
                Defaults to None.
            log (bool | None, optional): Override the objects default log setting if not None.
                Defaults to None.
            printer (Callable[[str], None] | None, optional): Override the objects function to print with if not None.
                 Defaults to None.

        """
        self.start(key)
        yield
        self.stop(key, res=res, log=log, printer=printer)


stopwatch = Chronometer()

__all__ = ["Chronometer", "stopwatch"]
