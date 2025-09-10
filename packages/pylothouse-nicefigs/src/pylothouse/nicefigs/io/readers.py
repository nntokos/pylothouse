from pathlib import Path
import pandas as pd
from typing import Optional, Union, Callable, Any, Dict

def _resolve_path(p: Union[str, Path], base_dir: Optional[str]) -> Path:
    p = Path(p).expanduser()
    if not p.is_absolute() and base_dir:
        p = Path(base_dir) / p
    return p.resolve()


def load_dataframe(obj, base_dir: Optional[str] = None):
    """Return a pandas.DataFrame from various inputs.
    Supported:
    - pandas.DataFrame: returned as-is
    - callable: called with no args; result is re-processed recursively
    - dict: minimal support {path, reader, kwargs} where reader in {csv, parquet, json}
    - str/Path: file path, inferred by extension (csv/parquet/json; default csv)
    """
    if obj is None:
        return None

    # DataFrame
    if isinstance(obj, pd.DataFrame):
        return obj

    # Callable -> evaluate then recurse
    if callable(obj):
        return load_dataframe(obj(), base_dir=base_dir)

    # Dict spec
    if isinstance(obj, dict):
        # direct df in dict
        df = obj.get("dataframe") or obj.get("df")
        if isinstance(df, pd.DataFrame):
            return df
        # loader callable in dict
        loader = obj.get("loader") or obj.get("call") or obj.get("func")
        if callable(loader):
            return load_dataframe(loader(), base_dir=base_dir)
        # path with optional reader and kwargs
        path = obj.get("path") or obj.get("file") or obj.get("csv") or obj.get("parquet") or obj.get("json")
        if path is None:
            raise ValueError("Unsupported dict spec for load_dataframe; expected keys like path/file or loader/func")
        reader = obj.get("reader")
        kwargs: Dict[str, Any] = obj.get("kwargs", {})
        p = _resolve_path(path, base_dir)
        if not p.exists():
            raise FileNotFoundError(f"Data not found: {path}")
        if reader == "csv" or p.suffix.lower() == ".csv":
            return pd.read_csv(p, **kwargs)
        if reader == "parquet" or p.suffix.lower() in (".parquet", ".pq"):
            return pd.read_parquet(p, **kwargs)
        if reader == "json" or p.suffix.lower() == ".json":
            return pd.read_json(p, **kwargs)
        return pd.read_csv(p, **kwargs)

    # Path-like
    if isinstance(obj, (str, Path)):
        p = _resolve_path(obj, base_dir)
        if not p.exists():
            raise FileNotFoundError(f"Data not found: {obj}")
        if p.suffix.lower() == ".csv":
            return pd.read_csv(p)
        if p.suffix.lower() in (".parquet", ".pq"):
            return pd.read_parquet(p)
        if p.suffix.lower() == ".json":
            return pd.read_json(p)
        return pd.read_csv(p)

    raise TypeError(f"Unsupported data spec type: {type(obj)!r}")
