use std::{fs::File, io::{BufRead, BufReader}, path::Path};

use pyo3::{exceptions::PyIOError, prelude::*, types::PyDict};


#[pyfunction]
fn hyd_env(py:Python, path: &str) -> PyResult<()> {
    let p = Path::new(path);
    let file = File::open(p)
        .map_err(|e| PyErr::new::<PyIOError, _>(format!("Failed to open .env file: {}", e)))?;
    let reader = BufReader::new(file);

    let env_vars = PyDict::new(py);

    for (i, line_result) in reader.lines().enumerate() {
        let line = line_result
            .map_err(|e| PyErr::new::<PyIOError, _>(format!("Failed to read line: {}", e)))?;
        let line = line.trim();

        if line.is_empty() || line.starts_with('#') {
            continue;
        }

        let parts: Vec<&str> = line.splitn(2, '=').collect();
        if parts.len() != 2 {
            return Err(PyErr::new::<PyIOError, _>(format!("Invalid line {} in .env file '{}'", i, line)));
        }

        let key = parts[0].trim();
        let value = parts[1].trim().trim_matches('"');

        env_vars.set_item(key, value)?;
    }

    let os = py.import("os")?;
    let environ = os.getattr("environ")?;
    environ.call_method1("update", (env_vars,))?;
    Ok(())
}

#[pymodule(name = "min_dotenv")]
fn min_dotenv(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(hyd_env, m)?)?;
    Ok(())
}
