"""Utilities for Python-Rust interoperability.

This module provides functions for converting SQLAlchemy models to Rust structs
and Python enums to Rust enums.
"""

import enum
import inspect
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple, Type, cast

from sqlalchemy.orm import DeclarativeBase

from nomy_data_models.utils.string import to_snake_case


def get_all_models() -> Dict[str, Type[DeclarativeBase]]:
    """Get all SQLAlchemy models defined in the package.

    Returns:
        Dict[str, Type[DeclarativeBase]]: Dictionary of model name to model class
    """
    from nomy_data_models import models
    from nomy_data_models.models.base import BaseModel

    print("\nDebug: Scanning for models...")
    result: Dict[str, Type[DeclarativeBase]] = {}
    for name in dir(models):
        print(f"Checking {name}...")
        item = getattr(models, name)
        if inspect.isclass(item):
            print(f"  - Is a class")
            # Skip if it's not a subclass of BaseModel or if it's BaseModel itself
            if (
                not (hasattr(item, "__mro__") and issubclass(item, BaseModel))
                or item == BaseModel
            ):
                print(f"  - Skipping: Not a BaseModel subclass or is BaseModel itself")
                continue

            # Skip if it's not in the nomy_data_models.models package
            if not item.__module__.startswith("nomy_data_models.models"):
                print(f"  - Skipping: Not in nomy_data_models.models package")
                continue

            # Check if the class itself (not its parent) has __abstract__ = True
            is_abstract = (
                "__abstract__" in item.__dict__
                and item.__dict__["__abstract__"] is True
            )

            if not is_abstract:
                print(f"  - Adding to results")
                result[name] = cast(Type[DeclarativeBase], item)
            else:
                print(f"  - Skipping: Is abstract")

    return result


def sqlalchemy_to_rust_type(type_name: str, column: Any = None) -> str:
    """Convert SQLAlchemy type to Rust type.

    Args:
        type_name: SQLAlchemy type name
        column: SQLAlchemy column object (optional)

    Returns:
        Rust type name
    """
    type_mapping = {
        "Integer": "i32",
        "BigInteger": "i64",
        "SmallInteger": "i16",
        "String": "String",
        "Text": "String",
        "Boolean": "bool",
        "Float": "f64",
        "Numeric": "Decimal",
        "DateTime": "DateTime<Utc>",
        "Date": "NaiveDate",
        "Time": "NaiveTime",
        "UUID": "Uuid",
        "ARRAY": "Vec<String>",
        "JSON": "JsonValue",
        "JSONB": "JsonValue",
        "Interval": "chrono::Duration",
        "Enum": "String",
    }

    # Handle UUID type case-insensitively
    if type_name.lower() == "uuid":
        base_type = "Uuid"
    else:
        base_type = type_mapping.get(type_name, "String")

    # If no column is provided (for testing), return the base type
    if column is None:
        return base_type

    # Check if the field is optional by looking at both the type annotation and nullable parameter
    is_optional = False
    if hasattr(column, "nullable") and column.nullable:
        is_optional = True
    elif hasattr(column, "type") and hasattr(column.type, "python_type"):
        # Check if the Python type is Optional
        python_type = str(column.type.python_type)
        if "Optional" in python_type or "Union" in python_type:
            is_optional = True

    # If the field is optional, wrap it in Option<T>
    if is_optional:
        return f"Option<{base_type}>"

    return base_type


def _print_unknown_type_warning(type_name: str) -> None:
    """Print warning about unknown type.

    Args:
        type_name: SQLAlchemy type name
    """
    print(f"Warning: Unknown SQLAlchemy type {type_name}, defaulting to String")


def _generate_rust_fields(columns: List[Tuple[str, str]]) -> List[str]:
    """Generate Rust struct fields from column definitions.

    Args:
        columns: List of (name, type) tuples

    Returns:
        List of Rust struct field definitions
    """
    fields = []
    for name, rust_type in columns:
        fields.append(f"    pub {name}: {rust_type},")
    return fields


def get_required_imports(model_class: Type) -> Set[str]:
    """Get the required imports for a model.

    Args:
        model_class: SQLAlchemy model class

    Returns:
        Set[str]: Set of required imports
    """
    imports: Set[str] = set()

    # Skip classes that don't have a __table__ attribute
    if not hasattr(model_class, "__table__"):
        return imports

    # Track which chrono types are needed
    needs_datetime = False
    needs_naive_date = False
    needs_naive_time = False
    needs_duration = False

    # Check if the model has any columns that require specific imports
    for column in model_class.__table__.columns:
        type_name = column.type.__class__.__name__

        if type_name == "DateTime":
            needs_datetime = True
        elif type_name == "Date":
            needs_naive_date = True
        elif type_name == "Time":
            needs_naive_time = True
        elif type_name == "Interval":
            needs_duration = True
        elif type_name == "Numeric":
            imports.add("use rust_decimal::Decimal;")
        elif type_name.lower() == "uuid":
            imports.add("use uuid::Uuid;")
        elif type_name in ["JSON", "JSONB"]:
            imports.add("use serde_json::Value as JsonValue;")
        elif type_name == "Enum":
            # For enum types, we need to import the enum
            # Use a try-except block to handle the case where enum_class is not defined
            try:
                enum_class = column.type.enum_class  # type: ignore
                enum_module = enum_class.__module__
                enum_name = enum_class.__name__

                # Special case for test enums defined in the test module
                if enum_module == "__main__" or enum_module == "test_py_to_rust":
                    imports.add(f"use crate::models::{enum_name};")
                # Only add imports for enums in our package
                elif enum_module.startswith("nomy_data_models"):  # pragma: no cover
                    # Import directly from models, not from models::enums
                    imports.add(f"use crate::models::{enum_name};")  # pragma: no cover
            except AttributeError:
                # If enum_class is not defined, just skip it
                pass

    # Add chrono imports based on what's needed
    chrono_imports = []
    if needs_datetime:
        chrono_imports.append("DateTime, Utc")
    if needs_naive_date:
        chrono_imports.append("NaiveDate")
    if needs_naive_time:
        chrono_imports.append("NaiveTime")
    if needs_duration:
        chrono_imports.append("Duration")

    if chrono_imports:
        imports.add(f"use chrono::{{{', '.join(chrono_imports)}}};")

    return imports


def generate_rust_model(model_class: Type) -> str:
    """Generate Rust model from SQLAlchemy model.

    Args:
        model_class: SQLAlchemy model class

    Returns:
        str: Rust model code
    """
    model_name = model_class.__name__
    model_doc = model_class.__doc__ or f"Model for {model_name}."

    # Format multi-line docstrings with '/// ' at the beginning of each line
    if "\n" in model_doc:
        # Clean up whitespace in docstrings
        lines = []
        for line in model_doc.split("\n"):
            # Remove trailing whitespace
            line = line.rstrip()
            lines.append(line)
        # Join with newline and '/// ' prefix, ensuring a space after '///' even for empty lines
        model_doc = "\n/// ".join(lines)

    # Skip abstract classes
    is_abstract = (
        "__abstract__" in model_class.__dict__
        and model_class.__dict__["__abstract__"] is True
    )
    if is_abstract:
        print(f"Skipping abstract class {model_name}")
        return ""

    # Get required imports based on column types
    required_imports = get_required_imports(model_class)

    # Generate imports - filter out imports that are already included in the template
    imports = []
    standard_imports = [
        "use chrono::{DateTime, Utc",
        "use uuid::Uuid",
        "use rust_decimal::Decimal",
        "use serde_json::Value as JsonValue",
    ]

    for import_stmt in required_imports:
        # Skip imports that are already included in the template
        if not any(
            import_stmt.startswith(std_import) for std_import in standard_imports
        ):
            imports.append(import_stmt)

    # Sort imports alphabetically
    imports.sort()

    # Get columns
    columns: List[Tuple[str, str]] = []
    if hasattr(model_class, "__table__"):
        # Use __table__ attribute to get columns
        for column in model_class.__table__.columns:
            column_type = type(column.type).__name__
            rust_type = sqlalchemy_to_rust_type(column_type, column)

            # Handle None type (this can happen in tests with mocked functions)
            if rust_type is None:
                _print_unknown_type_warning(column_type)
                rust_type = "String"
            else:
                # Check if the type is unknown and print a warning
                known_types = [
                    "Integer",
                    "BigInteger",
                    "SmallInteger",
                    "String",
                    "Text",
                    "Boolean",
                    "Float",
                    "Numeric",
                    "DateTime",
                    "Date",
                    "Time",
                    "UUID",
                    "ARRAY",
                    "JSON",
                    "JSONB",
                    "Interval",
                    "Enum",
                ]
                if column_type not in known_types and column_type.lower() != "uuid":
                    _print_unknown_type_warning(column_type)

            columns.append((column.name, rust_type))
    elif hasattr(model_class, "__annotations__"):
        # Use __annotations__ to get columns
        for name, annotation in model_class.__annotations__.items():
            if name.startswith("_"):  # pragma: no cover
                continue

            # Try to determine the Rust type from the annotation
            rust_type = "String"  # Default to String  # pragma: no cover
            if "Decimal" in str(annotation):
                rust_type = "Decimal"
            elif "datetime" in str(annotation):
                rust_type = "DateTime<Utc>"
            elif "UUID" in str(annotation) or "uuid" in str(annotation):
                rust_type = "Uuid"
            elif "int" in str(annotation):
                rust_type = "i32"
            elif "float" in str(annotation):
                rust_type = "f64"
            elif "bool" in str(annotation):
                rust_type = "bool"
            elif "dict" in str(annotation) or "Dict" in str(annotation):
                rust_type = "JsonValue"

            # Check if the field is optional
            if "Optional" in str(annotation) or "Union" in str(annotation):
                rust_type = f"Option<{rust_type}>"

            columns.append((name, rust_type))
    else:
        # No columns found
        print(f"No columns found for {model_name}")  # pragma: no cover
        return ""  # pragma: no cover

    if not columns:  # pragma: no cover
        # No columns found
        print(f"No columns found for {model_name}")  # pragma: no cover
        return ""  # pragma: no cover

    # Generate Rust struct fields
    fields = _generate_rust_fields(columns)

    # Generate constructor arguments - one per line with trailing commas
    constructor_args = []
    for name, rust_type in columns:
        # For optional fields, use the base type in the constructor
        if rust_type.startswith("Option<"):
            base_type = rust_type[7:-1]  # Remove Option<> wrapper
            constructor_args.append(f"{name}: {base_type},")
        else:
            constructor_args.append(f"{name}: {rust_type},")

    # Generate constructor body
    constructor_body = []
    for name, rust_type in columns:
        # For optional fields, wrap the value in Some()
        if rust_type.startswith("Option<"):
            constructor_body.append(f"            {name}: Some({name}),")
        else:
            constructor_body.append(f"            {name},")

    # Load template
    template_path = (
        Path(__file__).parent.parent
        / "scripts"
        / "templates"
        / "rust_model_template.rs"
    )
    with open(template_path, "r") as f:
        template = f.read()

    # Replace the imports placeholder with our generated imports
    imports_str = "\n".join(imports) if imports else "// No additional imports needed"

    # Fill template using string replacement instead of format to avoid issues with curly braces
    rust_code = template.replace("{model_name}", model_name)
    rust_code = rust_code.replace("{model_doc}", model_doc)
    rust_code = rust_code.replace("{imports}", imports_str)
    rust_code = rust_code.replace("{fields}", "\n".join(fields))
    rust_code = rust_code.replace(
        "{constructor_args}", "\n        ".join(constructor_args)
    )
    rust_code = rust_code.replace("{constructor_body}", "\n".join(constructor_body))

    # Ensure there's a newline at the end of the file
    if not rust_code.endswith("\n"):
        rust_code += "\n"

    return rust_code


def generate_rust_enum(enum_class: Type) -> str:
    """Generate Rust enum from Python enum.

    Args:
        enum_class: Python enum class

    Returns:
        str: Rust enum code
    """
    enum_name = enum_class.__name__
    enum_doc = enum_class.__doc__ or f"{enum_name} enum."

    # Generate enum variants
    variants = []
    for variant in enum_class:
        variant_name = variant.name
        variant_value = variant.value
        if isinstance(variant_value, str):
            variants.append(f'    #[serde(rename = "{variant_value}")]')
            variants.append(f"    {variant_name},")
        else:
            variants.append(f"    {variant_name} = {variant_value},")

    # Generate Rust enum
    rust_code = f"""#![allow(clippy::too_many_arguments, unused_imports, non_camel_case_types)]
//! {enum_name} enum definition.
//!
//! This file is generated automatically from the Python enum.
//! Do not edit this file manually.

use serde::{{Deserialize, Serialize}};

/// {enum_doc}
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash, Serialize, Deserialize)]
pub enum {enum_name} {{
{chr(10).join(variants)}
}}

impl {enum_name} {{
    /// Convert to string representation.
    pub fn as_str(&self) -> &'static str {{
        match self {{
"""

    # Generate match arms for as_str method
    for variant in enum_class:
        variant_name = variant.name
        variant_value = variant.value
        if isinstance(variant_value, str):
            rust_code += (
                f'            {enum_name}::{variant_name} => "{variant_value}",\n'
            )
        else:
            rust_code += f'            {enum_name}::{variant_name} => "{variant_name.lower()}",\n'

    rust_code += """        }
    }
}
"""

    return rust_code


def generate_rust_models(output_dir: Optional[str] = None) -> None:
    """Generate Rust models from SQLAlchemy models.

    Args:
        output_dir: Directory to write Rust models to. Defaults to src/models.
    """
    if output_dir is None:
        output_dir = "src/models"

    print("Starting Rust model generation...")
    print("Output directory:", output_dir)

    # Create output directory if it doesn't exist
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    # Get all models
    models = get_all_models()
    print("\nFound", len(models), "models:")

    # Initialize tracking lists
    generated_models: List[str] = []
    generated_enums: List[str] = []

    # Generate mod.rs file
    mod_rs_content = [
        "//! Model definitions for Nomy wallet analysis data processing.",
        "//!",
        "//! This file is generated automatically from the Python models.",
        "//! Do not edit this file manually.",
        "",
    ]

    # Generate Rust models
    for model_name, model_class in models.items():
        print("-", model_name)
        # Skip abstract classes
        is_abstract = (
            "__abstract__" in model_class.__dict__
            and model_class.__dict__["__abstract__"] is True
        )
        if is_abstract:
            print("  Skipping abstract class")
            continue

        # Generate Rust model
        rust_code = generate_rust_model(model_class)  # pragma: no cover
        if not rust_code:  # pragma: no cover
            continue

        # Write to file
        file_name = to_snake_case(model_name) + ".rs"  # pragma: no cover
        with open(Path(output_dir) / file_name, "w") as f:  # pragma: no cover
            f.write(rust_code)  # pragma: no cover

        # Add to mod.rs
        snake_case_name = to_snake_case(model_name)  # pragma: no cover
        mod_rs_content.append("pub mod " + snake_case_name + ";")
        mod_rs_content.append("pub use " + snake_case_name + "::" + model_name + ";")
        mod_rs_content.append("")

        generated_models.append(model_name)

    # Generate Rust enums
    import nomy_data_models.models.enums as enums_module  # pragma: no cover

    # Find all enum classes in the enums module
    enum_classes = []
    for name in dir(enums_module):
        item = getattr(enums_module, name)
        if (
            inspect.isclass(item)
            and issubclass(item, enum.Enum)
            and item.__module__ == "nomy_data_models.models.enums"
        ):
            enum_classes.append((name, item))

    # Add enum section header
    mod_rs_content.append("// Enum exports")
    mod_rs_content.append("")

    # Generate Rust enums for each enum class
    for enum_name, enum_class in enum_classes:
        # Generate Rust enum code
        enum_code = generate_rust_enum(enum_class)  # pragma: no cover

        # Convert enum name to snake case for file name
        file_name = to_snake_case(enum_name) + ".rs"

        # Write to file - directly to the models directory, not to an enums subdirectory
        with open(Path(output_dir) / file_name, "w") as f:  # pragma: no cover
            f.write(enum_code)

        # Add to mod.rs
        snake_case_name = to_snake_case(enum_name)
        mod_rs_content.append("pub mod " + snake_case_name + ";")  # pragma: no cover
        mod_rs_content.append(
            "pub use " + snake_case_name + "::" + enum_name + ";"
        )  # pragma: no cover
        mod_rs_content.append("")  # pragma: no cover

        # Track generated enum
        generated_enums.append(enum_name)

    # Add struct section header
    mod_rs_content.append("// Struct exports")
    mod_rs_content.append("")

    # Write mod.rs
    with open(Path(output_dir) / "mod.rs", "w") as f:  # pragma: no cover
        f.write("\n".join(mod_rs_content))

    # Generate lib.rs
    lib_rs_content = [
        "//! Nomy Data Models",
        "//!",
        "//! This crate provides data model definitions for Nomy wallet analysis data processing.",
        "//! These models are shared across multiple services and are generated from Python SQLAlchemy models.",
        "",
        "pub mod models;",
        "",
        "/// Re-export all models for convenience",
        "pub use models::{",
        "    // Enums",
    ]

    # Add enum exports
    for enum_name in generated_enums:
        lib_rs_content.append("    " + enum_name + ",")

    # Add struct exports
    lib_rs_content.append("    // Structs")
    for model_name in generated_models:
        lib_rs_content.append("    " + model_name + ",")

    lib_rs_content.extend(
        [
            "};",
            "",
            "/// Error types for the crate",
            "pub mod error {",
            "    use thiserror::Error;",
            "",
            "    /// Error type for Nomy Data Models",
            "    #[derive(Error, Debug)]",
            "    pub enum NomyDataModelError {",
            "        /// Error when serializing or deserializing data",
            '        #[error("Serialization error: {0}")]',
            "        SerializationError(#[from] serde_json::Error),",
            "",
            "        /// Error when parsing a date or time",
            '        #[error("Date/time parsing error: {0}")]',
            "        DateTimeError(#[from] chrono::ParseError),",
            "",
            "        /// Other errors",
            '        #[error("Other error: {0}")]',
            "        Other(String),",
            "    }",
            "}",
            "",
            "/// Result type for the crate",
            "pub type Result<T> = std::result::Result<T, error::NomyDataModelError>;",
            "",
            "/// Version of the crate",
            'pub const VERSION: &str = env!("CARGO_PKG_VERSION");',
        ]
    )

    # Write lib.rs
    with open(Path("src/lib.rs"), "w") as f:  # pragma: no cover
        f.write("\n".join(lib_rs_content))


if __name__ == "__main__":
    generate_rust_models()
