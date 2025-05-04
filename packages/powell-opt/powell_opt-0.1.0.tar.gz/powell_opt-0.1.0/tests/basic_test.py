import math
import time

import powell_opt as po


def test_powell_quadratic():
    """Basic example of Powell's method for a simple quadratic function"""

    def quadratic(x):
        """Simple quadratic function: f(x) = x[0]^2 + x[1]^2"""
        return x[0] ** 2 + x[1] ** 2

    print("\n=== Powell's Method - Quadratic Function ===")

    # Initial guess
    x0 = [1.0, 1.0]

    # Minimize using Powell's method
    start_time = time.time()
    result = po.minimize(quadratic, x0)
    end_time = time.time()

    print(f"Solution: {result.x}")
    print(f"Function value: {result.fun}")
    print(f"Number of iterations: {result.nit}")
    print(f"Number of function evaluations: {result.nfev}")
    print(f"Success: {result.success}")
    print(f"Execution time: {end_time - start_time:.4f} seconds")
    assert math.isclose(result.fun, 0.0, abs_tol=1e-2)
    assert math.isclose(result.x[0], 0.0, abs_tol=1e-2)
    assert math.isclose(result.x[1], 0.0, abs_tol=1e-2)


def test_powell_rosenbrock():
    """Example of Powell's method for the more challenging Rosenbrock function"""

    def rosenbrock(x):
        """Rosenbrock function - a classical test case for optimization
        Has a narrow curved valley with the minimum at (1, 1)
        """
        return 100 * (x[1] - x[0] ** 2) ** 2 + (1 - x[0]) ** 2

    print("\n=== Powell's Method - Rosenbrock Function ===")

    # Initial guess
    x0 = [0.0, 0.0]

    # Set options
    options = po.Options(maxiter=2000, ftol=1e-8)

    # Minimize using Powell's method
    start_time = time.time()
    result = po.minimize(rosenbrock, x0, options)
    end_time = time.time()

    print(f"Solution: {result.x}")
    print(f"Function value: {result.fun}")
    print(f"Number of iterations: {result.nit}")
    print(f"Number of function evaluations: {result.nfev}")
    print(f"Success: {result.success}")
    print(f"Execution time: {end_time - start_time:.4f} seconds")

    # Expected solution is [1.0, 1.0]
    print(
        f"Distance from known minimum: [{abs(result.x[0]-1.0):.6f}, {abs(result.x[1]-1.0):.6f}]"
    )
    assert math.isclose(result.fun, 0.0, abs_tol=1e-2)
    assert math.isclose(result.x[0], 1.0, abs_tol=1e-2)
    assert math.isclose(result.x[1], 1.0, abs_tol=1e-2)


def test_powell_higher_dimension():
    """Example of Powell's method for a higher-dimensional problem"""

    def sum_squares(x):
        """Sum of squares function: f(x) = x[0]^2 + x[1]^2 + ... + x[n-1]^2"""
        return sum(xi**2 for xi in x)

    print("\n=== Powell's Method - Higher Dimensional Problem ===")

    # Initial guess - 10 dimensional problem
    x0 = [1.0] * 10

    # Minimize using Powell's method
    start_time = time.time()
    result = po.minimize(sum_squares, x0)
    end_time = time.time()

    print(f"Solution (10 dimensions): {result.x}")
    print(f"Function value: {result.fun}")
    print(f"Number of iterations: {result.nit}")
    print(f"Number of function evaluations: {result.nfev}")
    print(f"Success: {result.success}")
    print(f"Execution time: {end_time - start_time:.4f} seconds")
