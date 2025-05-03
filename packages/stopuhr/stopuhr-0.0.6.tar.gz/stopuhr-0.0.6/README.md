# stopuhr

A simple tool for measuring durations in Python.

## Installation

You can install stopuhr via pip:

```sh
pip install stopuhr
```

However, `uv` is recommended for installing python packages:

```sh
uv add stopuhr
```

## Usage

With stopuhr it is convinient to measure durations in Python:

```python
import time
from stopuhr import stopwatch

with stopwatch("My Timer"):
    # Do something
    time.sleep(2)
>>> My Timer took 2.00s

@stopwatch("My Timer")
def my_function():
    # Do something
    time.sleep(2)

>>> My Timer took 2.00s
```

This library can much more than that. Visit the reference or example section for more details.
