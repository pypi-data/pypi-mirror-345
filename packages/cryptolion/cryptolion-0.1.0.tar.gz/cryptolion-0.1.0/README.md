[![CI](https://github.com/phoenixsenses/cryptolion/actions/workflows/ci.yml/badge.svg)](https://github.com/phoenixsenses/cryptolion/actions/workflows/ci.yml)
[![PyPI version](https://img.shields.io/pypi/v/cryptolion-backtester.svg)](https://pypi.org/project/cryptolion-backtester/)

# CryptoLion Backtester

A lightweight command‑line tool for backtesting cryptocurrency strategies, optimizing parameters, walk‑forward validation, and portfolio aggregation.

## Installation

```bash
pip install -r requirements.txt
pip install cryptolion-backtester
```

## Usage

Show help and available commands:

```bash
backtester --help
```

Run a backtest:

```bash
backtester backtest \
  --file data/ETH_USDT_4h.csv \
  --params '{"fast":5,"slow":21,"fee":0.001,"sig":9}' \
  --save-plots
```

Optimize strategy parameters:

```bash
backtester optimize \
  --file data/ETH_USDT_4h.csv \
  --param-grid '{"fast":[5,8],"slow":[21,34]}' \
  --processes 4 \
  --output grid_results.csv
```

Aggregate multiple symbols into an equal‑weight monthly‑rebalanced portfolio:

```bash
backtester portfolio \
  --folder data/ \
  --weight equal \
  --rebalance M \
  --fee 0.001 \
  --slippage 0.0005 \
  --out-file portfolio_equity.csv
```

## Development

Install dev dependencies and run formatting, linting, and tests:

```bash
pip install -r requirements.txt black flake8 pytest
black backtester.py tests
flake8 backtester.py tests
pytest -q
```

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

## Next Steps

1. **Verify CI Status**: Check the GitHub **Actions** tab to ensure all tests, linting, and formatting checks pass on `main` and PRs.
2. **Release a new version to PyPI**

   > If you get a 403 Forbidden during upload it likely means the project name `backtester` is already taken on PyPI. We've renamed the package to `cryptolion-backtester`—make sure your metadata matches.

   **Update package metadata**

   1. Open `pyproject.toml` and set:
      ```toml
      [project]
      name = "cryptolion-backtester"
      version = "0.1.1"
      # ...
      ```
   2. Commit and tag:
      ```bash
      git add pyproject.toml
      git commit -m "chore: rename package, bump to v0.1.1"
      git tag v0.1.1
      git push origin main --tags
      ```

   **Clean old build artifacts**

   ```bash
   rm -rf dist build cryptolion_backtester-*.egg-info
   ```

   **Build & upload**

   ```bash
   pip install --upgrade build twine
   python3 -m build
   twine upload dist/*
   ```

   _Ensure your `~/.pypirc` or `TWINE_USERNAME`/`TWINE_PASSWORD` points to your valid API token for `cryptolion-backtester`._

### Using this token

To use this API token:

- Set your username to `__token__`
- Set your password to the token value, including the `pypi-` prefix

For example, in `~/.pypirc`:

```ini
[pypi]
username = __token__
password =

For further instructions, see the [PyPI help page](https://pypi.org/help/#invalid-auth).

```

![Coverage Status](https://coveralls.io/repos/github/<your-org>/<your-repo>/badge.svg?branch=main)](https://coveralls.io/github/<your-org>/<your-repo>?branch=main)
