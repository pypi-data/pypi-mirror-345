import pytest
import contractme
from epycs.subprocess import cmd
from contractme import precondition, postcondition
import warnings


@pytest.fixture
def preconditions_ignored():
    contractme.ignore_preconditions()
    yield
    contractme.check_preconditions()


@pytest.fixture
def postconditions_ignored():
    contractme.ignore_postconditions()
    yield
    contractme.check_postconditions()


def eps_eq(a, b):
    return abs(a - b) <= 1e-7 * min(abs(a), abs(b))


def test_square_root():
    @precondition(lambda x: x > 0)
    @postcondition(lambda x, result: eps_eq(result * result, x))
    def square_root(x: float) -> float:
        return x**0.5

    for v in (1, 4, 9, 16, 2):
        _ = square_root(v)

    for v in (-1, -2, -4):
        with pytest.raises(AssertionError):
            _ = square_root(v)


def test_ignore_precondition(preconditions_ignored):
    @precondition(lambda x: x > 0)
    def square_root_no_post(x: float) -> float:
        if x < 0:
            # cause negative values to return garbage
            # should be dead!
            return 0
        return x**0.5

    for v in (-1, -2, -4, 1, 4, 9, 16, 2):
        _ = square_root_no_post(v)

    @postcondition(lambda x, result: eps_eq(result * result, x))
    def square_root(x: float) -> float:
        return square_root_no_post(x)

    for v in (1, 4, 9, 16, 2):
        _ = square_root(v)

    for v in (-1, -2, -4):
        with pytest.raises(AssertionError):
            _ = square_root(v)


def test_ignore_postcondition(postconditions_ignored):
    @postcondition(lambda x, result: eps_eq(result * result, x))
    def square_root_no_pre(x: float) -> float:
        return x**0.5

    for v in (-1, -2, -4, 1, 4, 9, 16, 2):
        _ = square_root_no_pre(v)

    @precondition(lambda x: x > 0)
    def square_root(x: float) -> float:
        return square_root_no_pre(x)

    for v in (1, 4, 9, 16, 2):
        _ = square_root(v)

    for v in (-1, -2, -4):
        with pytest.raises(AssertionError):
            _ = square_root(v)


def test_append():
    @precondition(lambda n: n >= 0 and round(n) == n)
    @postcondition(lambda l: len(l) > 0)
    @postcondition(lambda l, n: l[-1] == n)
    @postcondition(lambda l, old: l[:-1] == old.l)
    def append_count(l: list[int], n: int):
        l.append(n)

    a: list[int] = []
    append_count(a, 2)


def test_no_append_count():
    @precondition(lambda l: hasattr(l, "__len__"))
    @precondition(lambda n: n >= 0 and round(n) == n)
    @postcondition(lambda l: hasattr(l, "__len__"))
    @postcondition(lambda l: len(l) > 0)
    @postcondition(lambda l, n: l[-1] == n)
    @postcondition(lambda l, old: l[:-1] == old.l)
    def buggy_append_count(l, n):
        pass

    with pytest.raises(AssertionError):
        buggy_append_count(None, 2)
    with pytest.raises(AssertionError):
        buggy_append_count([], 2)


def test_printout_error_messages():
    # parsing when parentheses are not before the lambda kw
    @precondition(lambda a: (False))
    def f(a):  # pragma: no cover
        pass

    with pytest.raises(AssertionError):
        f(None)

    # parsing with a var that is a lambda
    cond = lambda a: False

    @precondition(cond)
    def f2(a):  # pragma: no cover
        pass

    with pytest.raises(AssertionError):
        f2(None)


def test_rejects_accepts():
    @precondition(lambda a: a > 0)
    def f(a):  # pragma: no cover
        pass

    assert f.rejects(0)
    assert f.accepts(1)
    assert f.accepts(a=1)


def test_with_global():
    count = 0

    def count_is_reset() -> bool:
        return count == 0

    @postcondition(count_is_reset)
    def reset_count():
        nonlocal count
        count = 0

    @postcondition(count_is_reset)
    def failing_reset_count():
        pass

    count = 1
    with pytest.raises(AssertionError):
        failing_reset_count()
    reset_count()


def test_call_precondition_with_no_arguments():
    @precondition(lambda: 1 != 0)
    def f(a):  # pragma: no cover
        pass

    with pytest.raises(TypeError, match=r"missing .* required .* argument"):
        with pytest.warns(UserWarning, match="contracts ignored"):
            # the wrapper should let it crash on its own
            f()


def test_call_with_default():
    @precondition(lambda a: a > 0)
    def f(a=1, b=2, c=3):
        pass

    f()


def test_failing_pre_with_message():
    @precondition(lambda: False, "message that should be displayed")
    def f():  # pragma: no cover
        pass

    with pytest.raises(AssertionError):
        f()


def test_failing_post_with_message():
    @postcondition(lambda: False, "message that should be displayed")
    def f():
        pass

    with pytest.raises(AssertionError):
        f()


def test_rejects_accepts_with_message():
    @precondition(lambda a: a > 0, "message that should be displayed")
    def f(a):
        pass

    f(1)
    assert f.rejects(0)
    assert f.accepts(1)


def test_failing_post_with_old():
    @postcondition(lambda l, old: len(l) > len(old.l))
    def f(l):
        pass

    with pytest.raises(AssertionError):
        f([])


def test_call_with_long_argument_that_requires_shorter_repr():
    @precondition(lambda a: False)
    def f(a):  # pragma: no cover
        pass

    with pytest.raises(AssertionError):
        f(
            "Myh very long argument, I can't believe how long it is, what am I gonna do my console is going to be a mess"
        )


def test_cannot_have_precondition_of_a_constructor():
    with pytest.raises(RuntimeError):

        class C:
            @precondition(lambda self: True)
            def __init__(self):  # pragma: no cover
                pass


def test_can_have_kwarg_precondition():
    @precondition(lambda **kw: kw["a"] > 0)
    def f(a):
        return a

    f(1)
    with pytest.raises(AssertionError):
        f(0)


def test_can_have_kwarg_postcondition():
    @postcondition(lambda **kw: kw["result"] > 0)
    def f(a):
        return a

    f(1)
    with pytest.raises(AssertionError):
        f(0)
