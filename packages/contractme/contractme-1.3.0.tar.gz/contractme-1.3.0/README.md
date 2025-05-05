# ContractMe

![coverage](https://gitlab.com/leogermond/contractme/badges/main/coverage.svg?job=checks)
[![Checked with pyright](https://microsoft.github.io/pyright/img/pyright_badge.svg)](https://microsoft.github.io/pyright/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](ttps://github.com/psf/black)

A lightweight and adaptable framework for design-by-contract in python

# Example code

Here are some examples:

## `result`

```python
@precondition(lambda x: x >= 0)
@postcondition(lambda x, result: eps_eq(result * result, x))
def square_root(x: float) -> float:
    return x**0.5
```

## `old`

```python
@precondition(lambda l, n: n >= 0 and round(n) == n)
@postcondition(lambda l, n: len(l) > 0)
@postcondition(lambda l, n: l[-1] == n)
@postcondition(lambda l, n, old: l[:-1] == old.l)
def append_count(l: list[int], n: int):
    l.append(n)
```

## Using annotations

```python
@annotated
def incr(v : int) -> int:
    return v + 1
```

Supports annotations and [PEP-593](https://peps.python.org/pep-0593/)
using the [annotated-types](https://pypi.org/project/annotated-types/) library.
**Note:** `annodated_types.MultipleOf` follows the Python semantics.
**Note 2:** Following an open-world reasoning, any unknown annotation is considered
to be correct, so it won't cause a check failure.

```python
from typing import TypeAlias, Annotated
from annotated_types import MultipleOf

Even: TypeAlias = Annotated[int, MultipleOf(2)]

@annotated
def square(v : Even) -> Even
    return v * v
```

## Writing tests and having test generation

The hypothesis plugin can be used easily through the `contractme.testing.autotest`
function.

```python
Positive: TypeAlias = Annotated[int, Ge(1)]

@annotated
def div(d: Positive) return Positive:
    return 1000 // d

def test_div():
    autotest(div)
```

You can access the underlying hypothesis generator with `contractme.testing.get_generator(div)`.

It's a pure hypothesis strategy generator, inferred from the annotated types and
contracts of the function. The main weirdness is that it takes a tuple as parameter since
the parameters are all generated together so that the contracts can be checked.

You can easily extend it with
[Hypothesis advanced features](https://hypothesis.readthedocs.io/en/latest/reference/api.html)

```python
generator_function = contractme.testing.get_generator(div)
# kinda weird to have this double call, but that's decorators for you...
test_div_force_0 = example((0,))(generator_function)
```

The library provides its own `contractme.testing.test_with_examples` function which has three differences
with the one provided by hypothesis:

* It checks the contracts when being called (at test construction): contracts should hold on all
  examples.
* It takes a vararg of either tuple `*args` or dict `**kwarg` as examples, to avoid
  function nesting.

With pytest:
```python
test_div = contractme.testing.test_with_examples(
    div,
    (1,),
    (2,),
    (0,), # this causes a RuntimeError at test elaboration
)
```

# Test

`uv run pytest`

# Deploy new version

* `uv build`
* Push the resulting new lock file
* Git tag as `v<number>`
* Gitlab will take care of doing the release

# Changelog

* v1.3.0

Binding and helpers to hypothesis library for test data generation.

* v1.2.0

Full support of annotated-types library for checking PEP-593 compatible type annotations
automatically through the `@annotated` decorator.

Generated contracted functions are now of a `ContractedFunction` class, with a `original_call`
attribute that contains the function without contracts checking.

Pyright check for the totality of the code.

* v1.1.0

Contracts can be disabled at runtime with `ignore_preconditions()` and `ignore_postconditions()`

Contracts are disabled from the start with python optimized (`-O`) flag.

Fix a bug where contracts would hide an incorrect function call
