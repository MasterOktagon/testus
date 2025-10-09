from inspect import signature, getframeinfo, stack
import sys
import traceback
import types

_tests: list[tuple[callable, signature]] = []
_successes = 0
_fails = 0
_in_section = []


class _test_fail(BaseException):
    def __init__(self, stringus: str, sec_cache: list[str], lineno: int):
        super().__init__()
        self.stringus = stringus
        self.sec_cache = sec_cache
        self.lineno = lineno


class Section:
    def __init__(self, name: str):
        self.name = name

    def __enter__(self):
        _in_section.append(self.name)

    def __exit__(self, *args):
        del _in_section[-1]


def test(f: callable):
    sign = signature(f)
    if len(sign.parameters):
        raise Exception("YOU IDIOT NO PARAMS!!!")
    _tests.append((f, sign))
    return f


def _exec_tests():
    global _successes, _fails
    for test in _tests:
        try:
            test[0]()
            _successes += 1
        except _test_fail as e:
            print(f"\033[31;1mTEST FAILED: {test[0].__name__}\033[0m")
            if e.sec_cache:
                for ind, i in enumerate(e.sec_cache):
                    print("  " * (ind+1) + f" in section {i}")
            print("\nassertion \033[1m" + e.stringus.strip() + "\033[0m failed at line " + str(e.lineno))

            _fails += 1
        except:
            raise Exception("YOU IDIOT, GET GOOD")


def require(check: bool):
    if not check:
        caller = getframeinfo(stack()[1][0])
        raise _test_fail(str(caller.code_context[0]), _in_section.copy(), int(caller.lineno))


def _print_result():
    total = _fails + _successes
    print("\n\033[32;1m[TEST RESULTS]\033[0m")
    print(f"\033[32m🗸\033[0m Passed: {_successes}/{total}")
    print(f"\033[31m𐄂\033[0m Failed: {_fails}/{total}")
    perc_succ = int(_successes/total * 50)
    print("[\033[32m" + "="*perc_succ + "\033[31m" + "="*(50-perc_succ) + "\033[0m]")

def run_tests():
    _exec_tests()
    _print_result()

if __name__ == "__main__":
    run_tests()
