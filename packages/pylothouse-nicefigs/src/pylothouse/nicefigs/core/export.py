from pathlib import Path
from typing import Optional

def save(fig, export_spec, base_dir: Optional[str] = None):
    base = Path(base_dir) if base_dir else None
    base_path = Path(export_spec.path)
    if base is not None and not base_path.is_absolute():
        base_path = base / base_path
    for fmt in export_spec.formats:
        path = base_path if str(base_path).endswith(f".{fmt}") else base_path.with_suffix(f".{fmt}")
        fig.savefig(
            path,
            dpi=export_spec.dpi,
            bbox_inches="tight" if export_spec.tight_layout else None,
            metadata=export_spec.metadata,
        )
