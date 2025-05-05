from pytest import raises
import operator as op
from typing import TypeAlias, Annotated
from contractme import annotated, precondition, postcondition
from annotated_types import Ge, Le
import hypothesis

import contractme.testing
from contractme.testing import autotest, get_generator

"""
This contains tests for the testing extension.

As this is testing the testing code, it is probably harder to understand that
it needs to be.

Refer to the doc for simpler examples.
"""


MyInt: TypeAlias = Annotated[int, Ge(0), Le(1000)]


@annotated
def sub_and_div_no_contract(a: MyInt, b: MyInt) -> float:
    """
    This is incorrectly contracted: it fails for a == b
    """
    return 1.0 / float(a - b)


def test_trivial_failure_missing_contract():
    with raises(ZeroDivisionError):
        autotest(sub_and_div_no_contract)


@annotated
@precondition(lambda a, b: a != b)
def sub_and_div(a: MyInt, b: MyInt) -> float:
    """
    This is correctly contracted
    """
    return 1.0 / float(a - b)


def test_no_failure():
    autotest(sub_and_div)


def test_div_force_fail():
    gen_sub_and_div = get_generator(sub_and_div)
    # kinda weird to have this double call, but that's decorators for you...
    gen = hypothesis.example((0, 0))(gen_sub_and_div)
    with raises(AssertionError):
        # catched by contracts at call
        gen()


def test_test_with_examples():
    gen = contractme.testing.test_with_examples(
        sub_and_div,
        (1, 0),
        (3, 2),
        {"a": 4, "b": 10},
    )
    gen()


def test_test_with_examples_contract_fails():
    with raises(RuntimeError):
        # catched by contracts at test generation
        _ = contractme.testing.test_with_examples(
            sub_and_div,
            (1, 0),
            (0, 0),
        )


def test_test_with_examples_function_fails():
    # no contracts, no catch
    gen = contractme.testing.test_with_examples(
        sub_and_div_no_contract,
        (1, 0),
        (0, 0),
    )

    with raises(ZeroDivisionError):
        gen()


@annotated
@precondition(lambda a, b: a != b)
@postcondition(lambda result: result > 0.0)
def sub_and_div_wrong_impl(a: MyInt, b: MyInt) -> float:
    """
    This is correctly contracted
    """
    return 1.0 / float(a - b)


def test_test_with_examples_postcondition_checked_at_call():
    # no contracts, no catch
    gen = contractme.testing.test_with_examples(
        sub_and_div_wrong_impl,
        (1, 10),
    )

    with raises(AssertionError):
        gen()
