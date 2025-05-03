# Installation Guide

GitFleet is a Python package with Rust components that provides Git repository analysis and API clients. This guide covers how to install GitFleet and its dependencies.

## Basic Installation

Install GitFleet from PyPI:

```bash
pip install gitfleet
```

This installs GitFleet with minimal dependencies required for core functionality.

## Prerequisites

- **Python**: 3.10 or higher
- **Rust**: If you're building from source, you'll need a Rust toolchain (rustc, cargo)

## Installation Options

GitFleet follows the optional dependencies pattern, allowing you to install only what you need:

### Full Installation (All Features)

```bash
pip install "gitfleet[all]"
```

### Feature-specific Installation

Choose only the features you need:

```bash
# For data analysis with pandas
pip install "gitfleet[pandas]"

# For secure token encryption
pip install "gitfleet[crypto]"

# For pydantic integration (future use)
pip install "gitfleet[pydantic]"

# For development (linting, testing, etc.)
pip install "gitfleet[dev]"

# Multiple features can be combined
pip install "gitfleet[pandas,crypto]"
```

## Dependencies Explained

### Core Dependencies

- **httpx**: Required for API clients to communicate with Git provider APIs

### Optional Dependencies

- **pandas** (`[pandas]`): For data analysis and DataFrame conversion
- **cryptography** (`[crypto]`): For secure token encryption and management
- **pydantic** (`[pydantic]`): For data validation (planned for future use)

### Development Dependencies

- **maturin**: For building the Rust components
- **pytest**: For running tests
- **black**: For code formatting
- **isort**: For import sorting

## Installation from Source

Clone the repository and install in development mode:

```bash
# Clone the repository
git clone https://github.com/bmeddeb/GitFleet.git
cd GitFleet

# Install in development mode with all dependencies
pip install -e ".[all,dev]"

# Build the Rust components
maturin develop
```

## Rust Implementation

GitFleet automatically detects if its Rust components are available and uses them for better performance. If the Rust components aren't available (for example, on platforms without Rust support), GitFleet falls back to pure Python implementations.

## Platform Support

GitFleet is tested on:
- Linux (x86_64, aarch64)
- macOS (x86_64, Apple Silicon)
- Windows (x86_64)

## Virtual Environments

It's recommended to install GitFleet within a virtual environment:

```bash
# Create a virtual environment
python -m venv venv

# Activate it (Linux/macOS)
source venv/bin/activate

# Activate it (Windows)
venv\Scripts\activate

# Install GitFleet
pip install "gitfleet[all]"
```

## Troubleshooting

### Rust Build Failures

If you encounter issues building the Rust components:

```bash
# Install required dependencies (Ubuntu/Debian)
apt-get install build-essential libssl-dev pkg-config

# Install with Python-only mode
pip install gitfleet
# Then force Python implementation in your code:
github = GitHubClient(token="your-token", use_python_impl=True)
```

### Missing Optional Dependencies

If you see warnings about missing dependencies:

```bash
# Install the required optional dependency
pip install pandas  # For data analysis
pip install cryptography  # For secure token handling
```

## Verification

Verify your installation:

```python
import GitFleet

# Check version
print(GitFleet.__version__)  # Should print "0.2.0" or newer

# Check if Rust is available (in a script)
from GitFleet import GitHubClient
client = GitHubClient(token="test")
print(f"Using Rust: {getattr(client, '_use_rust', False)}")
```