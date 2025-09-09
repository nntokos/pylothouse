# pylothouse
A Python package suite with modular tools for math, computer vision, dashboards, utilities, and more. Install the whole suite or just the parts you need.

## Overview
`pylothouse` is a meta-package that installs several related packages under the `pylothouse` namespace:
- Core helpers (config, errors, logging, registry)
- Math utilities
- Computer vision utilities
- Dash/Plotly helpers for building dashboards
- General utilities
- Xarray helpers
- Figure utilities ("nicefigs")

Each component is available as its own pip package and can be used independently.

## Installation
- Install the full suite (meta-package):
  ```bash
  pip install pylothouse
  ```
- Install a specific component only (replace <component>):
  ```bash
  pip install pylothouse-<component>
  ```
  Components include: core, math, cv, dash, utils, xr, nicefigs

Python 3.8+ is supported (some tooling is configured for Python 3.10).

## Quick start
Once installed, import what you need from the `pylothouse` namespace:
```python
from pylothouse.core import config
from pylothouse.math import *  # math helpers
from pylothouse.cv import *    # computer vision utilities
from pylothouse.dash import *  # dash/plotly helpers
```
Refer to each package’s README for APIs and examples.

## Packages
- Core: [pylothouse-core](packages/pylothouse-core/README.md) – Config, errors, logging, registry.
- Math: [pylothouse-math](packages/pylothouse-math/README.md) – Math utilities.
- CV: [pylothouse-cv](packages/pylothouse-cv/README.md) – Computer vision utilities.
- Dash: [pylothouse-dash](packages/pylothouse-dash/README.md) – Dash/Plotly dashboard helpers.
- Utils: [pylothouse-utils](packages/pylothouse-utils/README.md) – General utilities.
- XR: [pylothouse-xr](packages/pylothouse-xr/README.md) – Xarray helpers.
- Nice Figs: [pylothouse-nicefigs](packages/pylothouse-nicefigs/README.md) – Figure/plot helpers.

## Local development
Work with all packages locally via the meta-package’s local extra:
```bash
# create and activate a virtual env (example: venv)
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# editable install of the meta-package + local component links
pip install -e packages/pylothouse[local]
```
This installs the `pylothouse` meta-package in editable mode and links the component packages from the repository for local development.

Optional dev tools:
```bash
pip install ruff mypy pytest
# Lint & type check
ruff check .
mypy packages/*/src
# Run tests (if present)
pytest packages
```

## Contributing
- Open an issue or pull request with a clear description.
- Keep changes focused and add/update minimal tests when changing public behavior.
- Follow style/type guidelines (ruff, mypy) where configured.

## License
MIT. See the LICENSE file if present in individual packages.

## Contact
Maintainer: Nikolaos Ntokos (https://github.com/nnmav)
