from scatter_append import ScatterAppend
import pytest


@pytest.fixture
def list_examples():
    xs: list[int] = [1, 2, 3, 4]
    ys: list[str] = ["abc", "def", "ghi", "jkl"]

    return xs, ys


def test(list_examples):
    xs, ys = list_examples

    x_: list[int] = []
    y_: list[str] = []
    sa = ScatterAppend(x_, y_)

    for x, y in zip(xs, ys):
        sa += x, y

    assert xs == x_ and ys == y_


def test2(list_examples):
    xs, ys = list_examples
    sa = ScatterAppend.make_n(2)

    for x, y in zip(xs, ys):
        sa += x, y

    x_, y_ = sa

    assert xs == x_ and ys == y_


def test_get(list_examples):
    xs, ys = list_examples
    sa = ScatterAppend.make_n(2)

    for x, y in zip(xs, ys):
        sa += x, y

    for i in range(max(len(xs), len(ys))):
        x, y = sa.get(i)
        assert x == xs[i] and y == ys[i]


def test_size(list_examples):
    xs, ys = list_examples
    sa = ScatterAppend.make_n(2)

    for x, y in zip(xs, ys):
        sa += x, y

    assert sa.size() == (len(xs), len(ys))
    assert sa.size(0) == len(xs)
    assert sa.size(1) == len(ys)
