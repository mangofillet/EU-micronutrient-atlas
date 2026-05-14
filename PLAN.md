# Food Comparison by Country — Project Plan

## Concept

A cinematic dark-mode Dash dashboard comparing nutritional values of foods across national databases and country-level dietary patterns. Two core views:

1. **Food Explorer** — search any food, compare how Sweden, USA, UK, Norway, China measure its nutrients side by side
2. **Country Dietary Patterns** — choropleth map + rankings of per-capita macro intake across 170+ countries (FAO Food Balance Sheets)

---

## Data Sources

| Country | Source | Format | Foods | Download URL |
|---|---|---|---|---|
| Sweden | Livsmedelsverket | CSV | 2,576 | Local (from Food Choices Dash project) |
| USA | USDA SR Legacy | Relational CSV ZIP | ~8,000 | https://fdc.nal.usda.gov/fdc-datasets/FoodData_Central_sr_legacy_food_csv_2021-10-28.zip |
| UK | CoFID (FSA) | Excel (.xlsx) | ~2,000 | https://assets.publishing.service.gov.uk/media/60538b91e90e07527df82ae4/McCance_Widdowsons_Composition_of_Foods_Integrated_Dataset_2021..xlsx |
| Norway | Matvaretabellen | JSON REST API | 2,121 | https://www.matvaretabellen.no/api/en/foods.json |
| China | CFCD (community JSON) | JSON | ~1,500 | https://github.com/Sanotsu/china-food-composition-data |
| Global | FAOSTAT Food Balance Sheets | Bulk CSV | 178 countries | https://fenixservices.fao.org/faostat/static/bulkdownloads/FoodBalanceSheets_E_All_Data.zip |

### Data Provenance Notes

| Source | How gathered | Licence |
|---|---|---|
| Livsmedelsverket | Manual CSV export from Swedish National Food Agency | Open government (CC0-equivalent) |
| USDA SR Legacy | Bulk ZIP from fdc.nal.usda.gov. Relational: food + food_nutrient + nutrient tables joined on import | USDA public domain |
| UK CoFID | Direct .xlsx from gov.uk (FSA). McCance & Widdowson 2021 | UK Open Government Licence |
| Matvaretabellen | Paginated REST API. Cached locally; updates annually in autumn | CC BY 4.0 |
| China CFCD | Community-digitised JSON from 6th Edition Standard Version (中国食物成分表). Fewer micronutrients than others | Community (CC BY-NC) |
| FAOSTAT | Bulk CSV download. 178 countries, 2010–2022, per-capita supply in kcal/protein/fat/day by food commodity group | FAO open data |

---

## Database Schema (`data/global_nutrition.db`)

```sql
CREATE TABLE foods (
    id          INTEGER PRIMARY KEY,
    country     TEXT NOT NULL,
    source      TEXT NOT NULL,
    food_name   TEXT NOT NULL,
    food_name_local TEXT,
    food_group  TEXT,
    energy_kcal REAL, protein_g REAL, fat_g REAL,
    carbs_g REAL, fiber_g REAL, sugar_g REAL,
    saturated_fat_g REAL, cholesterol_mg REAL, water_g REAL,
    sodium_mg REAL, calcium_mg REAL, iron_mg REAL,
    potassium_mg REAL, magnesium_mg REAL, zinc_mg REAL,
    phosphorus_mg REAL, selenium_ug REAL,
    vitamin_c_mg REAL, vitamin_d_ug REAL, vitamin_a_ug REAL,
    vitamin_b12_ug REAL, folate_ug REAL, vitamin_e_mg REAL,
    vitamin_b6_mg REAL, thiamin_mg REAL, riboflavin_mg REAL,
    niacin_mg REAL, omega3_g REAL, omega6_g REAL
);

CREATE TABLE country_diet (
    id INTEGER PRIMARY KEY,
    country TEXT NOT NULL, year INTEGER NOT NULL, food_group TEXT NOT NULL,
    kcal_per_capita_day REAL, protein_g_per_capita_day REAL,
    fat_g_per_capita_day REAL, kg_per_capita_year REAL
);
```

---

## Import Scripts (`scripts/`)

- `import_sweden.py` — map Livsmedelsverket CSV columns to schema
- `import_usda.py` — download + join SR Legacy relational CSV
- `import_norway.py` — paginate Matvaretabellen JSON API
- `import_uk.py` — parse CoFID Excel with openpyxl
- `import_china.py` — parse community JSON
- `import_faostat.py` — parse Food Balance Sheets, aggregate per country/year
- `build_db.py` — master runner

---

## Landing Page Design (Cinematic Dark Mode)

**Aesthetic:** "Spotify Wrapped for global nutrition" — dark, glassmorphism, animated gradients.

**Design tokens:**
```
--bg: #050810
--surface: rgba(255,255,255,0.04)
--accent-1: #6EE7B7  (emerald)
--accent-2: #818CF8  (indigo)
--accent-3: #F472B6  (pink)
--text-1: #F8FAFC
--font: Inter
```

### Sections
1. **Hero** — fullscreen animated gradient bg, large title "How does food nutrition differ across the world?", animated choropleth, floating stat chips
2. **Food Explorer** — glassmorphism search card, country filter pills, radar chart + grouped bars + micronutrient heatmap
3. **Global Nutrition Map** — full-width choropleth, nutrient selector, year slider, top/bottom 10 bars
4. **Featured Insights** — 3 editorial glassmorphism cards auto-populated from real data
5. **Animated Stats** — count-up number cards (16,197 foods / 5 databases / 170+ countries / 30 nutrients)
6. **About the Data** — expandable provenance accordion
7. **Footer**

---

## Implementation Order

1. Data layer — write + run all import scripts, verify row counts
2. Landing page shell + CSS design system
3. Food Explorer section
4. Country Patterns section
5. Editorial cards + stats + footer
