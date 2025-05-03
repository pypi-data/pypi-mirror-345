## Typing stubs for setuptools

This is a [PEP 561](https://peps.python.org/pep-0561/)
type stub package for the [`setuptools`](https://github.com/pypa/setuptools) package.
It can be used by type-checking tools like
[mypy](https://github.com/python/mypy/),
[pyright](https://github.com/microsoft/pyright),
[pytype](https://github.com/google/pytype/),
[Pyre](https://pyre-check.org/),
PyCharm, etc. to check code that uses `setuptools`. This version of
`types-setuptools` aims to provide accurate annotations for
`setuptools==80.1.*`.

Given that `pkg_resources` is typed since `setuptools >= 71.1`, it is no longer included with `types-setuptools`.

This package is part of the [typeshed project](https://github.com/python/typeshed).
All fixes for types and metadata should be contributed there.
See [the README](https://github.com/python/typeshed/blob/main/README.md)
for more details. The source for this package can be found in the
[`stubs/setuptools`](https://github.com/python/typeshed/tree/main/stubs/setuptools)
directory.

This package was tested with
mypy 1.15.0,
pyright 1.1.400,
and pytype 2024.10.11.
It was generated from typeshed commit
[`c994e2d947894b7fb156e46c2eb0f544cc4dbd7c`](https://github.com/python/typeshed/commit/c994e2d947894b7fb156e46c2eb0f544cc4dbd7c).