
     EU  MICRONUTRIENT  ATLAS       


> *You can't compare apples and oranges — but can you even compare apples and apples?*
>
> Turns out, not all apples are created equal. Depending on where it was grown,
> how it was measured, and which country's data you trust, the same apple can look
> like a nutritional hero or a nutritional zero. Now scale that uncertainty across
> 2,500 foods, 16 micronutrients, and 7 European countries — and you start to
> wonder what you actually know about what you eat.

> **The EU Micronutrient Atlas** is an attempt to find out. It maps EFSA Total Diet study data into an interactive, cinematic dashboard so you can explore, compare,
> and question the food on your plate — one nutrient at a time.

---

## What You Can Explore

- Which foods are the richest natural sources of any given micronutrient?
- How much does the same food vary in nutrient content across EU countries?
- How many grams would you actually need to eat to hit your daily recommended intake?
- Which alcoholic drinks are — against all odds — surprisingly nutrient-dense?

---

## Data

| Source | Description |
|---|---|
| **EFSA Total Diet Study** | Per-food micronutrient concentrations averaged across 7 EU countries (DE, FR, IT, ES, NL, BE, UK) | 
https://www.efsa.europa.eu/en/microstrategy/food-composition-data
| **EU RDA** | EFSA Dietary Reference Values used for % of RDA calculations |


**File:** `data/EU/eu_nutrients_unified.csv`

**Coverage:** ~2,500 foods × 16 micronutrients × 7 countries + EU average

**Nutrients tracked:**
Calcium, Copper, Iron, Magnesium, Phosphorus, Potassium, Selenium, Zinc,
Alpha Tocopherol, Niacin Equivalent, Riboflavin, Thiamine, Vitamin B6, Vitamin B12, Vitamin E, Vitamin K

**Units:** mg/100g or µg/100g depending on nutrient

---

## Features

### Nutrient Heatmap
- Browse top nutrient-dense foods by category (Food view) or compare countries (Country view)
- Three colour scales: **Z-score** (relative ranking), **% of RDA** (daily requirement coverage per 100g), **Actual Values** (raw mg/µg with colour by % of max)
- Filter by nutrient group (Vitamins / Minerals / All)

### Food Fingerprint — Single Food
- Select any food and compare its micronutrient profile across all 7 EU countries
- Difference chart shows country spread as % of daily RDA per 100g (log scale by default)
- Z-score scale highlights which countries are relatively high or low

### Top Foods — Nutrient Bar Chart
- Rank the top N foods in a category by a chosen nutrient
- Radar chart overlay for multi-nutrient comparison

### Drinks & Alcohol Radar
- Nutrient radar comparing selected alcoholic drinks
- Separate panel: Sheep Liver vs the top 3 most nutrient-dense alcoholic drinks (cross-item normalised)

### RDA Calculator
- Choose a food and nutrient; see how many grams you'd need to hit your daily RDA
- Adjusts for age group, sex, weight, and height

---

## Installation

```bash
# Clone the repo
git clone <repo-url>
cd "Food comparison by country"

# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

---

## Running

```bash
python app.py
```

Opens automatically at [http://127.0.0.1:8050](http://127.0.0.1:8050).

---

## Project Structure

```
.
├── app.py                  # Main Dash application
├── requirements.txt        # Python dependencies
├── assets/
│   ├── style.css           # Design system + component styles
│   ├── inter.css           # Inter font import
│   ├── video-bg.css        # Background video styles
│   ├── video-bg.js         # Video background logic
│   ├── carousel.js         # Carousel animations
│   └── scroll-anim.js      # Scroll reveal animations
├── data/
│   └── EU/
│       ├── eu_nutrients_unified.csv   # Main dataset (app reads this)
│       └── *.csv                      # Per-nutrient source files
├── videos/                 # Background video files (MP4, 4K)
└── _old_project/           # Archived files from earlier project scope
```

---

## Dependencies

| Package | Purpose |
|---|---|
| `dash` | Web app framework |
| `plotly` | Interactive charts |
| `pandas` | Data processing |
| `numpy` | Numerical operations |
| `requests` | HTTP (not used in current build) |
| `openpyxl` | Excel parsing (not used in current build) |

Requires Python 3.10+. Tested with Dash 4.1.0.

---

## Notes

- The app pre-computes several figures at startup to keep callbacks fast.
- All values are per 100g of food as consumed.
- EU average is the mean across available country measurements.
- Zero values in the source data are treated as missing (NaN) throughout.
- The `_old_project/` folder contains archived data and scripts from an earlier version of this project that planned to include USDA, UK CoFID, Swedish, Norwegian, and FAOSTAT global data. Those datasets are not used by the current app.
