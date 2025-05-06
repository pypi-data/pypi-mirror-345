use pyo3::{pyclass, pymethods};

#[pyclass]
#[derive(Clone, Copy, Debug)]
pub enum FieldType {
    Character,
    Numeric,
    Date,
    Logical,
}

#[pymethods]
impl FieldType {
    fn __str__(&self) -> String {
        match self {
            FieldType::Character => "C".to_string(),
            FieldType::Numeric => "N".to_string(),
            FieldType::Date => "D".to_string(),
            FieldType::Logical => "L".to_string(),
        }
    }

    fn __repr__(&self) -> String {
        match self {
            FieldType::Character => "FieldType.Character".to_string(),
            FieldType::Numeric => "FieldType.Numeric".to_string(),
            FieldType::Date => "FieldType.Date".to_string(),
            FieldType::Logical => "FieldType.Logical".to_string(),
        }
    }
}

/// This struct represents a field in a dbf file.
/// # Fields
/// * `name` - A string that represents the name of the field
/// * `field_type` - A string that represents the type of the field
/// * `size` - A u8 that represents the size of the field
#[pyclass]
#[derive(Clone)]
pub struct Field {
    pub name: String,
    pub field_type: FieldType,
    pub size: u8,
    pub decimals: Option<u8>,
}

#[pymethods]
impl Field {
    #[staticmethod]
    pub fn new_character(name: String, size: u8) -> Field {
        Field {
            name,
            field_type: FieldType::Character,
            size,
            decimals: None,
        }
    }

    // Constructor for numeric fields
    #[staticmethod]
    pub fn new_numeric(name: String, size: u8, decimals: u8) -> Field {
        Field {
            name,
            field_type: FieldType::Numeric,
            size,
            decimals: Some(decimals),
        }
    }

    // Constructor for logical fields
    #[staticmethod]
    pub fn new_logical(name: String) -> Field {
        Field {
            name,
            field_type: FieldType::Logical,
            size: 1, // Logical fields always have a size of 1
            decimals: None,
        }
    }

    // Constructor for date fields
    #[staticmethod]
    pub fn new_date(name: String) -> Field {
        Field {
            name,
            field_type: FieldType::Date,
            size: 8,  // Example: if date has a standard size
            decimals: None,
        }
    }

    #[getter]
    fn get_name(&self) -> &str {
        &self.name
    }

    #[getter]
    fn get_type(&self) -> FieldType {
        self.field_type
    }

    #[getter]
    fn get_size(&self) -> u8 {
        self.size
    }

    #[getter]
    fn get_decimals(&self) -> u8 {
        self.decimals.unwrap_or(0)
    }
}

/// This struct represents a list of fields in a dbf file.
/// # Fields
/// * `fields` - A vector of Field objects that represent the fields in the dbf file
/// # Example
/// ```python
/// fields = Fields()
/// fields.add("field1", "C", 10)
/// fields.add("field2", "N", 10)
/// fields.list_fields()
#[pyclass]
#[derive(Clone)]
pub struct Fields {
    pub fields: Vec<Field>,
}

#[pymethods]
impl Fields {
    #[new]
    fn new() -> Self {
        Fields {
            fields: Vec::new(),
        }
    }

    fn add_character_field(&mut self, name: String, size: u8) {
        let field = Field {
            name,
            field_type: FieldType::Character,
            size,
            decimals: None,
        };
        self.fields.push(field);
    }

    fn add_numeric_field(&mut self, name: String, size: u8, decimals: u8) {
        let field = Field {
            name,
            field_type: FieldType::Numeric,
            size,
            decimals: Some(decimals),
        };
        self.fields.push(field);
    }

    fn add_date_field(&mut self, name: String) {
        let field = Field {
            name,
            field_type: FieldType::Date,
            size: 8,
            decimals: None,
        };
        self.fields.push(field);
    }

    fn add_logical_field(&mut self, name: String) {
        let field = Field {
            name,
            field_type: FieldType::Logical,
            size: 1,
            decimals: None,
        };
        self.fields.push(field);
    }
}
