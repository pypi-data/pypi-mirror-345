# Guide to Publishing Clivy on PyPI

This guide will walk you through the process of building and uploading your Clivy package to PyPI (Python Package Index).

## Prerequisites

1. Create an account on PyPI: https://pypi.org/account/register/
2. Install required tools:
   ```bash
   pip install build twine
   ```

## Building the Package

1. Navigate to the root directory of your package (where pyproject.toml is located):
   ```bash
   cd path/to/clivy
   ```

2. Build the package:
   ```bash
   python -m build
   ```
   This will create a `dist` directory containing both the source distribution (.tar.gz) and wheel (.whl) files.

## Uploading to PyPI

### Testing on TestPyPI (Recommended)

Before uploading to the main PyPI repository, it's a good practice to test your package on TestPyPI:

1. Create an account on TestPyPI: https://test.pypi.org/account/register/

2. Upload your package to TestPyPI:
   ```bash
   python -m twine upload --repository testpypi dist/*
   ```

3. Install your package from TestPyPI to test it:
   ```bash
   pip install --index-url https://test.pypi.org/simple/ clivy
   ```

### Uploading to PyPI

Once you've tested your package and everything works as expected, you can upload it to the main PyPI repository:

```bash
python -m twine upload dist/*
```

You'll be prompted for your PyPI username and password.

## Updating Your Package

When you want to release a new version:

1. Update the version number in `pyproject.toml`
2. Rebuild the package: `python -m build`
3. Upload the new version: `python -m twine upload dist/*`

## Additional Resources

- [Packaging Python Projects](https://packaging.python.org/tutorials/packaging-projects/)
- [PyPI Documentation](https://pypi.org/help/)
- [Python Packaging User Guide](https://packaging.python.org/)
