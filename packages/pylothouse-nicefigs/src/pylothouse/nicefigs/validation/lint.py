def lint(spec):
    warnings = []
    # naive checks
    if spec.font.size < 6:
        warnings.append("Font size is very small; consider >= 6pt for print.")
    return warnings
