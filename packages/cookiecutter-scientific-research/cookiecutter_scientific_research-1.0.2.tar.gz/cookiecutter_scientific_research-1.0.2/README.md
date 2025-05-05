# 🧪 Cookiecutter Scientific Research

<p align="center">
  <strong>A standardized, flexible template for scientific research projects</strong>
</p>

<p align="center">
  <a href="#project-overview">Project Overview</a> •
  <a href="#features">Features</a> •
  <a href="#quick-start">Quick Start</a> •
  <a href="#project-structure">Project Structure</a> •
  <a href="#development-guide">Development Guide</a> •
  <a href="#acknowledgements">Acknowledgements</a> •
  <a href="#license">License</a>
</p>

## 📋 Project Overview

Cookiecutter Scientific Research is a project template generator designed for scientific research projects, aimed at providing a standardized structure and tool configuration to help researchers focus on scientific discovery rather than project setup. Through predefined best practices, this template supports high-quality scientific computing and data analysis workflows, ensuring the reproducibility and reliability of the research process.

## ✨ Features

- **Standardized Project Structure** - Conforms to best practices for modern scientific computing projects

- **Reproducible Experimental Environment** - Built-in environment management and dependency locking mechanisms
- **Integrated Documentation System** - Preconfigured MkDocs documentation for showcasing research results
- **Testing and Quality Control** - Built-in testing frameworks and code quality tools
- **Modern Package Management** - Simplifies dependency management using modern tools like uv/pip

## 🚀 Quick Start

### Prerequisites

- Python 3.9 or higher
- [uv](https://docs.astral.sh/uv/) or [pipx](https://pipx.pypa.io/stable/) (recommended for tool installation)

### Installation

This project is available on PyPI. As a cross-project tool, we recommend using uv or pipx for installation:

```bash
# Install using uv (recommended)
uv tool install cookiecutter-scientific-research

# Or install using pipx
pipx install cookiecutter-scientific-research
```

### Creating a New Project

After installation, simply run the following command and follow the prompts:

```bash
ccsr
```

### Initializing the Project Environment

After creating the project, navigate to the project directory and initialize the environment:

```bash
cd your-project-name

# Use uv to manage dependencies (recommended)
uv lock
uv sync
```

## 📂 Project Structure

The generated project follows the directory structure below, with each section having a clear responsibility:

```
├── LICENSE            <- Project license
├── Makefile           <- Makefile with common commands
├── README.md          <- Project documentation
├── pyproject.toml     <- Project configuration and dependency management
│
├── data               <- Data directory
│   ├── external       <- Third-party data
│   ├── interim        <- Intermediate processed data
│   ├── processed      <- Final analysis datasets
│   └── raw            <- Original data (read-only)
│
├── {{ cookiecutter.module_name }}  <- Project source code
│   ├── __init__.py    <- Package initialization file
│   ├── config.py      <- Configuration parameter management
│   ├── dataset.py     <- Data acquisition and loading
│   ├── plots.py       <- Data visualization functions
│   │
│   ├── analyze        <- Data analysis module
│   │   └── analysis.py
│   │
│   ├── modeling       <- Model training and prediction
│   │   ├── __init__.py
│   │   ├── predict.py <- Model prediction
│   │   └── train.py   <- Model training
│   │
│   ├── models         <- Model definitions
│   │   ├── __init__.py
│   │   └── model.py   <- Model architecture
│   │
│   ├── process        <- Data processing
│   │   └── features.py <- Feature engineering
│   │
│   └── utils          <- Utility functions
│       ├── __init__.py
│       └── tools.py   <- General utilities
│
├── notebooks          <- Jupyter/Marimo notebooks
│                         (Naming convention: number-creator-description)
│
├── docs               <- Project documentation (MkDocs)
│
├── references         <- Reference materials and literature
│
├── reports            <- Analysis reports and results
│   ├── figures        <- Generated charts
│   └── logs           <- Experiment logs
│
└── tests              <- Test directory
```

## 🔧 Development Guide

### Package Management and Building

This project uses `flit_core` as the build backend, supporting modern Python package management. To build distribution packages:

```bash
# Install build dependencies
uv lock
# Install all optional dependencies
uv sync --all-extras
# Or install specific dependency groups
uv sync -e dev    # Development dependencies
uv sync -e test   # Testing dependencies
uv sync -e docs   # Documentation dependencies

# Build distribution packages
uv build
```

The built wheel files and source distribution packages will be saved in the `dist/` directory.

### Project Customization

During the template generation process, you can customize various aspects of the project according to prompts:

- Project name and module name
- Author information
- License type
- Dependency management method
- Test framework selection
- And more

## 🙏 Acknowledgements

This project is modified from [cookiecutter-data-science](https://github.com/drivendataorg/cookiecutter-data-science), special thanks to the DrivenData team for providing the excellent template and inspiration. The project has been customized for scientific research scenarios on the original basis, including tool chain optimization, workflow adjustments, and documentation structure optimization.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
