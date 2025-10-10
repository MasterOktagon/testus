from inspect import signature, getframeinfo, stack
import sys
import traceback
import types
import time

_tests: list[tuple[callable, signature]] = []
_successes = 0
_fails = 0
_in_section = []
_benchmarks = []

# TODO generate(), benchmark mintime, catch(), exception prettyprinting

class _test_fail(BaseException):
    def __init__(self, stringus: str, sec_cache: list[str], lineno: int, filename: str):
        super().__init__()
        self.stringus = stringus
        self.sec_cache = sec_cache
        self.lineno = lineno
        self.filename = filename


class Section:
    def __init__(self, name: str):
        self.name = name

    def __enter__(self):
        _in_section.append(self.name)

    def __exit__(self, *args):
        del _in_section[-1]

class Benchmark(Section):
    def __init__(self, name: str=""):
        self.name = ""
        if name != "":
            self.name = "::" + name

    def __enter__(self):
        super().__enter__()
        self.__timer_start = time.process_time()

    def __exit__(self, *args):
        global _benchmarks
        super().__exit__(*args)
        time_diff = time.process_time() - self.__timer_start
        _benchmarks.append((self.name, time_diff, _in_section.copy()))


def test(f: callable):
    sign = signature(f)
    if len(sign.parameters):
        raise Exception("YOU IDIOT NO PARAMS!!!")
    _tests.append((f, sign))
    return f


def _exec_tests():
    global _successes, _fails, _benchmarks
    for test in _tests:
        try:
            test[0]()
            _successes += 1
        except _test_fail as e:
            print(f"\033[31;1mTEST FAILED: {test[0].__name__.replace('_', ' ').strip()}\033[0m \033[31m({e.filename})\033[0m")
            if e.sec_cache:
                for ind, i in enumerate(e.sec_cache):
                    if i == "": continue
                    print("  " * (ind+1) + f"in section {i}")
            print("\nassertion \033[1m" + e.stringus.strip() + "\033[0m failed at line " + str(e.lineno) + "\n")

            _fails += 1
        except:
            raise Exception("YOU IDIOT, GET GOOD")

        for name, bm_time, section in _benchmarks:
                print(f"[Benchmark \033[1m{test[0].__name__ + '::'*int(len(section) > 0) + '::'.join(section) + name}\033[0m required {round(bm_time, 6)}s]")
        
        _benchmarks = []


def require(check: bool):
    if not check:
        caller = getframeinfo(stack()[1][0])
        raise _test_fail(str(caller.code_context[0]), _in_section.copy(), int(caller.lineno), caller.filename)


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
