import time

from stopuhr import Chronometer, stopwatch


def assert_out(excpected_start: str):
    def _innter(msg: str):
        assert msg.startswith(excpected_start), f"Expected {msg} to start with '{excpected_start}'"

    return _innter


def assert_never():
    def _inner(msg: str):
        raise AssertionError(f"Expected no output, but got: {msg}")

    return _inner


def test_default_context_manager():
    with stopwatch("test", printer=assert_out("test took")):
        time.sleep(0.1)


def test_default_decorator():
    @stopwatch("test", printer=assert_out("test took"))
    def test_function():
        time.sleep(0.1)

    test_function()


def test_default_no_log():
    with stopwatch("test", printer=assert_never(), log=False):
        time.sleep(0.1)


def test_default_res():
    with stopwatch("test", printer=assert_out("test took 0.100"), res=3):
        time.sleep(0.1)


def test_summary():
    timer = Chronometer()
    with timer("test", log=False):
        time.sleep(0.1)

    with timer("test", log=False):
        time.sleep(0.3)

    with timer("test2", log=False):
        time.sleep(0.2)

    out = []
    stopwatch.summary(printer=out.append, res=1)
    assert out[0] == "test took 0.2 ± 0.1s (n=2 -> total=0.4s)"
    assert out[1] == "test2 took 0.2s"


def test_default_export():
    timer = Chronometer()
    with timer("test", log=False):
        time.sleep(0.1)

    with timer("test", log=False):
        time.sleep(0.3)

    with timer("test2", log=False):
        time.sleep(0.2)

    times = timer.export()
    assert len(times) == 2
    assert len(times.columns) == 2
    assert times.iloc[:, 0].count() == 2
    assert times.iloc[:, 1].count() == 1
    assert abs(times.iloc[:, 0].sum() - 0.4) < 0.01
    assert abs(times.iloc[:, 1].sum() - 0.2) < 0.01


def test_adv_decorator():
    @stopwatch.f("test", printer=assert_out("test (with a=1, b=2, c=3) took"))
    def test_function(a, b, c):
        time.sleep(0.1)

    test_function(1, 2, 3)


def test_adv_decorator_with_arg_filter():
    @stopwatch.f("test", printer=assert_out("test (with a=1, c=3) took"), print_kwargs=["a", "c"])
    def test_function(a, b, c):
        time.sleep(0.1)

    test_function(1, 2, 3)
