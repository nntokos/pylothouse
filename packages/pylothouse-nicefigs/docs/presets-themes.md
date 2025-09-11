# Presets and themes

Presets provide convenient figure sizes and font tweaks; themes can flip palettes or future `rcParams` tweaks.

## Presets (`config/presets/journals.py`)

- `ieee_single_col`: `size` `{width: 89, height: 67, unit: mm}`, `font.size`: `8`
- `ieee_double_col`: `size` `{width: 183, height: 67, unit: mm}`, `font.size`: `8`
- `nature_single_col`: `size` `{width: 89, height: 89, unit: mm}`, `font.size`: `9`

## Usage

- In `YAML`: `preset: ieee_single_col`
- Preset values fill in missing fields; explicit user config wins

## Themes (`config/presets/themes.py`)

- `light`: `palette` `okabe_ito`
- `dark`: `palette` `okabe_ito` (placeholder)

## Usage

- In `YAML`: `theme: light`
- Theme settings are merged with user config, user values win
