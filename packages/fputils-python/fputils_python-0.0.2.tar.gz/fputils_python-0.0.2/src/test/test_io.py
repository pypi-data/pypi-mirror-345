from fputils.io import IO
import pytest


def test_io_decorator():
    @IO
    def div(a: int, b: int) -> float:
        return float(a / b)

    result = div(6, 2).collect()
    result2 = div(b=2, a=6).collect()

    assert result == 3, f"Expected 3, but got {result}"
    assert result2 == 3, f"Expected 3, but got {result2}"


def test_lazy_eval():
    side_effect = 0

    def fn_with_side_effect(a: int) -> int:
        nonlocal side_effect
        side_effect = 42
        return a

    io = IO(fn_with_side_effect, 123)

    assert side_effect == 0, f"Expected side effect to be 0, but got {side_effect}"

    result = io.collect()
    assert result == 123, f"Expected result to be 123, but got {result}"
    assert side_effect == 42, f"Expected side effect to be 42, but got {side_effect}"


def test_map():
    def add_one(x: int) -> int:
        return x + 1

    io = IO(5).map(add_one)
    result = io.collect()

    assert result == 6, f"Expected result to be 6, but got {result}"


def test_flatmap():
    @IO
    def add_one(x: int) -> int:
        return x + 1

    io = IO(5).flatmap(add_one)
    result = io.collect()

    assert result == 6, f"Expected result to be 6, but got {result}"


def test_chained_maps():
    def square(x: int) -> int:
        return x * x

    def half(x: int) -> float:
        return x * 0.5

    io = IO(2).map(square).flatmap(IO(half)).flatmap(IO(square)).map(half)
    result = io.collect()

    assert result == 2, f"Expected result to be 2, but got {result}"


def test_mismatched_types():
    def square(x: int) -> int:
        return x * x

    def to_string(x: int) -> str:
        return str(x)

    with pytest.raises(TypeError):
        io = IO(2).map(to_string).map(square)
        io.collect()

    with pytest.raises(TypeError):
        io = IO(2).flatmap(IO(to_string)).flatmap(IO(square))
        io.collect()
