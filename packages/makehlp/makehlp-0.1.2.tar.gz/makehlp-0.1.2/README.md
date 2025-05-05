# makehlp (make help)

Always-available script to analyze any unknown makefile and print out an inferred usage/help message explaining the available targets. Compatible with many various inconsistent types of makefile comment patterns found in the wild.

Many versions of this concept exist.. but this one is mine.

## Example output

```
$ makehlp
Usage: make [TARGET]
Targets:
  clean
  _lint_autofixing           run the linters that support autofixing, with autofixing enabled
  _lint_autofixing_disabled  run the linters that support autofixing, but with autofixing disabled
  _lint_nonautofixing        run the linters that don't support autofixing
  lint
  auto
  test_py
  test_that_build_is_clean
  test_ci                    Smaller testsuite for CI until I bother to fix the CI environment to run postgres etc.
  test_packaging             test installing the package fresh on a new computer, using docker
  coverage
  docs                       Generate Sphinx HTML documentation, including API docs
  servedocs                  Autoreload docs
  release                    Build and release to PyPI
```
