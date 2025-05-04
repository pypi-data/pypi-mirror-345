# powell-opt

[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)
[![pdm-managed](https://img.shields.io/badge/pdm-managed-blueviolet)](https://pdm.fming.dev)
[![PyPI](https://img.shields.io/pypi/v/powell-opt.svg)](https://pypi.org/project/powell-opt)
[![Supported Python versions](https://img.shields.io/pypi/pyversions/powell-opt.svg)](https://pypi.org/project/powell-opt)
[![License](https://img.shields.io/pypi/l/powell-opt.svg)](https://pypi.python.org/pypi/powell-opt)
[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/lmmx/powell-opt/master.svg)](https://results.pre-commit.ci/latest/github/lmmx/powell-opt/master)

Python bindings for the _Powell's method_ optimisation algorithm from the `scirs2-optimize` Rust library.

## Installation

```bash
pip install powell-opt
```

## About Powell's Method

Powell's method is a derivative-free optimization algorithm that minimizes functions by performing sequential one-dimensional searches along different directions. It's particularly useful for functions that:

- Cannot be easily differentiated
- Have discontinuities or non-smooth regions
- Have relatively few dimensions

## Usage

```python
import powell_opt as po

def rosenbrock(x):
    """Rosenbrock function - a classical test case for optimization"""
    return 100 * (x[1] - x[0]**2)**2 + (1 - x[0])**2

# Initial guess
x0 = [0.0, 0.0]

# Set options (optional)
options = po.Options(maxiter=1000, ftol=1e-6)

# Minimize using Powell's method
result = po.minimize(rosenbrock, x0, options)

print(f"Solution: {result.x}")
print(f"Function value: {result.fun}")
print(f"Number of iterations: {result.nit}")
print(f"Success: {result.success}")
```
⇣
```
Solution: [1.0000000000000002, 1.0000000000000007]
Function value: 4.979684464207637e-30
Number of iterations: 19
Success: True
```

- Find this at `examples/basic_usage.py` and in the tests as `test_powell_rosenbrock()`

## API Reference

### `minimize(func, x0, options=None)`

Minimizes a scalar function using Powell's method.

**Parameters:**
- `func`: A callable that takes a list of parameters and returns a scalar value
- `x0`: Initial guess (list of parameters)
- `options`: Optional `Options` object with algorithm parameters

**Returns:**
- `MinimizeResult` object containing the optimization results

### `Options`

Class for configuring the Powell optimization algorithm.

**Parameters:**
- `maxiter`: Maximum number of iterations (optional)
- `ftol`: Relative tolerance for convergence in function value (optional)
- `gtol`: Relative tolerance for convergence in gradient norm (optional)
- `disp`: Whether to print convergence progress messages (default: False)
- `eps`: Small value used for numerical stability in calculations (optional)
- `finite_diff_rel_step`: Relative step size for finite difference approximation of derivatives (optional)
- `return_all`: Whether to return intermediate solutions from all iterations (default: False)

### `MinimizeResult`

Class containing optimization results.

**Attributes:**
- `x`: Solution array
- `fun`: Value of the objective function at the solution
- `nfev`: Number of function evaluations
- `nit`: Number of iterations
- `message`: Description of the termination reason
- `success`: Whether the optimizer exited successfully

## Performance

This implementation leverages Rust's performance through PyO3 bindings, making it significantly faster than pure Python implementations for computationally intensive problems.

(TODO: benchmark!)

## Contributing

Maintained by [lmmx](https://github.com/lmmx). Contributions welcome!

1. **Issues & Discussions**: Please open a GitHub issue or discussion for bugs, feature requests, or questions.
2. **Pull Requests**: PRs are welcome!
   - Install the dev extra (e.g. with [uv](https://docs.astral.sh/uv/): `uv pip install -e .[dev]`)
   - Run tests (when available) and include updates to docs or examples if relevant.
   - If reporting a bug, please include the version and the error message/traceback if available.

## License

MIT License

Copyright (c) 2025 Louis Maddox
