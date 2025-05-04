use super::*;
use approx::assert_relative_eq;
use ndarray::Array1;
use scirs2_optimize::unconstrained::Options;

fn quadratic(x: &[f64]) -> f64 {
    x.iter().map(|&xi| xi * xi).sum()
}

// Test PyOptions conversion
#[test]
fn test_pyoptions_conversion() {
    let py_options = PyOptions {
        maxiter: Some(1000),
        ftol: Some(1e-16),
        gtol: Some(1e-20),
        eps: Some(10.0),
        disp: true,
        ..PyOptions::default()
    };

    let options: Options = py_options.into();

    assert_eq!(options.maxiter, Some(1000), "maxiter differs");
    assert_eq!(options.ftol, Some(1e-16), "ftol differs");
    assert!(options.disp, "disp differs");
    assert!(!options.return_all, "return_all differs");
    assert_eq!(options.gtol, Some(1e-20), "gtol differs");
    assert_eq!(options.eps, Some(10.0), "eps differs");
    assert_eq!(
        options.finite_diff_rel_step, None,
        "finite_diff_rel_step differs"
    );
}

// Test with a basic quadratic function using direct rust calls
// This tests the interaction with the underlying scirs2-optimize library
#[test]
fn test_quadratic_minimization() {
    // Define a simple quadratic function
    // Initial point
    let x0 = Array1::from(vec![1.0, 1.0]);

    // Options
    let options = Options {
        maxiter: Some(100),
        ftol: Some(1e-3),
        ..Options::default()
    };

    // Minimize
    let result = minimize(quadratic, &x0, Method::Powell, Some(options)).unwrap();
    println!("{}", result);

    // The minimum of x^2 + y^2 is at (0, 0)
    assert_relative_eq!(result.x[0], 0.0, epsilon = 1e-5);
    assert_relative_eq!(result.x[1], 0.0, epsilon = 1e-5);
    assert_relative_eq!(result.fun, 0.0, epsilon = 1e-5);
    assert!(result.success);
}

// Test with a more complex function - Rosenbrock function
#[test]
fn test_rosenbrock_minimization() {
    // Define the Rosenbrock function
    let rosenbrock =
        |x: &[f64]| -> f64 { 100.0 * (x[1] - x[0] * x[0]).powi(2) + (1.0 - x[0]).powi(2) };

    // Initial point
    let x0 = Array1::from(vec![0.0, 0.0]);

    // Options with higher iteration limit for this challenging function
    let options = Options {
        maxiter: Some(2000),
        ..Options::default()
    };

    // Minimize
    let result = minimize(rosenbrock, &x0, Method::Powell, Some(options)).unwrap();

    // The minimum of the Rosenbrock function is at (1, 1)
    assert_relative_eq!(result.x[0], 1.0, epsilon = 1e-4);
    assert_relative_eq!(result.x[1], 1.0, epsilon = 1e-4);
    assert_relative_eq!(result.fun, 0.0, epsilon = 1e-4);
    assert!(result.success);
}
