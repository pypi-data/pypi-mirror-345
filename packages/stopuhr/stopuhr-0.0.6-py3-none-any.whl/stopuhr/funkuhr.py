"""Very high level benchmarking decorator."""

from collections.abc import Callable
from inspect import Signature, signature
from typing import TYPE_CHECKING, Any, Literal
from typing_extensions import deprecated

from stopuhr.stopuhr import StopUhr, stopuhr

if TYPE_CHECKING:
    import pandas as pd


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


@deprecated("FunkUhr is deprecated. Use Chronometer instead.")
class FunkUhr:
    """Very high level benchmarking decorator.

    Wraps the `StopUhr` class to provide a decorator for benchmarking functions.

    Example:
        A stateful decorator exists as well, which is just a wrapper around the stateful timer.
        It supports the same arguments as the stateful timer.

        .. code-block:: python

            >>> from stopuhr import FunkUhr

            >>> funkuhr = FunkUhr()

            >>> @funkuhr("Busy Function", log=False)
            >>> def busy_function():
            >>>     time.sleep(0.1)

            >>> for i in range(5):
            >>>     busy_function()

            >>> funkuhr.summary()
            Busy Function took 0.10 ± 0.00 s (n=5 -> total=0.50s)

        Like the stateless decorator, it is possible to add arguments to the message.

        .. code-block:: python

            >>> from stopuhr import FunkUhr

            >>> funkuhr = FunkUhr()

            >>> @funkuhr("Busy Function", print_kwargs=["arg1", "arg2"])
            >>> def busy_function(arg1, arg2, arg3):
            >>>     time.sleep(0.1)

            >>> for i in range(5):
            >>>     busy_function(1, 2, 3)

            >>> funkuhr.summary()
            Busy Function took 0.10 ± 0.00 s (n=5 -> total=0.50s) (with arg1=1, arg2=2)

        It is also possible to add all arguments to the message.

        .. code-block:: python

            >>> from stopuhr import FunkUhr

            >>> funkuhr = FunkUhr()

            >>> @funkuhr("Busy Function", print_kwargs=True)
            >>> def busy_function(arg1, arg2):
            >>>     time.sleep(0.1)

            >>> for i in range(5):
            >>>     busy_function(1, 2)

            >>> funkuhr.summary()
            Busy Function took 0.10 ± 0.00 s (n=5 -> total=0.50s) (with arg1=1, arg2=2)

    """

    def __init__(self, printer: callable = print):
        """FunkUhr: a very high level benchmarking decorator.

        Args:
            printer (callable, optional): The function to print with. Defaults to print.

        """
        self.stopuhr = StopUhr(printer)

    def export(self) -> "pd.DataFrame":
        """Export the durations as a pandas DataFrame.

        Returns:
            pd.DataFrame: A pandas DataFrame with the durations.

        """
        return self.stopuhr.export()

    def summary(self, res: int = 2):
        """Print a summary of the durations.

        Args:
            res (int, optional): The number of decimal places to round to. Defaults to 2.

        """
        self.stopuhr.summary(res)

    def __call__(
        self,
        key: str,
        res: int = 2,
        log: bool = True,
        print_kwargs: list[str] | Literal["all"] | None = None,
    ):
        """Decorate a function to measure the time taken in a block.

        Args:
            key (str): The key to store the duration under.
            res (int, optional): The number of decimal places to round to. Defaults to 2.
            log (bool, optional): Whether to log the duration. Defaults to True.
            print_kwargs (list[str] | bool, optional): The arguments to be added to the `key`.
                If a list, only the arguments in the list will be added to the message.
                If True, all arguments will added. If False, no arguments will be added.
                Additions to the message will have the form: f"{key} (with {arg1=val1, arg2=val2, ...})".
                Defaults to False.

        Raises:
            ValueError: If any of the print_kwargs are not in the functions signature.

        """

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

                with self.stopuhr(_inner_key, res=res, log=log):
                    return func(*args, **kwargs)

            return _inner

        return _decorator


@deprecated("funkuhr is deprecated. Use stopwatch instead.")
def funkuhr(msg: str, printer: callable = print, res: int = 2, print_kwargs: list[str] | bool = False):
    """Decorate a function to measure the time taken in a block.

    Wraps the `stopuhr` function to provide a decorator for benchmarking functions.

    Example:
        .. code-block:: python

            >>> from stopuhr import funkuhr

            >>> @funkuhr("Busy Function")
            >>> def busy_function():
            >>>     time.sleep(0.2)

            >>> busy_function()
            Busy Function took 0.20s

        It is possible to add arguments to the message.

        .. code-block:: python

            >>> from stopuhr import funkuhr

            >>> @funkuhr("Busy Function", print_kwargs=["arg1", "arg2"])
            >>> def busy_function(arg1, arg2, arg3):
            >>>     time.sleep(0.2)

            >>> busy_function(1, 2, 3)
            Busy Function took 0.20s (with arg1=1, arg2=2)

        It is also possible to add all arguments to the message.

        .. code-block:: python

            >>> from stopuhr import funkuhr

            >>> @funkuhr("Busy Function", print_kwargs=True)
            >>> def busy_function(arg1, arg2):
            >>>     time.sleep(0.2)

            >>> busy_function(1, 2)
            Busy Function took 0.20s (with arg1=1, arg2=2)

    Args:
        func (callable): The function to decorate.
        msg (str): The message to print.
        printer (callable, optional): The function to print with. Defaults to print.
        res (int, optional): The number of decimal places to round to. Defaults to 2.
        print_kwargs (list[str] | bool, optional): The arguments to be added to the `msg`.
            If a list, only the arguments in the list will be added to the message.
            If True, all arguments will added. If False, no arguments will be added.
            Additions to the message will have the form: f"{msg} (with {arg1=val1, arg2=val2, ...})".
            Defaults to False.

    Raises:
        ValueError: If any of the print_kwargs are not in the functions signature.

    """

    def _decorator(func: Callable):
        func_signature = signature(func)
        # Check if any of the print_kwargs are not in the functions signature and raise an error if so
        if isinstance(print_kwargs, list) and any(
            k not in func_signature.parameters for k in print_kwargs if isinstance(print_kwargs, list)
        ):
            raise ValueError(
                f"Not all {print_kwargs=} found in {func_signature.parameters=} of function {func.__name__}"
            )

        def _inner(*args, **kwargs):
            _inner_msg = msg

            if isinstance(print_kwargs, list):
                bound_args = _get_bound_args(func_signature, *args, **kwargs)
                # Filter by print_kwargs
                bound_args = {k: bound_args[k] for k in print_kwargs if k in bound_args}
                # Make a string of it and add it to the message
                bound_args_msg = ", ".join(f"{k}={v}" for k, v in bound_args.items())
                _inner_msg += f" (with {bound_args_msg})"
            elif print_kwargs:  # True was passed
                bound_args = _get_bound_args(func_signature, *args, **kwargs)
                # Make a string of it and add it to the message
                bound_args_msg = ", ".join(f"{k}={v}" for k, v in bound_args.items())
                _inner_msg += f" (with {bound_args_msg})"

            with stopuhr(_inner_msg, printer, res):
                return func(*args, **kwargs)

        return _inner

    return _decorator


__all__ = ["FunkUhr", "funkuhr"]
