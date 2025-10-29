from inspect import signature, getframeinfo, stack
import time

_tests: list[tuple[callable, signature]] = []
_successes: int = 0
_fails: int = 0
_in_section: list[str] = []
_benchmarks: list[str] = []
_trace: dict[str,any] = {}
_generator_idx: int = 0
_generating: bool = True
_generator_data: list[int] = []
# TODO benchmark mintime, exception prettyprinting
class _test_fail(BaseException):
    def __init__(self, stringus: str, sec_cache: list[str], lineno: int, filename: str):
        super().__init__()
        self.stringus = stringus
        self.sec_cache = sec_cache
        self.lineno = lineno
        self.filename = filename

class _catch_fail(BaseException):
    def __init__(self, stringus: str, sec_cache: list[str], lineno: int, filename: str, errname: str, errname_real: str):
        super().__init__()
        self.stringus = stringus
        self.sec_cache = sec_cache
        self.lineno = lineno
        self.filename = filename
        self.errname = errname
        self.errname_real = errname_real

class _test_slow(BaseException):
    def __init__(self, stringus: str, sec_cache: list[str], lineno: int, filename: str, limit: float, time_diff: float):
        super().__init__()
        self.stringus = stringus
        self.sec_cache = sec_cache
        self.lineno = lineno
        self.filename = filename
        self.limit = limit
        self.time_diff = time_diff


class Section:
    def __init__(self, name: str):
        self.name = name

    def __enter__(self):
        _in_section.append(self.name)

    def __exit__(self, *args):
        del _in_section[-1]

class Benchmark(Section):
    def __init__(self, name: str="", limit: float=0):
        self.name = ""
        self.limit = limit
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
        #if time_diff > limit:
        #    caller = getframeinfo(stack()[1][0])
        #    raise _test_slow(str(caller.code_context[0]), _in_section.copy(), int(caller.lineno), caller.filename, self.limit, time_diff)

def trace(expr: any):
    code = getframeinfo(stack()[1][0]).code_context[0].strip()
    code = code[code.find('(')+1:code.find(')')]
    _trace[code] = expr

def generate(args: list):
    global _generator_idx, _generator_data, _generating
    if _generating:
        _generator_data.append(-1)
    if _generator_data[_generator_idx] == -1:
        _generator_data[_generator_idx] = len(args)-1
    
    _arg = list(reversed(args))
    data = _arg[_generator_data[_generator_idx]]
    if (_generator_idx == len(_generator_data)-1 or _generator_data[_generator_idx+1:] == [0]*(len(_generator_data)-_generator_idx-1)) and not _generating:
        _generator_data[_generator_idx] -= 1
    _generator_idx += 1

    code = getframeinfo(stack()[1][0]).code_context[0].strip()
    code = code.split('=')[0].strip()
    _trace[code] = str(data)

    return data

def test(f: callable):

    sign = signature(f)
    if len(sign.parameters):
        raise Exception("YOU IDIOT NO PARAMS!!!")
    _tests.append((f, sign))

    return f

def _print_trace():
    if len(_trace) > 0:
        print()
    for t in _trace:
        print(f"  with \033[1m{t}={_trace[t]}\033[0m")

def _exec_test(test: tuple[callable, signature]):
    global _successes, _fails, _benchmarks, _generator_idx, _generator_data, _generating
    try:
        test[0]()
        _successes += 1
    except _test_fail as e:
        print(f"\033[31;1mTEST FAILED: {test[0].__name__.replace('_', ' ').strip()}\033[0m \033[31m({e.filename})\033[0m")
        if e.sec_cache:
            for ind, i in enumerate(e.sec_cache):
                if i == "": continue
                print("  " * (ind+1) + f"in section {i}")
        _print_trace()
        print("\nassertion \033[1m" + e.stringus.strip() + "\033[0m failed at line " + str(e.lineno) + "\n")
        _fails += 1

    except _test_slow as e:
        print(f"\033[31;1mTEST FAILED: {test[0].__name__.replace('_', ' ').strip()}\033[0m \033[31m({e.filename})\033[0m")
        if e.sec_cache:
            for ind, i in enumerate(e.sec_cache):
                if i == "": continue
                print("  " * (ind+1) + f"in section {i}")
        print("\nbenchmark \033[1m" + e.stringus.strip() + "\033[0m at line " + str(e.lineno) + f" was slow: {e.time_diff}s/{e.limit}s\n")

    except _catch_fail as e:
        print(f"\033[31;1mTEST FAILED: {test[0].__name__.replace('_', ' ').strip()}\033[0m \033[31m({e.filename})\033[0m")
        if e.sec_cache:
            for ind, i in enumerate(e.sec_cache):
                if i == "": continue
                print("  " * (ind+1) + f"in section {i}")
        if e.errname_real != "" and e.errname_real != "_catch_fail": print("\nassertion \033[1m" + e.stringus.strip() + "\033[0m at line " + str(e.lineno) + f" expected \033[1m{e.errname}\033[0m got {e.errname_real}\n")
        else: print("\nassertion \033[1m" + e.stringus.strip() + "\033[0m at line " + str(e.lineno) + f" expected \033[1m{e.errname}\033[0m got no error\n")

        _fails += 1
    except BaseException as e:
        raise e

    finally:
        for name, bm_time, section in _benchmarks:
            print(f"[Benchmark \033[1m{test[0].__name__ + '::'*int(len(section) > 0) + '::'.join(section) + name}\033[0m required {round(bm_time, 6)}s]")

def _exec_tests():
    global _successes, _fails, _benchmarks, _generator_idx, _generator_data, _generating
    for test in _tests:
        while _generator_data != [0]*len(_generator_data) or _generator_data == []:
            _exec_test(test)
            
            _benchmarks = []
            _trace = {}
            if _generating:
                _generating = False
                _generator_data[-1] -= 1
            _generator_idx = 0

            if _generator_data == []:
                break
        
        if _generator_data != []:
            _exec_test(test)

        _generator_idx = 0
        _generator_data = []
        _generating = True


def require(check: bool):
    if not check:
        caller = getframeinfo(stack()[1][0])
        raise _test_fail(str(caller.code_context[0]), _in_section.copy(), int(caller.lineno), caller.filename)

def catch(expr: callable, exc: type=Exception):
    try:
        expr()
        caller = getframeinfo(stack()[1][0])
        raise _catch_fail(str(caller.code_context[0]), _in_section.copy(), int(caller.lineno), caller.filename, exc.__name__, "")
    except exc:
        pass
    except BaseException as e:
        caller = getframeinfo(stack()[1][0])
        raise _catch_fail(str(caller.code_context[0]), _in_section.copy(), int(caller.lineno), caller.filename, exc.__name__, e.__class__.__name__)

def _print_result():
    total = _fails + _successes
    print("\n\033[32;1m[TEST RESULTS]\033[0m")
    if total == 0:
        print(f"\033[32mNo tests ran\033[0m")
        print("[\033[33m" + "="*50 + "\033[0m]")
    else:
        print(f"\033[32m🗸\033[0m Passed: {_successes}/{total}")
        print(f"\033[31m𐄂\033[0m Failed: {_fails}/{total}")
        perc_succ = int(_successes/total * 50)
        print("[\033[32m" + "="*perc_succ + "\033[31m" + "="*(50-perc_succ) + "\033[0m]")

def run_tests():
    _exec_tests()
    _print_result()