use pyo3::prelude::*;

#[pyfunction]
pub fn fib (n: u32) -> u32 {
    if n <= 0 {
          return 0;
    } else if n== 1{
          return 1;
} else {
    return fib (n-1)  + fib(n-2);
 }
}

#[pyfunction]
fn add(a: i32, b: i32) -> i32 {
    a + b
}

#[pyfunction]
fn greet(name: &str) -> String {
    format!("Hallo, {}!", name)
}

#[pymodule]
fn pyrust(m: &Bound<'_, PyModule>)-> PyResult<()> {
    m.add_function(wrap_pyfunction!(fib, m)?)?;
    m.add_function(wrap_pyfunction!(add, m)?)?;
    m.add_function(wrap_pyfunction!(greet, m)?)?;
    Ok(())
}
