# ruff: noqa: D205, D212, D400, D415, E402, D103
"""
======================
Advanced Usage Example
======================

This is a advanced usage example of the `stopuhr` package.

"""

# %%
# Also print out function arguments
import time

from stopuhr import stopwatch


@stopwatch.f("Sleeping")
def sleep(seconds: float):
    time.sleep(seconds)


sleep(0.1)

# %%
# If some parameters should not be printed,
# we can use the `print_kwargs` argument.to select which ones should be printed.


@stopwatch.f("Sleeping", print_kwargs=["seconds"])
def sleep(seconds: float, other: str):
    time.sleep(seconds)
    print(other)


sleep(0.1, "Hello")

# %%
# In multi processing situations, we must use a separate `Chronometer` instance for each process.
# For this, we can use the `merge` or `combine` method to combine the results of multiple `Chronometer` instances.

import stopuhr


def simulate_process():
    timer = stopuhr.Chronometer()

    with timer("Sleeping"):
        time.sleep(0.1)
        res = 3.14159
    return {"result": res, "timer": timer}


# We only simulate a multi processing situation here. A real one would be too much overhead.

tasks_outputs = [simulate_process() for _ in range(5)]
tasks_timer = [task["timer"] for task in tasks_outputs]

combined_timer = stopuhr.Chronometer.combine(tasks_timer)
combined_timer.summary()
