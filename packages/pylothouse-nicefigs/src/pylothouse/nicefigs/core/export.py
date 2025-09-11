"""Export utilities for saving figures.

This module centralizes the logic for writing a Matplotlib figure using the
validated ExportSpec. It resolves relative paths against the YAML directory
(base_dir) and supports multiple output formats per render (e.g., png + pdf).
"""

from pathlib import Path
from typing import Optional


def save(fig, export_spec, base_dir: Optional[str] = None):
    """Save a Matplotlib figure according to an ExportSpec.

    Parameters
    - fig: Matplotlib Figure instance to save.
    - export_spec: ExportSpec with path, dpi, formats, tight_layout, metadata.
    - base_dir: Optional base directory used to resolve relative export paths
      (typically the YAML file directory, provided by the loader).

    Behavior
    - If export_spec.path lacks an extension matching the target format, the
      appropriate suffix is applied for each format.
    - When tight_layout is True, bbox_inches="tight" is used for export to
      reduce extraneous whitespace while preserving labels.
    """
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
