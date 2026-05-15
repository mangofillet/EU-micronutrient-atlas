# Data Guide

## Main Dataset

**File:** `data/EU/eu_nutrients_unified.csv`

This is the only file the app reads at runtime. It contains one row per food with columns for each nutrient × country combination.

### Column naming convention

```
{Nutrient}_{Country}     — e.g. Calcium_DE, Iron_FR
{Nutrient}_EU_avg        — mean across all countries with non-zero data
food_name                — standardised English name
food_category            — FoodEx2 level-1 category
```

### Countries

| Code | Country |
|---|---|
| `DE` | Germany |
| `FR` | France |
| `IT` | Italy |
| `ES` | Spain |
| `NL` | Netherlands |
| `BE` | Belgium |
| `UK` | United Kingdom |

### Nutrients & Units

| Nutrient | Unit |
|---|---|
| Calcium | mg/100g |
| Copper | mg/100g |
| Iron | mg/100g |
| Magnesium | mg/100g |
| Phosphorus | mg/100g |
| Potassium | mg/100g |
| Zinc | mg/100g |
| Alpha Tocopherol | mg/100g |
| Niacin Equivalent | mg/100g |
| Riboflavin | mg/100g |
| Thiamine | mg/100g |
| Vitamin B6 | mg/100g |
| Vitamin E | mg/100g |
| Selenium | µg/100g |
| Vitamin B12 | µg/100g |
| Vitamin K | µg/100g |

---

## Source Data

The individual per-nutrient source files are preserved in `data/EU/` (e.g. `Calcium.csv`, `Iron.csv`). These were merged to produce `eu_nutrients_unified.csv`. If you receive updated EFSA data, update the individual CSVs and re-run the merge to regenerate the unified file.

**Source:** EFSA Total Diet Study — [https://www.efsa.europa.eu/en/topics/topic/total-diet-studies](https://www.efsa.europa.eu/en/topics/topic/total-diet-studies)

**Classification:** FoodEx2 system — [https://www.efsa.europa.eu/en/data/data-standardisation](https://www.efsa.europa.eu/en/data/data-standardisation)

---

## EU RDA Values

Defined in `app.py` as the `EU_RDA` dictionary (lines 27–33). These are EFSA Population Reference Intakes for adults.

A second dictionary `EU_RDA_DEMO` (lines 34–70) provides age- and sex-specific values used by the RDA calculator section.

To update RDA values, edit these dictionaries directly in `app.py`.

---

## Adding a New Food Category or Food

The `food_category` and `food_name` columns in `eu_nutrients_unified.csv` drive the Category dropdown and food search respectively. Adding rows to the CSV is sufficient — no code changes required, as categories and food names are read dynamically at startup.

---

## Data Limitations

- Zero values in the source data are treated as missing (not truly zero concentration).
- The EU average is the mean of non-zero country values only; foods measured in fewer countries will have a less representative average.
- Values represent the food **as consumed** (prepared/cooked where applicable), not raw unless stated.
- Data reflects EFSA Total Diet Study sampling and may not cover all foods available in each country.
