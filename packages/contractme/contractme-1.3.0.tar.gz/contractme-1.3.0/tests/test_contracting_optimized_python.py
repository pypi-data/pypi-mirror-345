import pytest
import epycs.subprocess
from epycs.subprocess import cmd
from subprocess import DEVNULL

epycs.subprocess.exit_on_error = False

contract_example = """
from contractme import precondition, postcondition

@precondition(lambda x: x > 0)
@postcondition(lambda result: result > 0)
def f(x: int) -> int:
    return x

def main():
    f(-1)

if __name__ == "__main__":
    main()
"""


def test_fail_without_optimized():
    r = cmd.python("-c", contract_example, stderr=DEVNULL)
    assert r.returncode != 0


def test_succeeds_with_optimized():
    r = cmd.python("-O", "-c", contract_example)
    assert r.returncode == 0
