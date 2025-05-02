# Nomy Data Models

This repository contains the data model definitions for Nomy wallet analysis data processing. These models are shared across multiple services:

- nomy-data-service
- nomy-data-processor
- nomy-data-ingestor

## Overview

The Nomy Data Models repository serves as a single source of truth for all data structures used in the Nomy wallet analysis ecosystem. By centralizing these models, we ensure consistency across different services and reduce duplication of code.

## Features

- **Cross-language support**: Models can be used in both Python and Rust
- **Versioned releases**: Proper versioning to manage dependencies
- **Consistent data structures**: Ensures data integrity across the entire pipeline
- **Centralized schema management**: Single source of truth for all data models
- **SQLAlchemy ORM models**: Database-ready models with full ORM support
- **Automatic Rust code generation**: Python SQLAlchemy models are automatically converted to Rust structs

## Installation

### Python

```bash
# Install from PyPI
pip install nomy-data-models

# Install from source
pip install -e .
```

### Rust

Add to your `Cargo.toml`:

```toml
[dependencies]
nomy-data-models = { version = "0.1.0", git = "https://github.com/bcnmy/nomy-data-models" }
```

## Usage

### Python

```python
from nomy_data_models.models import WalletState, ServiceState, RawTrade, EnrichedTrade, Position

# Use the models with SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

engine = create_engine("sqlite:///nomy.db")
with Session(engine) as session:
    wallet_state = WalletState(
        wallet_address="0x1234567890abcdef1234567890abcdef12345678",
        chain_id=1
    )
    session.add(wallet_state)
    session.commit()
```

### Rust

```rust
use nomy_data_models::models::{WalletState, ServiceState, RawTrade, EnrichedTrade, Position};

// Use the model
let wallet_state = WalletState {
    wallet_address: "0x1234567890abcdef1234567890abcdef12345678".to_string(),
    chain_id: 1,
    // ... other fields
};
```

## Development Setup

### Pre-commit Hooks

This repository uses pre-commit hooks to ensure code quality and consistency. After cloning the repository, install the pre-commit hooks:

```bash
# Make the script executable
chmod +x ./scripts/install-hooks.sh

# Install the hooks
./scripts/install-hooks.sh
```

The pre-commit hooks will automatically:

- Format code with Black
- Sort imports with isort
- Run Python tests
- Generate and verify Rust models
- Format Rust code with rustfmt
- Run Rust linting with Clippy

**Important**: Always ensure the pre-commit hooks are installed and up-to-date. They are essential for maintaining code quality and preventing CI failures.

## Development

### Prerequisites

- Python 3.8+
- Rust 1.50+
- Poetry (for Python dependency management)
- Cargo (for Rust dependency management)

### Setup

1. Clone the repository
2. Install Python dependencies: `poetry install`
3. Build Rust package: `cargo build`
4. Install git hooks: `./scripts/install-hooks.sh`

### Git Hooks

This repository includes git hooks to automate certain tasks:

- **pre-commit**: Automatically generates Rust models from Python models and verifies they build correctly before each commit

To install the git hooks, run:

```bash
./scripts/install-hooks.sh
```

This ensures that all Rust models are kept in sync with their Python counterparts and that they build correctly.

### Adding New Models

1. Add the model definition to the appropriate Python file in `nomy_data_models/models/`
2. Update the `__init__.py` files to export the new model
3. Run the code generation script: `python scripts/generate_rust.py`
4. Verify the generated Rust code in `src/models/`
5. Add tests for both Python and Rust implementations

### Testing

```bash
# Run Python tests
pytest tests/python

# Run Rust tests
cargo test
```

## Contributing

Please follow these steps when contributing:

1. Create a new branch for your feature
2. Add or modify models as needed
3. Ensure tests pass for both Python and Rust
4. Submit a pull request

## Package Deployment

### Preconditions

Before deploying a new version, ensure you have:

1. Updated the version number in `Cargo.toml` for the Rust package
2. Updated the version number in `pyproject.toml` for the Python package

### Automated Deployment

When your changes are merged into the main branch, the CI pipeline will automatically:

1. Deploy the Python package to PyPI (https://pypi.org/)
2. Deploy the Rust package to crates.io (https://crates.io/)

The deployment process is handled automatically by the CI pipeline, so you don't need to perform any manual steps after merging to main.

## Python-to-Rust Conversion

This repository includes a utility for automatically converting Python SQLAlchemy models to Rust structs. This ensures that the data models are consistent across both languages.

### How it works

1. Python SQLAlchemy models are defined in the `nomy_data_models/models` directory
2. The `nomy_data_models/py_to_rust.py` module provides functions for converting these models to Rust
3. The `scripts/generate_rust.py` script can be used to generate Rust code from the command line

### Usage

To generate Rust models from Python SQLAlchemy models:

```bash
python scripts/generate_rust.py [output_dir]
```

If `output_dir` is not specified, the default is `src/models`.

### Testing

To test the conversion process:

```bash
python scripts/test_conversion.py
```

This will generate Rust code in the `scripts/test_output/models` directory and run various tests to ensure the conversion is working correctly.
