# User Guide

A walkthrough of every section of the EU Micronutrient Atlas dashboard.

---

## Navigation

The dashboard is a single scrollable page. Each section reveals as you scroll down. The background video can be paused at any time using the **⏸ Freeze Video** button in the top-right corner.

---

## Section 1 — Food Fingerprint

**What it does:** Shows the full micronutrient profile of a single food across all 7 EU countries.

### Heatmap (All Foods / Country View)

| Control | What it does |
|---|---|
| **View** | Switch between *Top Foods* (rows = foods, ranked by nutrient density) and *By Country* (rows = countries, averaged across a food category) |
| **Category** | Filter to a food category (e.g. "Fish and fish products") |
| **Nutrients** | Show all 16, vitamins only, or minerals only |
| **Scale** | See below |

**Scale options:**
- **Z-score** — how each food ranks relative to others in the same column. Positive = above average, negative = below. Good for spotting standout foods.
- **% of RDA** — each cell's colour shows what percentage of the EU daily recommended intake 100g of that food covers. Capped at 300%.
- **Actual Values** — cell colour is relative within each column (% of the column maximum); the actual mg/µg values are shown as text inside each cell.

### Single Food View

Select *Single Food* from the View toggle to compare one food across countries.

| Control | What it does |
|---|---|
| **Search Food** | Type to search any of the 2,500+ foods |
| **Countries** | Toggle which EU countries to include |
| **Nutrients** | Vitamins / Minerals / All |
| **Scale** | Z-score (country vs country for this food) or Actual Values |
| **Difference chart scale** | Linear or Log — log is useful when nutrient values span several orders of magnitude |

The **difference chart** below the heatmap shows each nutrient as a horizontal bar, with one dot per country, displayed as % of daily RDA per 100g.

---

## Section 2 — National Overview

**What it does:** Scoreboard showing which countries lead or lag for each nutrient across all foods.

- Left chart: country rankings by average micronutrient content
- Right chart: data coverage — which nutrient/country combinations have the most complete data

---

## Section 3 — Top Foods Rich in a Nutrient

**What it does:** Find the top N foods in a category with the highest content of a chosen nutrient.

| Control | What it does |
|---|---|
| **Nutrient** | Which micronutrient to rank by |
| **Top N** | How many foods to show (5, 10, 15, 20) |
| **Country** | Show values for a specific country or the EU average |

Click any bar to see that food's full nutrient radar in the drill-down panel below.

---

## Section 4 — 10 Key Insights

An auto-generated carousel of data-driven observations pulled directly from the dataset — nutrient champions, country gaps, and surprising findings. Arrows or swipe to navigate.

---

## Section 5 — How Much Would You Need To Eat?

**What it does:** Given a food and a nutrient, calculates how many grams you'd need to eat to hit your daily RDA — and shows how that varies by country.

| Control | What it does |
|---|---|
| **Food** | Search any food |
| **Nutrient** | Which micronutrient to calculate for |
| **Age group** | 18–64 or 65+ (adjusts RDA) |
| **Sex** | Male / Female (adjusts RDA) |
| **Weight / Height** | Used to scale certain RDA values |

The chart shows one bar per country. Shorter bar = that country's version of the food is more nutrient-dense (you need to eat less to hit the RDA).

---

## Section 6 — Drinks & Alcohol

**What it does:** Explore the micronutrient content of alcoholic drinks.

### Compare Drinks radar
Select up to ~6 drinks from the dropdown. Each drink gets a coloured polygon on the radar chart. The scale is % of the maximum value across all displayed drinks for each nutrient.

### Nutrient Champion radar
Fixed comparison: Sheep Liver (the most micronutrient-dense food in the dataset) vs the top 3 most nutrient-dense alcoholic drinks (ranked by composite z-score). Shows that some alcoholic drinks — particularly egg liqueur and fortified wines — contain non-trivial micronutrient levels relative to their alcohol content.

---

## About & Methodology

Click **▲ About & Methodology** at the very bottom of the page to expand six information cards covering the data source, methodology, RDA definitions, limitations, and links to the original EFSA data portal.

---

## Tips

- **Hard refresh** (`Ctrl+Shift+R`) if the page looks odd after an update — Dash caches CSS aggressively.
- All values are **per 100g** of food as consumed.
- **Zero values** in the source data are treated as missing throughout (shown as blank/grey in heatmaps).
- The EU average column is the mean across whichever countries have non-zero data for that food.
