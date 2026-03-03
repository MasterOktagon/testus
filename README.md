# Testus - simple python unit tests inspired by Catch2

testus is a single-file dependency-free python module which adds python module tests to your project.

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

## ToDo

- [ ] assert statements in test cases
- [ ] assert decomposition
- [ ] VSCode integration

