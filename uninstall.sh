#!/usr/bin/env bash
set -euo pipefail

# pylothouse full uninstall script
# - Uninstalls the meta-package and all subpackages from the active Python env
# - Cleans local build artifacts (build/, dist/, *.egg-info, __pycache__, *.pyc)
# - Optional: remove local .venv (with --remove-venv)
# - Supports dry runs with --dry-run

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$SCRIPT_DIR"

YES=false
DRY_RUN=false
REMOVE_VENV=false

usage() {
  cat <<USAGE
Usage: $(basename "$0") [options]

Options:
  -y, --yes           Do not prompt for confirmation
  -n, --dry-run       Show what would be done, without making changes
      --remove-venv   Also remove a .venv in the repo root if present
  -h, --help          Show this help

Targets:
  Packages to uninstall (if installed):
    - pylothouse (meta)
    - pylothouse-core
    - pylothouse-cv
    - pylothouse-dash
    - pylothouse-math
    - pylothouse-utils
    - pylothouse-xr
    - pylothouse-nicefigs

Cleans (within repo only): build/, dist/, *.egg-info, __pycache__, *.pyc
USAGE
}

confirm() {
  if $YES; then return 0; fi
  read -r -p "$1 [y/N]: " ans
  [[ "${ans:-}" =~ ^[Yy]$ ]]
}

log() { echo "[uninstall] $*"; }
run() {
  if $DRY_RUN; then
    echo "+ $*";
  else
    eval "$@";
  fi
}

# Choose pip bound to current Python
PYTHON=${PYTHON:-}
if [[ -z "${PYTHON}" ]]; then
  if command -v python3 >/dev/null 2>&1; then
    PYTHON=$(command -v python3)
  elif command -v python >/dev/null 2>&1; then
    PYTHON=$(command -v python)
  else
    echo "Python not found in PATH" >&2; exit 1
  fi
fi
PIP_CMD="\"$PYTHON\" -m pip"

parse_args() {
  while [[ $# -gt 0 ]]; do
    case "$1" in
      -y|--yes) YES=true; shift ;;
      -n|--dry-run) DRY_RUN=true; shift ;;
      --remove-venv) REMOVE_VENV=true; shift ;;
      -h|--help) usage; exit 0 ;;
      *) echo "Unknown option: $1" >&2; usage; exit 1 ;;
    esac
  done
}

uninstall_pkg() {
  local name="$1"
  if $DRY_RUN; then
    echo "+ $PIP_CMD show $name >/dev/null 2>&1 && $PIP_CMD uninstall -y $name"; return 0
  fi
  if $PYTHON -m pip show "$name" >/dev/null 2>&1; then
    log "Uninstalling $name"
    $PYTHON -m pip uninstall -y "$name" || true
  else
    log "$name not installed; skipping"
  fi
}

clean_artifacts() {
  log "Cleaning build artifacts under $REPO_ROOT"
  run "find \"$REPO_ROOT\" -type d -name build -prune -exec rm -rf {} +"
  run "find \"$REPO_ROOT\" -type d -name dist -prune -exec rm -rf {} +"
  run "find \"$REPO_ROOT\" -type d -name __pycache__ -prune -exec rm -rf {} +"
  run "find \"$REPO_ROOT\" -type d -name '*.egg-info' -prune -exec rm -rf {} +"
  run "find \"$REPO_ROOT\" -type f -name '*.pyc' -delete"
}

remove_venv() {
  local venv_path="$REPO_ROOT/.venv"
  if [[ -d "$venv_path" ]]; then
    if confirm "Remove virtual environment at $venv_path?"; then
      run "rm -rf \"$venv_path\""
    else
      log "Skipping .venv removal"
    fi
  fi
}

main() {
  parse_args "$@"

  log "Using Python: $PYTHON"
  if ! $DRY_RUN && ! $YES; then
    confirm "Proceed to uninstall pylothouse and all subpackages from this Python environment?" || { echo "Aborted"; exit 1; }
  fi

  # Uninstall meta first (in case it pins subpackages), then subpackages to ensure all are removed
  uninstall_pkg "pylothouse"
  uninstall_pkg "pylothouse-core"
  uninstall_pkg "pylothouse-cv"
  uninstall_pkg "pylothouse-dash"
  uninstall_pkg "pylothouse-math"
  uninstall_pkg "pylothouse-utils"
  uninstall_pkg "pylothouse-xr"
  uninstall_pkg "pylothouse-nicefigs"

  clean_artifacts

  if $REMOVE_VENV; then
    remove_venv
  fi

  log "Done."
}

main "$@"
