import argparse, sys
from .api import load_config, render, render_spec

def main():
    parser = argparse.ArgumentParser(prog="nicefigs", description="Render figures from YAML config")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_render = sub.add_parser("render", help="Render a figure from YAML")
    p_render.add_argument("config", help="Path to YAML config")
    p_render.add_argument("--out", help="Override export.path (relative paths resolved against current working directory)")
    p_render.add_argument("--override", action="append", default=[], help="Dot-path overrides (e.g., size.width=89)")

    args = parser.parse_args()

    if args.cmd == "render":
        spec = load_config(args.config)
        # Apply overrides (simple dot-path setter)
        for ov in args.override:
            path, val = ov.split("=", 1)
            _setdot(spec, path, val)
        if args.out:
            spec.export.path = args.out
        # If --out used, resolve relative to CWD; otherwise, relative to spec dir
        resolve_to = "cwd" if args.out else "spec"
        render_spec(spec, resolve_export_relative_to=resolve_to)

def _setdot(obj, path, value):
    # Cast numeric strings to float/int when possible
    def _cast(v):
        try:
            if "." in v:
                return float(v)
            return int(v)
        except Exception:
            if v.lower() in ("true","false"):
                return v.lower()=="true"
            return v
    parts = path.split(".")
    cur = obj
    for p in parts[:-1]:
        cur = getattr(cur, p)
    setattr(cur, parts[-1], _cast(value))
