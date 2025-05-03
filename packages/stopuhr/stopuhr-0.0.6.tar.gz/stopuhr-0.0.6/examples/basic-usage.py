# ruff: noqa: D205, D212, D400, D415, E402, D103
"""
===================
Basic Usage Example
===================

This is a basic usage example of the `stopuhr` package.

"""

# %%
# Stop the time with a simple context manager and print the duration.
import time

import stopuhr

timer = stopuhr.Chronometer()

with timer("Sleeping"):
    time.sleep(0.1)

# %%
# stopuhr also provides a default instance of the `Chronometer` class, which is called `stopwatch`.
from stopuhr import stopwatch

with stopwatch("Sleeping"):
    time.sleep(0.1)

# %%
# Instead of printing, one can pass any callable to the `printer` argument, e.g. a logger.
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
logger.addHandler(handler)

with stopwatch("Sleeping", printer=logger.info):
    time.sleep(0.1)

# %%
# By default, the output is rounded to two decimal places. This can be changed with the `res` argument.
with stopwatch("Sleeping", res=3):
    time.sleep(0.16189)

# %%
# We can change the default behaviour by passing the arguments to the `__init__` method of the `Chronometer` class.
timer = stopuhr.Chronometer(printer=logger.info, res=3)
with timer("Sleeping"):
    time.sleep(0.16189)

# %%
# Since `stopwatch` is just a `Chronometer` instance, we can just overwrite the default behaviour.
stopwatch.res = 3
with stopwatch("Sleeping"):
    time.sleep(0.16189)
stopwatch.res = 2  # back to default

# %%
# The `Chronometer` class is stateful, meaning that it can be used to measure multiple durations at once.
# This also supports the `printer` and `res` arguments.
# The `log` argument of each call can be used to suppress the output.

for i in range(5):
    with stopwatch("Sleeping", log=False):
        time.sleep(0.2)

# Print a summary with the mean and standard deviation of the durations.
stopwatch.summary()

# %%
# This summary used also the previous calls to the `stopwatch` function to calculate the mean.
# We can reset it's state with the `reset` method, note that this is happening in-place.
stopwatch.reset()

# %%
# The previous behavior can also be achieved with the `start` and `stop` methods.
# Here, the `stop` method also supports the `printer`, `log` and `res` arguments.
for i in range(5):
    stopwatch.start("Sleeping")
    time.sleep(0.2)
    stopwatch.stop("Sleeping", log=False)

stopwatch.summary()

# %%
# The Chronometer can also measure multiple durations at once, thanks to that feature.

stopwatch.reset()

# Single duration
with stopwatch("A (single 0.2s sleep)", log=False):
    time.sleep(0.2)

for i in range(5):
    with stopwatch("B (multiple 0.2s sleeps)", log=False):
        time.sleep(0.2)
    with stopwatch("C (multiple 0.1s sleeps)", log=False):
        time.sleep(0.1)

stopwatch.summary()

# %%
# Because the `Chronometer`'s `__call__` method is a `@contextmanager`, it can be used as a decorator.
# This takes the same arguments as the context manager (`res`, `log` and `printer`).

stopwatch.reset()


@stopwatch("Busy Function")
def busy_function():
    time.sleep(0.2)


busy_function()

# %%
# Of course, this can be used to measure multiple functions at once.

stopwatch.reset()


@stopwatch("Busy Function", log=False)
def busy_function():
    time.sleep(0.1)


for i in range(5):
    busy_function()

stopwatch.summary()
