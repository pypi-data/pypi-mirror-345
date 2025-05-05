from contractme.contracting import ContractedFunction
from typing import Callable, get_type_hints, TypeAlias
from hypothesis import assume, given, example, strategies as st


def get_strategies(f: Callable) -> list[st.SearchStrategy]:
    th = get_type_hints(f, include_extras=True)

    sts = []

    for n, t in th.items():
        if n == "return":
            continue
        sts.append(st.from_type(t))
    return sts


TestableFunction: TypeAlias = ContractedFunction | Callable
TestGenerator: TypeAlias = Callable


def call_with_composite(f: Callable, composite: tuple | dict):
    if isinstance(composite, dict):
        return f(**composite)
    else:
        return f(*composite)


def draw_accepted_input(draw: Callable, f: TestableFunction) -> tuple:
    sts = get_strategies(f)
    v = tuple(draw(e) for e in sts)
    if isinstance(f, ContractedFunction):
        assume(f.accepts(*v))
    return v


def get_generator(f: TestableFunction) -> TestGenerator:
    @st.composite
    def correct_input(draw: Callable) -> tuple[int, int]:
        return draw_accepted_input(draw, f)

    @given(correct_input())
    def search(value):
        call_with_composite(f, value)

    return search


def autotest(f: TestableFunction):
    get_generator(f)()


def test_with_examples(f: TestableFunction, *exs) -> TestGenerator:
    gen = get_generator(f)
    for e in exs:
        if isinstance(f, ContractedFunction):
            accepted = call_with_composite(f.accepts, e)
            if not accepted:
                raise RuntimeError(f"contracts rejected example {e}")
        gen = example(e)(gen)
    return gen
