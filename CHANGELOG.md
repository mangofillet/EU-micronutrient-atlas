# Changelog

All notable changes to the EU Micronutrient Atlas dashboard.

---

## [Unreleased] — 2026-05

### Data & Scales

- **% of RDA scale**: replaced the redundant "% of max" heatmap scale with "% of RDA per 100g" — each cell's colour now represents the share of the EU daily recommended intake covered by a 100g serving (capped at 300% to prevent outliers collapsing the scale). Applied to all three heatmap views (food, country, single food).
- **Difference chart log scale**: country comparison dumbbell chart now defaults to log scale so small-value nutrients remain legible alongside large ones.
- **"Actual Values" label**: renamed heatmap scale option from "Values" to "Actual Values" for clarity.

### Charts & Visualisation

- **Nutrient radar — cross-item normalisation**: `make_drinks_wine_radar` rewritten to compute `axis_max` across all displayed items per nutrient rather than per-item, so the radar honestly represents relative quantities between foods.
- **Sheep Liver reference**: radar shows Sheep Liver vs the top 3 most nutrient-dense alcoholic drinks (dynamically ranked by composite z-score at startup). Previously hardcoded; now data-driven.
- **Top-3 alcohol ranking**: Egg Liqueur (#1), Port (#2), Ice Wine (#3) identified as most micronutrient-dense alcoholic drinks in the dataset.
- **Gaps chart**: food name now written inside bars (`textposition="inside"`, `insidetextanchor="middle"`); Y-axis shows nutrient name only (food name was redundant on the axis).

### UI / Controls

- **Food Fingerprint default countries**: Single Food view now pre-selects all 7 EU countries on load.
- **Country checklists**: changed to `nutrient-pills` class — same pill-button style as the View / Nutrients / Scale toggles.
- **Searchable dropdowns**: all non-search dropdowns (Category, Nutrient, Top N, Country, Age Group, Drink, Compare Drinks) set to `searchable=False`. Food search bars (`hm-food-search`, `rda-food`) remain `searchable=True`.
- **Video freeze button**: fixed-position top-right button toggles background video play/pause via a clientside callback.
- **Info / About section**: replaced old sticky footer with a collapsible bottom banner. Click "▲ About & Methodology" to expand six info cards; banner is non-sticky and sits at page bottom.

### CSS / Styling (Dash 4.1.0 migration)

- **Dropdown CSS class name fix**: Dash 4.1.0 completely rewrote the Dropdown component; old react-select v1 class names (`.Select-value-label`, `.Select-control`, `.Select--single`, etc.) no longer exist. All previous CSS targeting these was silently doing nothing.
- **New class names applied**: `.dash-dropdown`, `.dash-dropdown-value`, `.dash-dropdown-value-item`, `.dash-dropdown-placeholder`, `.dash-dropdown-search`, `.dash-dropdown-content`, `.dash-dropdown-option`, `.dash-dropdown-trigger-icon`.
- **DOM structure clarified**: in Dash 4.1.0 the user's `className` prop is merged onto the `<button class="dash-dropdown {className}">` element (not an outer wrapper). The dropdown content panel is a sibling of that button inside `.dash-dropdown-wrapper`. All selectors updated accordingly (`button.dash-dropdown.hm-dropdown`, `.dash-dropdown-wrapper:has(button.hm-dropdown) .dash-dropdown-content`).
- **Dropdown appearance**: all dropdowns (including food search bars) now use white background with black text for maximum readability.
- **Food search arrow hidden**: `.dash-dropdown-trigger-icon { display: none }` removes the dropdown arrow from search-style inputs.
- **Dead CSS removed**: eliminated all `.Select-*` rules that were targeting non-existent class names in Dash 4.1.0.

### Project Housekeeping

- **Quarantine folder**: files from the abandoned global-comparison project scope (USDA, UK CoFID, Swedish, Norwegian, FAOSTAT data + import scripts + planning docs) moved to `_old_project/` rather than deleted.
- **Lock files removed**: LibreOffice `.~lock.*` temp files deleted from repo.
- **README added**: comprehensive setup and feature documentation.
- **CHANGELOG added**: this file.
