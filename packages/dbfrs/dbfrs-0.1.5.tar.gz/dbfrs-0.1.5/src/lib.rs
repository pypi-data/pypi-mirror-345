mod types;

use types::{Field, FieldType, Fields};

use dbase::{FieldInfo, FieldValue};
use pyo3::prelude::*;
use pyo3::types::{PyList, PyString, PyTuple};
use pyo3::wrap_pyfunction;

/// Returns the number of records in a DBF file.
///
/// # Arguments
/// * `path` - A string that represents the path to the DBF file
///
/// # Returns
/// * The number of records in the DBF file
///
/// # Errors
/// * Returns an error if the file cannot be opened or read
/// * Returns an error if the file is not a valid DBF file
///
/// # Example
/// ```python
/// import dbfrs
/// count = dbfrs.get_record_count("path/to/dbf")
/// print(f"The DBF file contains {count} records")
/// ```
#[pyfunction]
fn get_record_count(path: String) -> PyResult<usize> {
    // Open the file with proper error handling
    let reader = dbase::Reader::from_path_with_encoding(&path, dbase::yore::code_pages::CP437)
        .map_err(|e| {
            pyo3::exceptions::PyIOError::new_err(
                format!("Failed to open DBF file '{}': {}", path, e)
            )
        })?;
    
    let table_info = reader.header();

    Ok(table_info.num_records as usize)
}

fn _get_dbf_fields(path: String) -> Vec<FieldInfo> {
    let reader = dbase::Reader::from_path_with_encoding(path, dbase::yore::code_pages::CP437).unwrap();
    let mut fields = Vec::new();

    for field in reader.fields() {
        if field.name() == "DeletionFlag" {
            continue;
        }
        fields.push(field.clone());
    }

    fields
}

/// This function takes a path to a dbf file and returns a list of fields
/// that are in the dbf file.
/// # Arguments
/// * `path` - A string that represents the path to the dbf file
/// # Returns
/// * A list of strings that represent the fields in the dbf file
/// # Example
/// ```python
/// import dbfrs
/// fields = dbfrs.get_dbf_fields("path/to/dbf")
/// print(fields)
/// ```
#[pyfunction]
fn get_dbf_fields(path: String) -> PyResult<Vec<Field>> {
    let reader = dbase::Reader::from_path_with_encoding(path, dbase::yore::code_pages::CP437).unwrap();

    let mut fields = Vec::new();

    for field in reader.fields() {
        if field.name() == "DeletionFlag" {
            continue;
        }
        let py_field = Field {
            name: field.name().to_string(),
            field_type: match field.field_type() {
                dbase::FieldType::Character => FieldType::Character,
                dbase::FieldType::Numeric => FieldType::Numeric,
                dbase::FieldType::Date => FieldType::Date,
                dbase::FieldType::Logical => FieldType::Logical,
                _ => panic!("Unsupported field type"),
            },
            size: field.length(),
            decimals: None, // Adjust based on your actual needs
        };
        fields.push(py_field);
    }

    Ok(fields)
}


/// # Note
/// This function is not meant to be used directly. It is used by the `load_dbf` function.
/// TODO: Make only_fields optional and load all fields if not provided
///
/// # Arguments
/// * `path` - A string that represents the path to the dbf file
/// * `only_fields` - A list of strings that represent the fields to be loaded
/// # Returns
/// * A list of lists that represent the records in the dbf file
/// # Example
/// ```python
/// import dbfrs
/// records = dbfrs.load_dbf("path/to/dbf", ["field1", "field2"])
/// print(records)
/// ```
#[pyfunction]
fn load_dbf<'py>(py: Python<'py>, path: String, only_fields: Option<Vec<String>>) -> PyResult<Bound<'py, PyList>> {
    let list = PyList::empty_bound(py);

    let mut reader = dbase::Reader::from_path_with_encoding(&path, dbase::yore::code_pages::CP437).unwrap();

    // Determine fields to load
    let fields_to_load = if let Some(fields) = only_fields {
        fields
    } else {
        // If only_fields is None, use get_dbf_fields to fetch all fields
        _get_dbf_fields(path.clone()).iter().map(|field| field.name().to_string()).collect()
    };

    for record_result in reader.iter_records() {
        let record = record_result.unwrap();
        let mut local = Vec::new();  // Use a Rust Vec to collect Py objects for this record

        for field_name in fields_to_load.iter() {
            let value = record.get(field_name);

            let py_value = match value {
                None => py.None(),
                Some(value) => match value {
                    FieldValue::Character(Some(string)) => string.into_py(py),
                    FieldValue::Numeric(value) => value.into_py(py),
                    FieldValue::Date(date) => date.expect("Error").to_string().into_py(py),
                    FieldValue::Logical(bool) => bool.into_py(py),
                    FieldValue::Character(v) => v.clone().into_py(py),
                    _ => panic!("Unhandled Type: {}", value)
                }
            };
            local.push(py_value);
        }
        list.append(PyTuple::new_bound(py, &local))?;  // Convert each record's Vec to PyTuple and append to the list
    }
    Ok(list)  // Return the list of tuples
}

/// This function writes a dbf file to the specified path.
/// # Arguments
/// * `fields` - A Fields object that represents the fields in the dbf file
/// * `records` - A list of lists that represent the records in the dbf file
/// * `path` - A string that represents the path to the dbf file
/// # Example
/// ```python
/// import dbfrs
/// fields = dbfrs.Fields()
/// fields.add_character_field("first_name", 20)
/// fields.add_character_field("last_name", 20)
/// fields.add_numeric_field("age", 20, 1)
/// fields.add_logical_field("is_happy")
/// records = [("John", "Doe", 33, True), ("Jane", "Smith", 44, False)]
/// dbfrs.write_dbf(fields, records, "path/to/dbf")
/// ```
/// # Note
/// * The fields in the Fields object must match the fields in the records
/// * The order of the fields in the Fields object must match the order of the fields in the records
#[pyfunction]
fn write_dbf<'py>(fields: Fields, records: &Bound<'py, PyList>, path: String) -> PyResult<()> {
    let mut builder = dbase::TableWriterBuilder::with_encoding(dbase::yore::code_pages::CP437);

    for field in &fields.fields {
        let field_name = dbase::FieldName::try_from(field.name.as_str()).unwrap();

        match field.field_type {
            FieldType::Character => {
                builder = builder.add_character_field(field_name, field.size);
            }
            FieldType::Numeric => {
                builder = builder.add_numeric_field(field_name, field.size, field.decimals.unwrap());
            }
            FieldType::Date => {
                builder = builder.add_date_field(field_name);
            }
            FieldType::Logical => {
                builder = builder.add_logical_field(field_name);
            }
        }
    }

    let mut writer = builder.build_with_file_dest(path).unwrap();

    for item in records.iter() {
        let tuple = item.downcast::<PyTuple>()?;

        let mut record = dbase::Record::default();

        for (index, field) in fields.fields.iter().enumerate() {
            match field.field_type {
                FieldType::Character => {
                    let value_py: &Bound<'py, PyString> = &tuple.get_item(index)?.downcast_into()?;
                    let value = value_py.to_string();
                    record.insert(field.name.clone(), dbase::FieldValue::Character(Some(value.clone())));
                }
                FieldType::Numeric => {
                    let value_py: &Bound<'py, PyAny> = &tuple.get_item(index)?;
                    let value: f64 = value_py.extract()?;
                    record.insert(field.name.clone(), dbase::FieldValue::Numeric(Some(value)));
                }
                FieldType::Date => {
                    let value_py: &Bound<'py, PyString> = &tuple.get_item(index)?.downcast_into()?;
                    let value = value_py.to_string();
                    record.insert(field.name.clone(), dbase::FieldValue::Date(Some(value.parse().unwrap())));
                }
                FieldType::Logical => {
                    let value_py: &Bound<'py, PyAny> = &tuple.get_item(index)?;
                    let value: bool = value_py.extract()?;
                    record.insert(field.name.clone(), dbase::FieldValue::Logical(Some(value)));
                }
            }
        }

        writer.write_record(&record).unwrap();
    }

    Ok(())
}

/// This module is a python module that provides functions to read and write dbf files.
#[pymodule]
fn dbfrs(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<Fields>()?;
    m.add_class::<Field>()?;
    m.add_class::<FieldType>()?;

    m.add_function(wrap_pyfunction!(load_dbf, m)?)?;
    m.add_function(wrap_pyfunction!(get_dbf_fields, m)?)?;
    m.add_function(wrap_pyfunction!(write_dbf, m)?)?;
    m.add_function(wrap_pyfunction!(get_record_count, m)?)?;

    Ok(())
}
