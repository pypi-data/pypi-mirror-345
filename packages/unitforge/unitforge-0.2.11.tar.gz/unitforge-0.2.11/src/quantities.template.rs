use pyo3::{Bound, PyAny, prelude::*};

#[derive(Clone, Copy, PartialEq, Debug)]
pub enum Quantity {
    //Is used for runtime checked operations with quantities
    FloatQuantity(f64),
    // __QUANTITY_VARIANTS__
}

impl Quantity {
    pub fn to(&self, unit: Unit) -> Result<f64, String> {
        match (self, unit) {
            (Quantity::FloatQuantity(value), Unit::NoUnit) => Ok(*value),
            // __QUANTITY_TO_VARIANTS__
            _ => Err("Cannot use given pair of quantity and unit.".to_string())
        }
    }
}

#[derive(Clone, Copy, PartialEq, Debug)]
pub enum Unit {
    //Is used for runtime checked operations with quantities
    NoUnit,
    // __UNIT_VARIANTS__
}

impl Unit {
    pub fn to_quantity(&self, value: f64) -> Quantity {
        match self {
            Unit::NoUnit => Quantity::FloatQuantity(value),
            // __TO_QUANTITY_VARIANTS__
        }
    }

    pub fn from_py_any(v: &Bound<PyAny>) -> Result<Self, String> {
        // __EXTRACT_UNIT_MATCHES__
        else {
            Err("Cannot interpret given value as Quantity".to_string())
        }
    }
}

pub fn extract_f64(v: &Bound<PyAny>) -> Option<f64> {
    if let Ok(inner) = v.extract::<f64>() {
        Some(inner)
    } else if let Ok(inner) = v.extract::<f32>() {
        Some(inner as f64)
    } else if let Ok(inner) = v.extract::<i32>() {
        Some(inner as f64)
    } else if let Ok(inner) = v.extract::<i64>() {
        Some(inner as f64)
    } else {
        None
    }
}

impl Quantity {
    pub fn from_py_any(v: &Bound<PyAny>) -> Result<Self, String> {
        if let Some(inner) = extract_f64(v) {
            Ok(Quantity::FloatQuantity(inner))
        }
        // __EXTRACT_QUANTITY_MATCHES__
        else {
            Err("Cannot interpret given value as Quantity".to_string())
        }
    }

    pub fn to_pyobject(self, py: Python) -> PyObject {
        match self {
            Quantity::FloatQuantity(v) => v.into_py(py),
            // __TO_PYOBJECT_MATCHES__
        }
    }

    pub fn multiply(self, rhs: Self) -> Option<Self> {
        fn try_multiply(lhs: &Quantity, rhs: &Quantity) -> Option<Quantity> {
            use Quantity::*;
            match (lhs, rhs) {
                (FloatQuantity(v_lhs), FloatQuantity(v_rhs)) => Some(FloatQuantity(v_lhs * v_rhs)),
                // __MUL_MATCHES__
                _ => None
            }
        }
        match try_multiply(&self, &rhs) {
            Some(result) => Some(result),
            None => try_multiply(&rhs, &self)
        }
    }

    pub fn divide(self, rhs: Self) -> Option<Self> {
        use Quantity::*;
        match (self, rhs) {
            (FloatQuantity(v_lhs), FloatQuantity(v_rhs)) => Some(FloatQuantity(v_lhs / v_rhs)),
            // __DIV_MATCHES__
            _ => None
        }
    }

    #[allow(clippy::should_implement_trait)]
    pub fn add(self, rhs: Self) -> Option<Self> {
        use Quantity::*;
        match (self, rhs) {
            (Quantity::FloatQuantity(v_lhs), Quantity::FloatQuantity(v_rhs)) => Some(Quantity::FloatQuantity(v_lhs + v_rhs)),
            // __ADD_QUANTITY_MATCHES__
            _ => None
        }
    }

    #[allow(clippy::should_implement_trait)]
    pub fn sub(self, rhs: Self) -> Option<Self> {
        use Quantity::*;
        match (self, rhs) {
            (Quantity::FloatQuantity(v_lhs), Quantity::FloatQuantity(v_rhs)) => Some(Quantity::FloatQuantity(v_lhs - v_rhs)),
            // __SUB_QUANTITY_MATCHES__
            _ => None
        }
    }

    pub fn extract_float(&self) -> Result<f64, String> {
        match self {
            Quantity::FloatQuantity(v) => Ok(*v),
            _ => Err("Cannot extract float from Quantity enum".into()),
        }
    }

    // __BASE_QUANTITY_MATCHES__

    pub fn sqrt(&self) -> Option<Self> {
        match self {
            Quantity::FloatQuantity(v) => Some(Self::FloatQuantity(v.sqrt())),
            // __QUANTITY_SQRTS__
            _=> None
        }
    }
}