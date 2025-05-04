import powell_opt as po


def rosenbrock(x):
    """Rosenbrock function - a classical test case for optimization"""
    return 100 * (x[1] - x[0] ** 2) ** 2 + (1 - x[0]) ** 2


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
