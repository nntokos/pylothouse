# pylothouse (meta-package)

Meta-package that installs the full pylothouse suite of subpackages:
- pylothouse-cv
- pylothouse-dash
- pylothouse-math
- pylothouse-utils
- pylothouse-xr

Requirements
- Python >= 3.10

Install from PyPI
```bash
pip install pylothouse
```

Install from this monorepo (local sources)
- From the repository root:
```bash
pip install "./packages/pylothouse[local]"
```
- Editable dev install:
```bash
pip install -e "./packages/pylothouse[local]"
```
This installs all subpackages from their local folders via the `local` extra.

Install individual subpackages
```bash
pip install pylothouse-cv
pip install pylothouse-dash
pip install pylothouse-math
pip install pylothouse-utils
pip install pylothouse-xr
```

Notes
- The meta-package is thin and only provides dependency aggregation.
- Subpackages live under `packages/*` and use a `src/` layout under the common `pylothouse` namespace.

