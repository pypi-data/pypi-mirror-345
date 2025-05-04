# Contributing to pstatstools

Thank you for your interest in contributing to this project! This document provides guidelines and instructions for contributing.

## Code of Conduct

By participating in this project, you are expected to uphold our Code of Conduct.

## How to Contribute

### Reporting Bugs

If you find a bug, please create an issue in our GitHub repository with the following information:

- A clear, descriptive title
- A detailed description of the bug
- Steps to reproduce the issue
- Expected behavior
- Actual behavior
- Screenshots (if applicable)
- Environment information (OS, python version, conda version, etc.)

### Suggesting Features

We welcome feature suggestions! Please create an issue with:

- A clear, descriptive title
- A detailed description of the proposed feature
- Any relevant examples or mockups
- Explanation of why this feature would be useful to the project

### Pull Requests

1. Fork the repository
2. Create a new branch from `master`: `git checkout -b user/feature/your-feature-name`
3. Make your changes
4. Add or update tests as needed
5. Make sure all tests pass (if applicable)
6. Commit your changes with clear, descriptive commit messages
7. Push your branch to your forked repository
8. Submit a pull request to the `master` branch of the original repository

### Pull Request Guidelines

- Follow the coding style and conventions used in the project
- Include appropriate tests for your changes
- Update documentation as necessary
- One pull request per feature or bug fix
- Link any relevant issues in the pull request description

## Development Setup

# Installation Guide for pstatstools

This guide explains how to install the pstatstools package and its dependencies using different package managers.

## Option 1: Using pip (standard Python package manager)

The simplest way to install the package with its dependencies:

```bash
# Install directly from the repository (development mode)
pip install -e .

# Or using the requirements file
pip install -r requirements.txt

# Once published to PyPI, you can install with:
pip install pstatstools
```

## Option 2: Using Conda (recommended)

Conda provides better management of binary dependencies and isolated environments:

```bash
# Create and activate a new conda environment with all dependencies
conda env create -f environments/environment-dev.yml
conda activate pstatstools-dev

# If you already have an environment, you can update it:
conda env update -f environments/environment-dev.yml
```

## Option 3: Using uv (faster Python package installer)

[uv](https://github.com/astral-sh/uv) is a newer, faster Python package installer:

```bash
# Install uv if you don't have it
pip install uv

# Install the package and dependencies
uv pip install -e .

# Or install just the dependencies
uv pip install -r requirements.txt
```

## Verifying Installation

You can verify that pstatstools is correctly installed by running:

```python
import pstatstools
print(pstatstools.__version__)  # Should print the current version

# Try creating a sample
from pstatstools import sample
import numpy as np
test_sample = sample(np.random.normal(0, 1, 100))
print(test_sample.mean())  # Should print a value close to 0
```

## Dependencies

The package requires:

* Python >= 3.6
* NumPy >= 1.19.0
* SciPy >= 1.7.0
* Matplotlib >= 3.4.0 
* Statsmodels >= 0.13.0
* Pandas >= 1.3.0

## Troubleshooting

If you encounter any issues during installation:

1. Make sure your Python version is 3.6 or higher
2. For conda installation issues, try updating conda first: `conda update -n base conda`
3. For pip installation issues, ensure you have the latest pip: `pip install --upgrade pip`
4. If you have dependency conflicts, consider using a virtual environment

## Development Installation

For contributors, install in development mode:

```bash
# Using pip
pip install -e ".[dev]"

# Using conda
conda env create -f environments/environment-dev.yml
conda activate pstatstools-dev

## Testing

[Instructions for running tests]

## Style Guidelines

### Code Style

[Information about code formatting, linting tools, etc.]

### Commit Messages

- Use the present tense ("Add feature" not "Added feature")
- Use the imperative mood ("Move cursor to..." not "Moves cursor to...")
- Limit the first line to 72 characters or less
- Reference issues and pull requests after the first line

## License

By contributing to this project, you agree that your contributions will be licensed under the project's [LICENSE](LICENSE) file.

## Questions?

If you have any questions or need help with the contribution process, feel free to create an issue with your question.

Thank you for contributing!