from pathlib import Path
import pandas as pd
from typing import Optional

def load_dataframe(path_or_name: str, base_dir: Optional[str] = None):
    if path_or_name is None:
        return None
    p = Path(path_or_name).expanduser()
    if not p.is_absolute() and base_dir:
        p = Path(base_dir) / p
    p = p.resolve()
    if not p.exists():
        raise FileNotFoundError(f"Data not found: {path_or_name}")
    if p.suffix.lower() == ".csv":
        return pd.read_csv(p)
    if p.suffix.lower() in (".parquet",".pq"):
        return pd.read_parquet(p)
    if p.suffix.lower() == ".json":
        return pd.read_json(p)
    # Default to CSV
    return pd.read_csv(p)
