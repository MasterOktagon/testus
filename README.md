# Testus - simple python unit tests inspired by Catch2

testus is a single-file dependency-free (well requires stdlibs `inspect` and `time`) python module which adds python module tests to your project.

```python
# mymodule.py

from testus import test, require, run_tests

def fib(n):
    if n < 3: return 1
    return fib(n-1) + fib(n-2)

@test
def test_fib():
    require(fib(5) == 5)
    require(fib(11) == 89)

if __name__ == "__main__":
    run_tests()
```

## Features

### Test annotation
annotate your test routines with the `@test` annotation to register them and run them with `run_tests`. Test routines may not have any arguments.
```py
@test
def testing_fibonacci():
    require(fib(20) == 6765)
```
### Test sections
use sections to annotate where your test failed

```py
@test
def testing_fibonacci():
    require(fib(20) == 6765)
    with Section("my section"):
        require(fib(3) == 2)
```

### Microbenchmarks
use Benchmarks to get a quick overview of your Performance

```py
@test
def testing_fibonacci():
    require(fib(20) == 6765)
    with Benchmark("my section"):
        require(fib(3) == 2)
```

### Variable tracing
use the `trace` method to get helpful metadata in tests
```py
@test
def testing_fibonacci():
    require(fib(20) == 6765)
    for i in range(4):
        trace(i)
        with Section("my section"):
            require(fib(3) == 2)
```

> [!WARNING]
> due to `trace` using suspect methods to decompose the variable name, trace will only
> work correctly if it is placed on a single line

### Batch test generation
the `generate` function takes a list of values and generates a single test case for each of them. It also traces the variables value.
```py
@test
def testing_fibonacci():
    require(fib(20) == 6765)
    i = generate([1,2,3,4])
    with Section("my section"):
        require(fib(3) == 2)
```
_(same result as above, but with multiple test cases)_ 
`generate` should be preferred to a for loop if there is a crucial require statement in the loop, as an assertion error will not abort the testing of this test case. using multiple `generate` calls will run the tests with any combination of all values

> [!WARNING]
> due to `generate` using suspect methods to decompose the variable name and load the list, generate will only
> work correctly if it is placed on a single line and the list passed to generate will not change between test runs

## ToDo

- [ ] assert statements in test cases
- [ ] assert decomposition
- [ ] VSCode integration

