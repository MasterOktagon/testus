from testus import run_tests, require, test, Section, Benchmark

def fib(i: int):
    if i < 3: return 1
    return fib(i-1) + fib(i-2)

@test
def testing_fibonacci():
    require(fib(20) == 6765)
    with Benchmark("my section"):
        require(fib(3) == 2)

run_tests()
