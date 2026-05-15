"""EU Micronutrient Atlas — EFSA Food Composition Dashboard."""
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from dash import Dash, Input, Output, State, ALL, ctx, dcc, html
from flask import send_from_directory
from pathlib import Path

# ── Paths ──────────────────────────────────────────────────────────────────────
EU_CSV    = Path("data/EU/eu_nutrients_unified.csv")
VIDEO_DIR = Path("videos").resolve()

# ── Nutrient metadata ──────────────────────────────────────────────────────────
EU_VITAMINS = ["Alpha Tocopherol","Niacin Equivalent","Riboflavin","Thiamine",
               "Vitamin B12","Vitamin B6","Vitamin E","Vitamin K"]
EU_MINERALS = ["Calcium","Copper","Iron","Magnesium",
               "Phosphorus","Potassium","Selenium","Zinc"]
EU_ALL      = EU_VITAMINS + EU_MINERALS

EU_UNITS = {
    "Alpha Tocopherol":"mg","Niacin Equivalent":"mg","Riboflavin":"mg",
    "Thiamine":"mg","Vitamin B12":"µg","Vitamin B6":"mg",
    "Vitamin E":"mg","Vitamin K":"µg",
    "Calcium":"mg","Copper":"mg","Iron":"mg","Magnesium":"mg",
    "Phosphorus":"mg","Potassium":"mg","Selenium":"µg","Zinc":"mg",
}
EU_RDA = {
    "Alpha Tocopherol": 12, "Niacin Equivalent": 16, "Riboflavin": 1.4,
    "Thiamine": 1.1, "Vitamin B12": 2.5, "Vitamin B6": 1.4,
    "Vitamin E": 12, "Vitamin K": 75,
    "Calcium": 800, "Copper": 1.0, "Iron": 14, "Magnesium": 375,
    "Phosphorus": 700, "Potassium": 2000, "Selenium": 55, "Zinc": 10,
}
EU_RDA_DEMO = {
    ("18-64", "male"): {
        "Alpha Tocopherol": 13, "Niacin Equivalent": 16, "Riboflavin": 1.6,
        "Thiamine": 1.2, "Vitamin B12": 2.5, "Vitamin B6": 1.4,
        "Vitamin E": 13, "Vitamin K": 75,
        "Calcium": 1000, "Copper": 1.5, "Iron": 11, "Magnesium": 350,
        "Phosphorus": 700, "Potassium": 2000, "Selenium": 70, "Zinc": 11,
    },
    ("18-64", "female"): {
        "Alpha Tocopherol": 11, "Niacin Equivalent": 14, "Riboflavin": 1.4,
        "Thiamine": 1.1, "Vitamin B12": 2.5, "Vitamin B6": 1.4,
        "Vitamin E": 11, "Vitamin K": 75,
        "Calcium": 1000, "Copper": 1.5, "Iron": 16, "Magnesium": 300,
        "Phosphorus": 700, "Potassium": 2000, "Selenium": 60, "Zinc": 8,
    },
    ("65+", "male"): {
        "Alpha Tocopherol": 13, "Niacin Equivalent": 16, "Riboflavin": 1.6,
        "Thiamine": 1.2, "Vitamin B12": 4.0, "Vitamin B6": 1.7,
        "Vitamin E": 13, "Vitamin K": 75,
        "Calcium": 1200, "Copper": 1.5, "Iron": 11, "Magnesium": 350,
        "Phosphorus": 700, "Potassium": 2000, "Selenium": 70, "Zinc": 11,
    },
    ("65+", "female"): {
        "Alpha Tocopherol": 11, "Niacin Equivalent": 14, "Riboflavin": 1.4,
        "Thiamine": 1.1, "Vitamin B12": 4.0, "Vitamin B6": 1.7,
        "Vitamin E": 11, "Vitamin K": 75,
        "Calcium": 1200, "Copper": 1.5, "Iron": 11, "Magnesium": 300,
        "Phosphorus": 700, "Potassium": 2000, "Selenium": 60, "Zinc": 8,
    },
}
EU_SHORT = {
    "Alpha Tocopherol":"α-Tocoph.","Niacin Equivalent":"Niacin Eq.",
    "Riboflavin":"Riboflavin","Thiamine":"Thiamine",
    "Vitamin B12":"B12","Vitamin B6":"B6","Vitamin E":"Vit E","Vitamin K":"Vit K",
    "Calcium":"Calcium","Copper":"Copper","Iron":"Iron","Magnesium":"Mg",
    "Phosphorus":"Phosphorus","Potassium":"Potassium","Selenium":"Selenium","Zinc":"Zinc",
}
EU_SHORT_REV = {v: k for k, v in EU_SHORT.items()}

EU_COUNTRIES = ["Finland","France","Germany","Italy","Netherlands","Sweden","United Kingdom"]
EU_FLAGS = {
    "Finland":"🇫🇮","France":"🇫🇷","Germany":"🇩🇪",
    "Italy":"🇮🇹","Netherlands":"🇳🇱","Sweden":"🇸🇪","United Kingdom":"🇬🇧",
}
EU_COLORS = {
    "Finland":"#6EE7B7","France":"#818CF8","Germany":"#F472B6",
    "Italy":"#FCD34D","Netherlands":"#F97316","Sweden":"#38BDF8",
    "United Kingdom":"#A78BFA",
}
CAT_COLORS = {
    "Meat and meat products":"#F472B6",
    "Fish, seafood, amphibians, reptiles and invertebrates":"#38BDF8",
    "Milk and dairy products":"#FCD34D",
    "Vegetables and vegetable products":"#6EE7B7",
    "Fruit and fruit products":"#FB923C",
    "Grains and grain-based products":"#A78BFA",
    "Legumes, nuts, oilseeds and spices":"#34D399",
    "Eggs and egg products":"#FBBF24",
    "Composite dishes":"#818CF8",
    "Seasoning, sauces and condiments":"#94A3B8",
    "Coffee, cocoa, tea and infusions":"#D97706",
    "Animal and vegetable fats and oils":"#F97316",
    "Alcoholic beverages":"#C084FC",
}

BASE = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color="#F8FAFC", family="Inter, system-ui, sans-serif", size=14),
    margin=dict(l=40, r=40, t=52, b=40),
    dragmode=False,
)
CFG = dict(
    displayModeBar="hover",
    modeBarButtonsToRemove=["select2d","lasso2d","autoScale2d"],
    toImageButtonOptions={"format":"svg","filename":"eu_nutrient"},
)

# ── Data ───────────────────────────────────────────────────────────────────────
df = pd.read_csv(EU_CSV)
CATEGORIES = sorted(df["food_category"].dropna().unique().tolist())
FOOD_NAMES = sorted(df["food_name"].dropna().unique().tolist())
_avg_cols = [f"{n}_EU_avg" for n in EU_ALL]
for col in _avg_cols + [f"{n}_{c}" for n in EU_ALL for c in EU_COUNTRIES]:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")
df = df.copy()  # defragment after bulk column coercions
FOODS_COUNT = len(df)
DRINK_NAMES = sorted(df[df["food_category"] == "Alcoholic beverages"]["food_name"].dropna().unique().tolist())
_drinks_sub = df[df["food_category"] == "Alcoholic beverages"].copy()
_drinks_z = (_drinks_sub[_avg_cols].replace(0, np.nan) - _drinks_sub[_avg_cols].replace(0, np.nan).mean()) / _drinks_sub[_avg_cols].replace(0, np.nan).std()
_DEFAULT_COMPARE_DRINKS = _drinks_sub.assign(_s=_drinks_z.sum(axis=1)).nlargest(5, "_s")["food_name"].tolist()

# Most nutrient-dense food + top 3 alcohols (used by nutrient profile radar)
_all_sub = df[_avg_cols].replace(0, np.nan)
_all_std_safe = _all_sub.std().replace(0, 1)
_all_z_global = (_all_sub - _all_sub.mean()) / _all_std_safe
# Use Sheep liver specifically (mirrors insight-6); fall back to best liver by z-score
_liver_row = df[df["food_name"] == "Sheep liver"]
if _liver_row.empty:
    _liver_cand = df[df["food_name"].str.contains("liver", case=False, na=False)]
    if not _liver_cand.empty:
        _liver_row = _liver_cand.loc[[_all_z_global.loc[_liver_cand.index].sum(axis=1).idxmax()]]
_MOST_DENSE_FOOD = _liver_row.iloc[0]["food_name"] if not _liver_row.empty else "Chicken liver"
_TOP3_ALCOHOL_NAMES = _drinks_sub.assign(_s=_drinks_z.sum(axis=1)).nlargest(3, "_s")["food_name"].tolist()
_RADAR_COLORS = ["#C084FC", "#FCD34D", "#F472B6", "#F97316", "#38BDF8", "#6EE7B7", "#818CF8"]

# ── Helpers ────────────────────────────────────────────────────────────────────
def _empty(msg="No data", h=340):
    fig = go.Figure()
    fig.add_annotation(text=msg, x=0.5, y=0.5, xref="paper", yref="paper",
                       showarrow=False, font=dict(color="#F8FAFC", size=13))
    fig.update_layout(**BASE, height=h)
    return fig

def _rgba(hex_c, a):
    h = hex_c.lstrip("#")
    r,g,b = int(h[:2],16), int(h[2:4],16), int(h[4:],16)
    return f"rgba({r},{g},{b},{a})"

def _shorten(name, n=32):
    return name[:n]+"…" if len(name)>n else name

def _nutrient_list(group):
    if group == "vitamins": return EU_VITAMINS
    if group == "minerals": return EU_MINERALS
    return EU_ALL

def _fmt_cell(v, unit):
    """Compact numeric label for heatmap cells, e.g. '23mg', '0.34µg'."""
    if not pd.notna(v) or v == 0: return ""
    if v >= 100: return f"{v:.0f}{unit}"
    if v >= 10:  return f"{v:.1f}{unit}"
    if v >= 1:   return f"{v:.2f}{unit}"
    return f"{v:.3f}{unit}"

def _row(food):
    sub = df[df["food_name"]==food]
    return sub.iloc[0] if not sub.empty else None

def _base(h=None, extra_margin=None):
    b = {**BASE}
    if extra_margin: b["margin"] = extra_margin
    if h: b["height"] = h
    return b

# ── Summary: Scoreboard ────────────────────────────────────────────────────────
def make_scoreboard(h=300):
    ranks, means = {}, {}
    for n in EU_ALL:
        m = {}
        for c in EU_COUNTRIES:
            v = df[f"{n}_{c}"].replace(0,np.nan).dropna()
            m[c] = v.mean() if len(v)>0 else np.nan
        ordered = sorted(m.items(), key=lambda x: -(x[1] if pd.notna(x[1]) else -1e9))
        ranks[n] = {c:i+1 for i,(c,_) in enumerate(ordered)}
        means[n]  = m
    y_labs = [f"{EU_FLAGS[c]} {c}" for c in EU_COUNTRIES]
    x_labs = [EU_SHORT[n] for n in EU_ALL]
    z      = [[ranks[n].get(c,4) for n in EU_ALL] for c in EU_COUNTRIES]
    hover  = [[f"Avg: {means[n].get(c,0):.2f} {EU_UNITS[n]}/100g · Rank #{ranks[n].get(c,'?')}"
               for n in EU_ALL] for c in EU_COUNTRIES]
    text   = [[f"#{ranks[n].get(c,'')}" for n in EU_ALL] for c in EU_COUNTRIES]
    fig = go.Figure(go.Heatmap(
        z=z, x=x_labs, y=y_labs,
        colorscale=[[0,"#F59E0B"],[0.25,"#6EE7B7"],[0.5,"#818CF8"],
                    [0.75,"#334155"],[1.0,"#0F172A"]],
        zmin=1, zmax=7,
        text=text, customdata=hover,
        hovertemplate="<b>%{y}</b><br><b>%{x}</b><br>%{customdata}<extra></extra>",
        texttemplate="%{text}", textfont=dict(size=9, color="rgba(255,255,255,0.75)"),
        showscale=False, xgap=2, ygap=2,
    ))
    v = len(EU_VITAMINS)-0.5
    fig.add_shape(type="line",x0=v,x1=v,y0=-0.5,y1=len(EU_COUNTRIES)-0.5,
                  line=dict(color="rgba(255,255,255,0.3)",width=1.5,dash="dot"))
    fig.update_layout(
        **_base(h, extra_margin=dict(l=140,r=20,t=52,b=40)),
        title=dict(text="Country Rankings per Nutrient — gold = #1, dark = #7",
                   font=dict(size=14,color="#F8FAFC")),
        xaxis=dict(side="bottom",tickfont=dict(size=13),showgrid=False),
        yaxis=dict(tickfont=dict(size=13),showgrid=False,autorange="reversed"),
    )
    return fig

# ── Summary: Leaders ───────────────────────────────────────────────────────────
def make_leaders(h=520):
    sub = df[_avg_cols].replace(0,np.nan)
    z   = (sub-sub.mean())/sub.std()
    df2 = df[["food_name","food_category"]].copy()
    df2["score"] = z.sum(axis=1)
    top = df2.nlargest(20,"score").sort_values("score")
    colors = [CAT_COLORS.get(c,"#94A3B8") for c in top["food_category"]]
    fig = go.Figure(go.Bar(
        x=top["score"], y=[_shorten(n,36) for n in top["food_name"]], orientation="h",
        marker=dict(color=colors,line=dict(color="rgba(255,255,255,0.07)",width=0.5)),
        hovertemplate="<b>%{y}</b><br>Score: %{x:.1f}<extra></extra>",
    ))
    fig.update_layout(**BASE, height=h,
        title=dict(text="Most Nutrient-Dense Foods — composite z-score across 16 nutrients",
                   font=dict(size=14,color="#F8FAFC")),
        xaxis=dict(title="composite score",showgrid=True,
                   gridcolor="rgba(255,255,255,0.06)",tickfont=dict(size=13)),
        yaxis=dict(showgrid=False,tickfont=dict(size=13)),bargap=0.3)
    return fig

# ── Summary: Gaps ──────────────────────────────────────────────────────────────
def make_gaps(h=480):
    rows = []
    for n in EU_ALL:
        best_ratio, best_row = 1.0, None
        for _, r in df.iterrows():
            vals = {c:r.get(f"{n}_{c}",np.nan) for c in EU_COUNTRIES}
            valid = {c:v for c,v in vals.items() if pd.notna(v) and v>0.001}
            if len(valid)<2: continue
            hi_c=max(valid,key=valid.get); lo_c=min(valid,key=valid.get)
            ratio=valid[hi_c]/valid[lo_c]
            if ratio>best_ratio:
                best_ratio=ratio
                best_row=dict(nutrient=n,food=r["food_name"],
                              hi_c=hi_c,hi_v=valid[hi_c],lo_c=lo_c,lo_v=valid[lo_c],ratio=ratio)
        if best_row: rows.append(best_row)
    gap_df = pd.DataFrame(rows).nlargest(16,"ratio").sort_values("ratio")
    y_labels = [r["nutrient"] for _, r in gap_df.iterrows()]
    food_text = [_shorten(r["food"], 24) for _, r in gap_df.iterrows()]
    hover  = [f"{_shorten(r['food'],40)}\n{EU_FLAGS.get(r['hi_c'],'')} {r['hi_c']}: {r['hi_v']:.1f}  vs  "
              f"{EU_FLAGS.get(r['lo_c'],'')} {r['lo_c']}: {r['lo_v']:.1f} {EU_UNITS[r['nutrient']]}/100g  ·  {r['ratio']:.0f}× gap"
              for _,r in gap_df.iterrows()]
    colors = ["#6EE7B7" if r["nutrient"] in EU_VITAMINS else "#FCD34D"
              for _,r in gap_df.iterrows()]
    fig = go.Figure(go.Bar(
        y=y_labels, x=gap_df["ratio"].values, orientation="h",
        marker=dict(color=colors,line=dict(color="rgba(255,255,255,0.07)",width=0.5)),
        customdata=hover,
        hovertemplate="<b>%{y}</b><br>%{customdata}<extra></extra>",
        text=food_text,
        textposition="inside",
        insidetextanchor="middle",
        textfont=dict(size=9, color="rgba(255,255,255,0.9)"),
    ))
    fig.update_layout(**BASE, height=h,
        title=dict(text="Biggest Country Gaps — max÷min for the same food (1 per nutrient)",
                   font=dict(size=14,color="#F8FAFC")),
        xaxis=dict(title="ratio (highest ÷ lowest country)",type="log",
                   showgrid=True,gridcolor="rgba(255,255,255,0.06)",tickfont=dict(size=13)),
        yaxis=dict(showgrid=False,tickfont=dict(size=14)),bargap=0.28)
    return fig

def make_top_foods(nutrient="Selenium", top_n=10, country="EU_avg", h=None):
    col = f"{nutrient}_EU_avg" if country == "EU_avg" else f"{nutrient}_{country}"
    if col not in df.columns:
        return _empty(f"No data: {col}")
    sub = df[["food_name","food_category",col]].copy()
    sub[col] = sub[col].replace(0, np.nan)
    sub = sub.dropna(subset=[col]).nlargest(int(top_n), col).sort_values(col)
    if sub.empty: return _empty("No data found")
    unit = EU_UNITS.get(nutrient, "")
    colors = [CAT_COLORS.get(c, "#94A3B8") for c in sub["food_category"]]
    ctry_label = "EU Average" if country == "EU_avg" else f"{EU_FLAGS.get(country,'')} {country}"
    fig = go.Figure(go.Bar(
        y=[_shorten(n, 42) for n in sub["food_name"]],
        x=sub[col].values,
        orientation="h",
        marker=dict(color=colors, line=dict(color="rgba(255,255,255,0.07)", width=0.5)),
        text=[f"{v:.2f} {unit}" for v in sub[col]],
        textposition="auto",
        textfont=dict(size=10, color="#F8FAFC"),
        hovertemplate="<b>%{y}</b><br>%{text}/100g<extra></extra>",
    ))
    fig.update_layout(**BASE, height=h or max(400, 32*int(top_n)+120),
        title=dict(text=f"Top {top_n} Foods Highest in {nutrient} — {ctry_label}",
                   font=dict(size=13, color="#FFFFFF")),
        xaxis=dict(title=f"{nutrient} ({unit}/100g)", showgrid=True,
                   gridcolor="rgba(255,255,255,0.08)", tickfont=dict(size=14)),
        yaxis=dict(showgrid=False, tickfont=dict(size=14)),
        bargap=0.28)
    return fig


def make_rda_chart(food="Tuna and bonito (generic)", nutrient="Selenium",
                   age_group="18-64", sex="male", weight=70, height=175, h=None):
    rda_table = EU_RDA_DEMO.get((age_group, sex), EU_RDA)
    rda = rda_table.get(nutrient, EU_RDA.get(nutrient, 1))
    unit = EU_UNITS.get(nutrient, "")
    bmi = round(weight / ((height / 100) ** 2), 1) if height and weight else None
    row = _row(food)
    if row is None: return _empty(f"Food not found: {food}")
    data = []
    for c in EU_COUNTRIES:
        v = row.get(f"{nutrient}_{c}", np.nan)
        if pd.notna(v) and v > 0:
            grams = round(rda / v * 100, 1)
            data.append((c, grams, v))
    if not data: return _empty("No country data")
    data.sort(key=lambda x: x[1])
    countries, grams, content = zip(*data)
    max_mult = max(grams) / min(grams)
    demo_str = f"{age_group}y {sex}, {weight}kg/{height}cm"
    if bmi:
        demo_str += f" (BMI {bmi})"
    fig = go.Figure(go.Bar(
        y=[f"{EU_FLAGS[c]} {c}" for c in countries],
        x=list(grams),
        orientation="h",
        marker=dict(color=list(grams), colorscale="RdYlGn_r",
                    cmin=min(grams), cmax=max(grams), showscale=False,
                    line=dict(color="rgba(255,255,255,0.07)", width=0.5)),
        text=[f"{g:.0f}g" for g in grams],
        textposition="outside",
        textfont=dict(size=12, color="#F8FAFC"),
        customdata=list(content),
        hovertemplate="%{y}<br><b>%{x:.0f}g</b> to hit RDA<br>Content: %{customdata:.1f} "+unit+"/100g<extra></extra>",
    ))
    fig.update_layout(**BASE, height=h or 380,
        title=dict(
            text=f"Grams of {_shorten(food,28)} to hit {nutrient} RDA ({rda} {unit}) · {demo_str} · {max_mult:.1f}× country gap",
            font=dict(size=13, color="#FFFFFF")
        ),
        xaxis=dict(title="Grams needed to reach daily RDA", showgrid=True,
                   gridcolor="rgba(255,255,255,0.08)", tickfont=dict(size=14)),
        yaxis=dict(showgrid=False, tickfont=dict(size=14)),
        bargap=0.3)
    return fig


# ── Heatmap ────────────────────────────────────────────────────────────────────
def _heatmap_scale(arr, scale, nutrients=None):
    """Return (z_norm, cscale, zmid_val, cbar_title, z_pct) for a 2-D raw-value array.
    z_pct is the raw % of RDA array (for cell text) when scale='rda', else None."""
    if scale == "zscore":
        col_m = np.nanmean(arr, axis=0); col_s = np.nanstd(arr, axis=0)
        col_s[col_s == 0] = 1
        return np.clip((arr - col_m) / col_s, -2.5, 2.5), "Plasma", 0, "z-score", None
    if scale == "rda" and nutrients is not None:
        rda_arr = np.array([EU_RDA.get(n, 1) for n in nutrients], dtype=float)
        rda_arr[rda_arr == 0] = 1
        pct = np.clip(arr / rda_arr * 100, 0, None)  # raw %, uncapped
        z_norm = np.log1p(pct)                         # log scale for colour so high values still differ
        return z_norm, "YlOrRd", None, "% of RDA (EU adult NRV)", pct
    # values: per-column % of max for colour
    col_max = np.nanmax(arr, axis=0); col_max[col_max == 0] = 1
    return arr / col_max, "YlOrRd", None, "% of max", None

def make_heatmap(view="food", category="Meat and meat products", nutrient_group="all", scale="zscore", h=None):
    nutrients = _nutrient_list(nutrient_group)
    x_labs    = [EU_SHORT[n] for n in nutrients]
    show_vals = scale == "values"

    if view == "country":
        sub = df if category == "__all__" else df[df["food_category"]==category]
        z_mat, h_mat = [], []
        for c in EU_COUNTRIES:
            row_z, row_h = [], []
            for n in nutrients:
                v = sub[f"{n}_{c}"].replace(0,np.nan).dropna()
                m = v.mean() if len(v)>0 else np.nan
                row_z.append(m)
                row_h.append(f"{m:.2f} {EU_UNITS[n]}/100g" if pd.notna(m) else "No data")
            z_mat.append(row_z); h_mat.append(row_h)
        z_arr = np.array(z_mat, dtype=float)
        z_norm, cscale, zmid_val, cbar_title, z_pct = _heatmap_scale(z_arr, scale, nutrients)
        # Cell text: actual mg/µg for values mode, XX% for rda mode
        if show_vals:
            cell_text = [[_fmt_cell(z_arr[i,j], EU_UNITS[nutrients[j]]) for j in range(len(nutrients))] for i in range(len(EU_COUNTRIES))]
        elif scale == "rda" and z_pct is not None:
            cell_text = [[f"{z_pct[i,j]:.0f}%" if np.isfinite(z_pct[i,j]) else "" for j in range(len(nutrients))] for i in range(len(EU_COUNTRIES))]
        else:
            cell_text = None
        y_labs = [f"{EU_FLAGS[c]} {c}" for c in EU_COUNTRIES]
        hm_kw = dict(zmid=zmid_val) if zmid_val is not None else {}
        txt_kw = dict(text=cell_text, texttemplate="%{text}",
                      textfont=dict(size=9, color="rgba(255,255,255,0.9)")) if cell_text is not None else {}
        fig = go.Figure(go.Heatmap(
            z=z_norm, x=x_labs, y=y_labs, colorscale=cscale, **hm_kw, **txt_kw,
            customdata=np.array(h_mat),
            hovertemplate="<b>%{y}</b><br><b>%{x}</b><br>%{customdata}<extra></extra>",
            colorbar=dict(title=dict(text=cbar_title, font=dict(color="#F8FAFC",size=10)),
                          tickfont=dict(color="#F8FAFC",size=9)),
            xgap=3, ygap=3,
        ))
        cat_label = "all categories" if category=="__all__" else category
        scale_lbl = {"zscore":"z-score","rda":"% of RDA","values":"actual values"}.get(scale, scale)
        fig.update_layout(**_base(h or 340, extra_margin=dict(l=160,r=80,t=52,b=40)),
            title=dict(text=f"Country Nutrient Profile — {cat_label} ({scale_lbl})",
                       font=dict(size=14,color="#F8FAFC")),
            xaxis=dict(tickfont=dict(size=13),showgrid=False),
            yaxis=dict(tickfont=dict(size=13),showgrid=False,autorange="reversed"))
    else:
        sub = df[df["food_category"]==category].copy()
        if sub.empty: return _empty(f"No data for: {category}", h or 480)
        ac = [f"{n}_EU_avg" for n in nutrients]
        tmp = sub[ac].replace(0,np.nan)
        zz  = (tmp-tmp.mean())/tmp.std()
        sub["_score"] = zz.sum(axis=1)
        sub = sub.nlargest(40,"_score").sort_values("_score",ascending=True)
        vals = sub[ac].replace(0,np.nan).values.astype(float)
        hover = [[
            f"{row.get(f'{n}_EU_avg',np.nan):.2f} {EU_UNITS[n]}/100g"
            if pd.notna(row.get(f"{n}_EU_avg")) and row.get(f"{n}_EU_avg",0)>0 else "No data"
            for n in nutrients
        ] for _,row in sub.iterrows()]
        full_names = sub["food_name"].values
        cdata_3d = np.array([[[full_names[i], hover[i][j]]
                               for j in range(len(nutrients))]
                              for i in range(len(sub))])
        z_norm, cscale, zmid_val, cbar_title, z_pct = _heatmap_scale(vals, scale, nutrients)
        # Cell text: actual mg/µg for values mode, XX% for rda mode
        if show_vals:
            cell_text = [[_fmt_cell(vals[i,j], EU_UNITS[nutrients[j]]) for j in range(len(nutrients))] for i in range(len(sub))]
        elif scale == "rda" and z_pct is not None:
            cell_text = [[f"{z_pct[i,j]:.0f}%" if np.isfinite(z_pct[i,j]) else "" for j in range(len(nutrients))] for i in range(len(sub))]
        else:
            cell_text = None
        y_labs = [_shorten(n,34) for n in sub["food_name"]]
        hm_kw = dict(zmid=zmid_val) if zmid_val is not None else {}
        txt_kw = dict(text=cell_text, texttemplate="%{text}",
                      textfont=dict(size=7, color="rgba(255,255,255,0.85)")) if cell_text is not None else {}
        scale_lbl = {"zscore":"z-score","rda":"% of RDA","values":"actual values"}.get(scale, scale)
        fig = go.Figure(go.Heatmap(
            z=z_norm, x=x_labs, y=y_labs, colorscale=cscale, **hm_kw, **txt_kw,
            customdata=cdata_3d,
            hovertemplate="<b>%{customdata[0]}</b><br><b>%{x}</b><br>%{customdata[1]}<extra></extra>",
            colorbar=dict(title=dict(text=cbar_title, font=dict(color="#F8FAFC",size=10)),
                          tickfont=dict(color="#F8FAFC",size=9)),
            xgap=1, ygap=1,
        ))
        fig.update_layout(**BASE, height=h or max(500,22*len(sub)+120),
            title=dict(text=f"Top nutrient-dense foods — {category} (EU avg, {scale_lbl})",
                       font=dict(size=14,color="#F8FAFC")),
            xaxis=dict(tickfont=dict(size=13),showgrid=False),
            yaxis=dict(tickfont=dict(size=13),showgrid=False))
    if nutrient_group=="all":
        n_rows = len(EU_COUNTRIES) if view=="country" else len(sub)
        fig.add_shape(type="line",
                      x0=len(EU_VITAMINS)-0.5, x1=len(EU_VITAMINS)-0.5,
                      y0=-0.5, y1=n_rows-0.5,
                      line=dict(color="rgba(255,255,255,0.35)",width=1.5,dash="dot"))
    return fig


# ── Single-food comparison heatmap ─────────────────────────────────────────────
def make_single_food_heatmap(food_name, countries, nutrient_group="all", scale="zscore", h=None):
    nutrients = _nutrient_list(nutrient_group)
    x_labs    = [EU_SHORT[n] for n in nutrients]
    row = df[df["food_name"]==food_name]
    if row.empty: return _empty(f"Food not found: {food_name}")
    row = row.iloc[0]
    countries = countries or EU_COUNTRIES
    show_vals = scale == "values"

    z_mat, h_mat = [], []
    for c in countries:
        row_raw, row_h = [], []
        for n in nutrients:
            v = row.get(f"{n}_{c}",np.nan)
            if pd.isna(v) or v==0: v=np.nan
            row_raw.append(v)
            row_h.append(f"{v:.2f} {EU_UNITS[n]}/100g" if pd.notna(v) else "No data")
        z_mat.append(row_raw); h_mat.append(row_h)

    z_arr = np.array(z_mat, dtype=float)
    # zscore mode uses RdYlGn (green=high) to distinguish from other views
    if scale == "zscore":
        col_m = np.nanmean(z_arr, axis=0); col_s = np.nanstd(z_arr, axis=0)
        col_s[col_s==0]=1
        z_norm = (z_arr - col_m) / col_s
        cscale, zmid_val, cbar_title = "RdYlGn", 0, "vs others"
        title_suffix = "green = relatively high"
    elif scale == "rda":
        rda_arr = np.array([EU_RDA.get(n, 1) for n in nutrients], dtype=float)
        rda_arr[rda_arr == 0] = 1
        z_pct = np.clip(z_arr / rda_arr * 100, 0, None)
        z_norm = np.log1p(z_pct)
        cscale, zmid_val, cbar_title = "YlOrRd", None, "% of RDA (EU adult NRV)"
        title_suffix = "% of daily RDA per 100g (EU adult NRV)"
    else:  # values
        z_pct = None
        col_max = np.nanmax(z_arr, axis=0); col_max[col_max == 0] = 1
        z_norm = z_arr / col_max
        cscale, zmid_val, cbar_title = "YlOrRd", None, "% of max"
        title_suffix = "actual values (% of max)"

    if show_vals:
        cell_text = [[_fmt_cell(z_arr[i,j], EU_UNITS[nutrients[j]]) for j in range(len(nutrients))] for i in range(len(countries))]
    elif scale == "rda" and z_pct is not None:
        cell_text = [[f"{z_pct[i,j]:.0f}%" if np.isfinite(z_pct[i,j]) else "" for j in range(len(nutrients))] for i in range(len(countries))]
    else:
        cell_text = None
    y_labs = [f"{EU_FLAGS[c]} {c}" for c in countries]
    hm_kw  = dict(zmid=zmid_val) if zmid_val is not None else {}
    txt_kw = dict(text=cell_text, texttemplate="%{text}",
                  textfont=dict(size=10, color="rgba(255,255,255,0.9)")) if cell_text is not None else {}
    n_rows = len(countries)
    fig = go.Figure(go.Heatmap(
        z=z_norm, x=x_labs, y=y_labs, colorscale=cscale, **hm_kw, **txt_kw,
        customdata=np.array(h_mat),
        hovertemplate="<b>%{y}</b><br><b>%{x}</b><br>%{customdata}<extra></extra>",
        colorbar=dict(title=dict(text=cbar_title, font=dict(color="#F8FAFC",size=10)),
                      tickfont=dict(color="#F8FAFC",size=9)),
        xgap=3, ygap=3,
    ))
    if nutrient_group=="all":
        fig.add_shape(type="line",
                      x0=len(EU_VITAMINS)-0.5, x1=len(EU_VITAMINS)-0.5,
                      y0=-0.5, y1=n_rows-0.5,
                      line=dict(color="rgba(255,255,255,0.35)",width=1.5,dash="dot"))
    fig.update_layout(
        **{**BASE,"margin":dict(l=160,r=80,t=60,b=40)},
        height=h or max(300, 56*n_rows+120),
        title=dict(text=f"<b>{food_name}</b> — nutrient profile by country ({title_suffix})",
                   font=dict(size=14,color="#F8FAFC")),
        xaxis=dict(tickfont=dict(size=13),showgrid=False),
        yaxis=dict(tickfont=dict(size=14),showgrid=False,autorange="reversed"),
    )
    return fig


def make_food_diff_chart(food_name, countries, nutrient_group="all", log_scale=False, h=None):
    """Dumbbell chart: per-nutrient values as % of RDA, one dot per country."""
    nutrients = _nutrient_list(nutrient_group)
    row = df[df["food_name"] == food_name]
    if row.empty: return _empty("Food not found")
    row = row.iloc[0]
    countries = countries or EU_COUNTRIES
    if len(countries) < 2: return _empty("Select at least 2 countries to compare")

    # Build per-nutrient data as % of RDA (normalises across different units)
    ndata = {}
    for n in nutrients:
        rda = EU_RDA.get(n, 1)
        nd = {}
        for c in countries:
            v = row.get(f"{n}_{c}", np.nan)
            if pd.notna(v) and v > 0:
                nd[c] = v / rda * 100
        if len(nd) >= 2:
            ndata[n] = nd
    if not ndata:
        return _empty("No overlapping data for these countries")

    fig = go.Figure()

    # Connecting lines from min to max value per nutrient
    for n, nd in ndata.items():
        vals = list(nd.values())
        fig.add_trace(go.Scatter(
            x=[min(vals), max(vals)], y=[EU_SHORT[n], EU_SHORT[n]],
            mode="lines", line=dict(color="rgba(255,255,255,0.18)", width=3),
            showlegend=False, hoverinfo="skip",
        ))

    # One dot trace per country
    for c in countries:
        x_vals, y_vals, cdata = [], [], []
        for n, nd in ndata.items():
            if c in nd:
                raw = row.get(f"{n}_{c}", 0)
                x_vals.append(nd[c])
                y_vals.append(EU_SHORT[n])
                cdata.append(f"{raw:.2f} {EU_UNITS[n]}/100g = {nd[c]:.1f}% RDA")
        if x_vals:
            fig.add_trace(go.Scatter(
                x=x_vals, y=y_vals, mode="markers",
                marker=dict(color=EU_COLORS[c], size=16,
                            line=dict(color="rgba(255,255,255,0.35)", width=2)),
                name=f"{EU_FLAGS.get(c,'')} {c}",
                customdata=cdata,
                hovertemplate="<b>%{y}</b><br>"
                              + f"{EU_FLAGS.get(c,'')} {c}<br>"
                              + "%{customdata}<extra></extra>",
            ))

    max_x = max(max(nd.values()) for nd in ndata.values())
    if len(countries) == 2:
        c1, c2 = countries[0], countries[1]
        title_text = (f"{EU_FLAGS.get(c1,'')} {c1} vs {EU_FLAGS.get(c2,'')} {c2}"
                      f" — {_shorten(food_name, 30)} · % of daily RDA per 100g")
    else:
        title_text = f"Country comparison — {_shorten(food_name, 30)} · % of daily RDA per 100g"

    xaxis_kw = dict(title="% of daily RDA (per 100g serving)", showgrid=True,
                    gridcolor="rgba(255,255,255,0.08)", tickfont=dict(size=13), ticksuffix="%")
    if log_scale:
        xaxis_kw["type"] = "log"
    else:
        xaxis_kw["range"] = [0, max_x * 1.15]

    fig.update_layout(**BASE, height=h or max(360, 44 * len(ndata) + 120),
        title=dict(text=title_text, font=dict(size=13, color="#FFFFFF")),
        xaxis=xaxis_kw,
        yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.06)",
                   tickfont=dict(size=13)),
        legend=dict(orientation="h", y=-0.12, font=dict(size=12)),
    )
    return fig


# ── Heatmap drilldown ──────────────────────────────────────────────────────────
def make_drilldown(food_or_country, nutrient_short, view, h=None):
    n_full = EU_SHORT_REV.get(nutrient_short, nutrient_short)
    if n_full not in EU_ALL:
        n_full = next((k for k,v in EU_SHORT.items() if v==nutrient_short), nutrient_short)
    unit = EU_UNITS.get(n_full,"")

    if view in ("food","single_food"):
        food_name = food_or_country
        sub = df[df["food_name"].str.strip()==food_name.strip()]
        if sub.empty: return _empty(f"Not found: {food_name}")
        row = sub.iloc[0]
        data = sorted(
            [(c, row.get(f"{n_full}_{c}",np.nan)) for c in EU_COUNTRIES
             if pd.notna(row.get(f"{n_full}_{c}",np.nan)) and row.get(f"{n_full}_{c}",0)>0],
            key=lambda x: -x[1])
        if not data: return _empty("No country data for this cell")
        countries, values = zip(*data)
        fig = go.Figure(go.Bar(
            y=[f"{EU_FLAGS[c]} {c}" for c in countries], x=list(values), orientation="h",
            marker=dict(color=[EU_COLORS[c] for c in countries],
                        line=dict(color="rgba(255,255,255,0.08)",width=0.5)),
            text=[f"{v:.2f} {unit}" for v in values], textposition="auto",
            hovertemplate="%{y}: %{text}/100g<extra></extra>",
        ))
        fig.update_layout(**BASE, height=h or max(280,48*len(countries)+80),
            title=dict(text=f"{n_full} in '{_shorten(food_name,42)}' by country",
                       font=dict(size=14,color="#F8FAFC")),
            xaxis=dict(title=f"{n_full} ({unit}/100g)",showgrid=True,
                       gridcolor="rgba(255,255,255,0.06)",tickfont=dict(size=13)),
            yaxis=dict(showgrid=False,tickfont=dict(size=13)),
            transition=dict(duration=450,easing="cubic-in-out"))
    else:
        country = food_or_country
        for c in EU_COUNTRIES:
            if c in country: country=c; break
        col = f"{n_full}_{country}"
        if col not in df.columns: return _empty(f"No data: {country}")
        sub = df[["food_name","food_category",col]].copy()
        sub[col] = sub[col].replace(0,np.nan)
        sub = sub.dropna(subset=[col]).nlargest(25,col).sort_values(col)
        colors = [CAT_COLORS.get(c,"#94A3B8") for c in sub["food_category"]]
        fig = go.Figure(go.Bar(
            y=[_shorten(n,32) for n in sub["food_name"]], x=sub[col].values, orientation="h",
            marker=dict(color=colors,line=dict(color="rgba(255,255,255,0.07)",width=0.5)),
            text=[f"{v:.2f} {unit}" for v in sub[col]], textposition="auto",
            hovertemplate="%{y}: %{text}/100g<extra></extra>",
        ))
        fig.update_layout(**BASE, height=h or max(420,22*len(sub)+100),
            title=dict(text=f"{EU_FLAGS.get(country,'')} {country} — Top foods for {n_full} ({unit}/100g)",
                       font=dict(size=14,color="#F8FAFC")),
            xaxis=dict(title=f"{n_full} ({unit}/100g)",showgrid=True,
                       gridcolor="rgba(255,255,255,0.06)",tickfont=dict(size=13)),
            yaxis=dict(showgrid=False,tickfont=dict(size=13)),
            transition=dict(duration=450,easing="cubic-in-out"))
    return fig


# ── Drinks section ─────────────────────────────────────────────────────────────
def make_drinks_compare(drink_names=None, nutrient_group="all", h=None):
    """Radar: compare multiple drinks side by side (EU avg per nutrient axis)."""
    nutrients = _nutrient_list(nutrient_group)
    theta = [EU_SHORT[n] for n in nutrients] + [EU_SHORT[nutrients[0]]]
    drinks_sub = df[df["food_category"] == "Alcoholic beverages"]
    if not drink_names:
        drink_names = _DEFAULT_COMPARE_DRINKS
    axis_max = {n: max(float(drinks_sub[f"{n}_EU_avg"].replace(0, np.nan).max() or 1e-9), 1e-9)
                for n in nutrients}
    DCOLS = ["#C084FC","#FCD34D","#F472B6","#F97316","#38BDF8","#6EE7B7","#818CF8"]
    fig = go.Figure()
    for i, name in enumerate(list(drink_names)[:7]):
        row = df[df["food_name"] == name]
        if row.empty: continue
        row = row.iloc[0]
        color = DCOLS[i % len(DCOLS)]
        vals = [float(row.get(f"{n}_EU_avg", 0) or 0) for n in nutrients]
        norm = [v / axis_max[n] * 100 for n, v in zip(nutrients, vals)]
        raw  = [f"{v:.2f} {EU_UNITS[n]}/100g" for n, v in zip(nutrients, vals)]
        label = _shorten(name, 26)
        fig.add_trace(go.Scatterpolar(
            r=norm + [norm[0]], theta=theta, name=label,
            fill="toself", fillcolor=_rgba(color, 0.08),
            line=dict(color=color, width=2),
            customdata=raw + [raw[0]],
            hovertemplate="%{theta}<br>%{customdata}<extra>" + label + "</extra>",
        ))
    fig.update_layout(
        **{**BASE, "margin": dict(l=80, r=80, t=70, b=90)},
        height=h or 520,
        title=dict(text="Compare Drinks — nutrient radar (EU avg, % of max in alcoholic drinks)",
                   font=dict(size=14, color="#FFFFFF")),
        polar=dict(bgcolor="rgba(0,0,0,0)",
            radialaxis=dict(visible=True, range=[0, 100], showgrid=True,
                           gridcolor="rgba(255,255,255,0.08)", showticklabels=False),
            angularaxis=dict(tickfont=dict(size=12, color="#F8FAFC"),
                            gridcolor="rgba(255,255,255,0.08)")),
        legend=dict(orientation="h", y=-0.22, font=dict(size=11)),
    )
    return fig


def make_drinks_beer_country(h=340):
    """Grouped bar: key minerals in regular beer by country."""
    beer = df[df["food_name"]=="Beer, regular"]
    if beer.empty: return _empty("Beer data not found")
    beer = beer.iloc[0]
    minerals = ["Potassium","Magnesium","Phosphorus","Calcium"]
    fig = go.Figure()
    for n in minerals:
        vals = [beer.get(f"{n}_{c}",0) or 0 for c in EU_COUNTRIES]
        fig.add_trace(go.Bar(
            name=n, x=[f"{EU_FLAGS[c]} {c}" for c in EU_COUNTRIES], y=vals,
            hovertemplate=f"<b>%{{x}}</b><br>{n}: %{{y:.1f}} mg/100g<extra></extra>",
        ))
    fig.update_layout(**BASE, height=h,
        barmode="group",
        title=dict(text="Key Minerals in Regular Beer by Country — Germany & Finland brew higher-mineral beer",
                   font=dict(size=14,color="#F8FAFC")),
        yaxis=dict(title="mg/100g",showgrid=True,gridcolor="rgba(255,255,255,0.06)",tickfont=dict(size=13)),
        xaxis=dict(showgrid=False,tickfont=dict(size=13)),
        legend=dict(orientation="h",y=-0.15,font=dict(size=10)),bargap=0.2,bargroupgap=0.05,
        colorway=["#6EE7B7","#818CF8","#F472B6","#FCD34D"])
    return fig


def make_drinks_wine_radar(h=400):
    """Radar: most nutrient-dense food (liver) vs top 3 alcohols — cross-item normalised."""
    nutrients_sel = ["Calcium","Iron","Magnesium","Potassium","Phosphorus","Zinc","Selenium","Riboflavin"]
    theta = [EU_SHORT[n] for n in nutrients_sel] + [EU_SHORT[nutrients_sel[0]]]

    # Items: liver first (pink, thick) then top-3 alcohols
    alcohol_colors = ["#C084FC", "#FCD34D", "#38BDF8"]
    items = [(_MOST_DENSE_FOOD, "#F472B6", 3.0)] + [
        (name, alcohol_colors[i], 2.0) for i, name in enumerate(_TOP3_ALCOHOL_NAMES)
    ]

    # Cross-item axis max per nutrient (so all traces share same scale)
    axis_max = {n: 1e-9 for n in nutrients_sel}
    for food_name, _, _ in items:
        row = df[df["food_name"] == food_name]
        if row.empty: continue
        row = row.iloc[0]
        for n in nutrients_sel:
            v = float(row.get(f"{n}_EU_avg", 0) or 0)
            axis_max[n] = max(axis_max[n], v)

    fig = go.Figure()
    for food_name, color, lw in items:
        row = df[df["food_name"] == food_name]
        if row.empty: continue
        row = row.iloc[0]
        is_liver = food_name == _MOST_DENSE_FOOD
        vals = [float(row.get(f"{n}_EU_avg", 0) or 0) for n in nutrients_sel]
        norm = [v / axis_max[n] * 100 for n, v in zip(nutrients_sel, vals)]
        raw  = [f"{v:.2f} {EU_UNITS[n]}/100g" for n, v in zip(nutrients_sel, vals)]
        label = _shorten(food_name, 28)
        fig.add_trace(go.Scatterpolar(
            r=norm + [norm[0]], theta=theta, name=label,
            fill="toself",
            fillcolor=_rgba(color, 0.20 if is_liver else 0.08),
            line=dict(color=color, width=lw, dash="solid" if is_liver else "solid"),
            customdata=raw + [raw[0]],
            hovertemplate="%{theta}<br>%{customdata}<extra>" + label + "</extra>",
        ))

    top_alcohol_label = _shorten(_TOP3_ALCOHOL_NAMES[0], 22) if _TOP3_ALCOHOL_NAMES else "top alcohol"
    fig.update_layout(**{**BASE, "margin": dict(l=60, r=60, t=70, b=80)}, height=h,
        title=dict(
            text=f"Nutrient Profile: {_shorten(_MOST_DENSE_FOOD, 22)} vs Top 3 Alcohols — shared scale per nutrient",
            font=dict(size=13, color="#F8FAFC")),
        polar=dict(bgcolor="rgba(0,0,0,0)",
            radialaxis=dict(visible=True, range=[0, 100], showgrid=True,
                           gridcolor="rgba(255,255,255,0.08)", showticklabels=False),
            angularaxis=dict(tickfont=dict(size=13, color="#F8FAFC"),
                            gridcolor="rgba(255,255,255,0.08)")),
        legend=dict(orientation="h", y=-0.18, font=dict(size=10)))
    return fig


def make_drinks_radar(drink_name="Beer, regular", countries=None, nutrient_group="all", h=None):
    """Radar: nutrient profile of a specific drink with per-country overlays."""
    nutrients = _nutrient_list(nutrient_group)
    theta = [EU_SHORT[n] for n in nutrients] + [EU_SHORT[nutrients[0]]]
    row = df[df["food_name"] == drink_name]
    if row.empty:
        return _empty(f"Drink not found: {drink_name}")
    row = row.iloc[0]
    countries = countries or ["EU_avg"]
    drinks_sub = df[df["food_category"] == "Alcoholic beverages"]
    axis_max = {n: max(float(drinks_sub[f"{n}_EU_avg"].replace(0, np.nan).max() or 1e-9), 1e-9)
                for n in nutrients}
    fig = go.Figure()
    for c in countries:
        col_suf = "EU_avg" if c == "EU_avg" else c
        label = "EU Average" if c == "EU_avg" else f"{EU_FLAGS.get(c,'')} {c}"
        color = "#CBD5E1" if c == "EU_avg" else EU_COLORS.get(c, "#94A3B8")
        vals = [float(row.get(f"{n}_{col_suf}", 0) or 0) for n in nutrients]
        norm = [v / axis_max[n] * 100 for n, v in zip(nutrients, vals)]
        raw  = [f"{v:.2f} {EU_UNITS[n]}/100g" for n, v in zip(nutrients, vals)]
        fig.add_trace(go.Scatterpolar(
            r=norm + [norm[0]], theta=theta, name=label,
            fill="toself", fillcolor=_rgba(color, 0.12),
            line=dict(color=color, width=2.5),
            customdata=raw + [raw[0]],
            hovertemplate="%{theta}<br>%{customdata}<extra>" + label + "</extra>",
        ))
    fig.update_layout(
        **{**BASE, "margin": dict(l=80, r=80, t=70, b=90)},
        height=h or 520,
        title=dict(text=f"{_shorten(drink_name, 46)} — nutrient profile by country",
                   font=dict(size=14, color="#FFFFFF")),
        polar=dict(bgcolor="rgba(0,0,0,0)",
            radialaxis=dict(visible=True, range=[0, 100], showgrid=True,
                           gridcolor="rgba(255,255,255,0.08)", showticklabels=False),
            angularaxis=dict(tickfont=dict(size=12, color="#F8FAFC"),
                            gridcolor="rgba(255,255,255,0.08)")),
        legend=dict(orientation="h", y=-0.22, font=dict(size=12)),
    )
    return fig


# ── Insight figures ────────────────────────────────────────────────────────────
def make_i1(h=None):
    food,nut = "Salt, flavoured","Calcium"
    row=_row(food);
    if row is None: return _empty()
    eu=row.get(f"{nut}_EU_avg",0)
    data=sorted([(c,row.get(f"{nut}_{c}",np.nan)) for c in EU_COUNTRIES
                 if pd.notna(row.get(f"{nut}_{c}",np.nan)) and row.get(f"{nut}_{c}",0)>0],key=lambda x:x[1])
    countries,values=zip(*data)
    fig=go.Figure(go.Bar(y=[f"{EU_FLAGS[c]} {c}" for c in countries],x=[v-eu for v in values],
        orientation="h",marker=dict(color=[EU_COLORS[c] for c in countries]),
        text=[f"{v:.0f} mg" for v in values],textposition="auto",
        hovertemplate="%{y}: %{text}/100g<extra></extra>"))
    fig.add_vline(x=0,line_color="rgba(255,255,255,0.3)",line_dash="dash")
    fig.update_layout(**BASE,height=h or 300,bargap=0.3,
        title=dict(text=f"Calcium in Salt — deviation from EU avg ({eu:.0f} mg/100g)",
                   font=dict(size=15,color="#F8FAFC")),
        xaxis=dict(title="mg deviation",showgrid=True,gridcolor="rgba(255,255,255,0.06)",tickfont=dict(size=13)),
        yaxis=dict(showgrid=False,tickfont=dict(size=13)))
    return fig

def make_i2(h=None):
    food,nut="Oysters","Zinc"; row=_row(food)
    if row is None: return _empty()
    data=sorted([(c,row.get(f"{nut}_{c}",np.nan)) for c in EU_COUNTRIES
                 if pd.notna(row.get(f"{nut}_{c}",np.nan)) and row.get(f"{nut}_{c}",0)>0],key=lambda x:x[1])
    countries,values=zip(*data)
    fig=go.Figure()
    for c,v in zip(countries,values):
        fig.add_shape(type="line",x0=0,x1=v,y0=f"{EU_FLAGS[c]} {c}",y1=f"{EU_FLAGS[c]} {c}",
                      line=dict(color=EU_COLORS[c],width=2))
    fig.add_trace(go.Scatter(x=list(values),y=[f"{EU_FLAGS[c]} {c}" for c in countries],
        mode="markers+text",
        marker=dict(size=14,color=[EU_COLORS[c] for c in countries],
                    line=dict(color="rgba(255,255,255,0.3)",width=1.5)),
        text=[f" {v:.1f}" for v in values],textposition="middle right",
        textfont=dict(size=9,color="#F8FAFC"),
        hovertemplate="%{y}: %{x:.1f} mg Zn/100g<extra></extra>",showlegend=False))
    fig.update_layout(**BASE,height=h or 300,showlegend=False,
        title=dict(text="Zinc in Oysters — 7× gap between Netherlands & Finland",font=dict(size=15,color="#F8FAFC")),
        xaxis=dict(title="Zinc (mg/100g)",range=[0,70],showgrid=True,gridcolor="rgba(255,255,255,0.06)",tickfont=dict(size=13)),
        yaxis=dict(showgrid=False,tickfont=dict(size=13)))
    return fig

def make_i3(h=None):
    food,nut="Tuna and bonito (generic)","Selenium"; row=_row(food)
    if row is None: return _empty()
    data=sorted([(c,row.get(f"{nut}_{c}",np.nan)) for c in EU_COUNTRIES
                 if pd.notna(row.get(f"{nut}_{c}",np.nan)) and row.get(f"{nut}_{c}",0)>0],key=lambda x:x[1])
    countries,values=zip(*data)
    fig=go.Figure(go.Bar(y=[f"{EU_FLAGS[c]} {c}" for c in countries],x=list(values),orientation="h",
        marker=dict(color=list(values),colorscale="Turbo",showscale=False,
                    line=dict(color="rgba(255,255,255,0.06)",width=0.5)),
        text=[f"{v:.0f} µg" for v in values],textposition="auto",
        hovertemplate="%{y}: %{text} Se/100g<extra></extra>"))
    fig.update_layout(**BASE,height=h or 300,bargap=0.3,
        title=dict(text="Selenium in Tuna — France 3× higher than Finland/Sweden",font=dict(size=15,color="#F8FAFC")),
        xaxis=dict(title="Selenium (µg/100g)",showgrid=True,gridcolor="rgba(255,255,255,0.06)",tickfont=dict(size=13)),
        yaxis=dict(showgrid=False,tickfont=dict(size=13)))
    return fig

def make_i4(h=None):
    food,nut="Cocoa powder","Magnesium"; row=_row(food)
    if row is None: return _empty()
    data=sorted([(c,row.get(f"{nut}_{c}",np.nan)) for c in EU_COUNTRIES
                 if pd.notna(row.get(f"{nut}_{c}",np.nan)) and row.get(f"{nut}_{c}",0)>0],key=lambda x:-x[1])
    countries,values=zip(*data)
    fig=go.Figure(go.Bar(x=[f"{EU_FLAGS[c]} {c}" for c in countries],y=list(values),
        marker=dict(color=[EU_COLORS[c] for c in countries],line=dict(color="rgba(255,255,255,0.08)",width=0.5)),
        text=[f"{v:.0f}" for v in values],textposition="outside",textfont=dict(size=15,color="#F8FAFC"),
        hovertemplate="%{x}: %{y:.0f} mg Mg/100g<extra></extra>"))
    fig.update_layout(**BASE,height=h or 320,bargap=0.35,
        title=dict(text="Magnesium in Cocoa Powder — Germany/Netherlands 4.8× France",font=dict(size=15,color="#F8FAFC")),
        yaxis=dict(title="Magnesium (mg/100g)",showgrid=True,gridcolor="rgba(255,255,255,0.06)",tickfont=dict(size=13)),
        xaxis=dict(showgrid=False,tickfont=dict(size=13)))
    return fig

def make_i5(h=None):
    comp=df[df["food_category"]=="Composite dishes"].copy()
    tmp=comp[_avg_cols].replace(0,np.nan); z=(tmp-tmp.mean())/tmp.std()
    comp["score"]=z.sum(axis=1); top=comp.nlargest(12,"score").sort_values("score")
    def _c(n):
        nl=n.lower()
        if any(w in nl for w in ["meat","beef","pork","chicken","lamb"]): return "#F472B6"
        if any(w in nl for w in ["fish","seafood","tuna"]): return "#38BDF8"
        if any(w in nl for w in ["cheese","egg","omelette"]): return "#FCD34D"
        return "#6EE7B7"
    fig=go.Figure(go.Bar(y=[_shorten(n,36) for n in top["food_name"]],x=top["score"].values,orientation="h",
        marker=dict(color=[_c(n) for n in top["food_name"]],line=dict(color="rgba(255,255,255,0.07)",width=0.5)),
        hovertemplate="<b>%{y}</b><br>Score: %{x:.1f}<extra></extra>"))
    fig.update_layout(**BASE,height=h or 400,bargap=0.3,
        title=dict(text="Most Nutrient-Dense Composite Dishes — meat & seafood win",font=dict(size=15,color="#F8FAFC")),
        xaxis=dict(title="Composite nutrient score",showgrid=True,gridcolor="rgba(255,255,255,0.06)",tickfont=dict(size=13)),
        yaxis=dict(showgrid=False,tickfont=dict(size=13)))
    return fig

def make_i6(h=None):
    liver_row=df[df["food_name"]=="Sheep liver"]
    if liver_row.empty: liver_row=df[df["food_name"].str.contains("liver",case=False,na=False)].head(1)
    if liver_row.empty: return _empty()
    all_avg=df[_avg_cols].replace(0,np.nan).mean(); liver_avg=liver_row[_avg_cols].replace(0,np.nan).iloc[0]
    maxes=pd.concat([all_avg,liver_avg],axis=1).max(axis=1).replace(0,1)
    def norm(s): return [(s.get(f"{n}_EU_avg",0) or 0)/(maxes.get(f"{n}_EU_avg",1) or 1)*100 for n in EU_ALL]
    theta=[EU_SHORT[n] for n in EU_ALL]+[EU_SHORT[EU_ALL[0]]]
    nl=norm(liver_avg)+[norm(liver_avg)[0]]; na=norm(all_avg)+[norm(all_avg)[0]]
    fig=go.Figure()
    fig.add_trace(go.Scatterpolar(r=nl,theta=theta,name="Sheep Liver",fill="toself",
        fillcolor="rgba(244,114,182,0.15)",line=dict(color="#F472B6",width=2.5),
        hovertemplate="%{theta}: %{r:.0f}%<extra>Sheep Liver</extra>"))
    fig.add_trace(go.Scatterpolar(r=na,theta=theta,name="EU Avg Food",fill="toself",
        fillcolor="rgba(148,163,184,0.07)",line=dict(color="#F8FAFC",width=1.5,dash="dot"),
        hovertemplate="%{theta}: %{r:.0f}%<extra>EU Average</extra>"))
    fig.update_layout(**{**BASE,"margin":dict(l=60,r=60,t=60,b=70)},height=h or 400,
        title=dict(text="Sheep Liver vs Average Food — all 16 nutrients (% of max)",font=dict(size=15,color="#F8FAFC")),
        polar=dict(bgcolor="rgba(0,0,0,0)",
            radialaxis=dict(visible=True,range=[0,100],showgrid=True,gridcolor="rgba(255,255,255,0.08)",showticklabels=False),
            angularaxis=dict(tickfont=dict(size=14,color="#F8FAFC"),gridcolor="rgba(255,255,255,0.08)")),
        legend=dict(orientation="h",y=-0.1,font=dict(size=10)))
    return fig

def make_i7(h=None):
    food,nut="Meat extract","Thiamine"; row=_row(food)
    if row is None: return _empty()
    data=sorted([(c,row.get(f"{nut}_{c}",np.nan)) for c in EU_COUNTRIES
                 if pd.notna(row.get(f"{nut}_{c}",np.nan)) and row.get(f"{nut}_{c}",0)>0],key=lambda x:x[1])
    countries,values=zip(*data)
    fig=go.Figure(go.Bar(y=[f"{EU_FLAGS[c]} {c}" for c in countries],x=list(values),orientation="h",
        marker=dict(color=[EU_COLORS[c] for c in countries],line=dict(color="rgba(255,255,255,0.07)",width=0.5)),
        text=[f"{v:.2f} mg" for v in values],textposition="auto",
        hovertemplate="%{y}: %{text} Thiamine/100g<extra></extra>"))
    fig.update_layout(**BASE,height=h or 300,bargap=0.3,
        title=dict(text="Thiamine in Meat Extract — UK 161× higher than Italy (log scale)",font=dict(size=15,color="#F8FAFC")),
        xaxis=dict(title="Thiamine (mg/100g) — log scale",type="log",showgrid=True,
                   gridcolor="rgba(255,255,255,0.06)",tickfont=dict(size=13)),
        yaxis=dict(showgrid=False,tickfont=dict(size=13)))
    return fig

def make_i8(h=None):
    food,nut="Yeast extract","Niacin Equivalent"; row=_row(food)
    if row is None: return _empty()
    data=sorted([(c,row.get(f"{nut}_{c}",np.nan)) for c in EU_COUNTRIES
                 if pd.notna(row.get(f"{nut}_{c}",np.nan)) and row.get(f"{nut}_{c}",0)>0],key=lambda x:-x[1])
    countries,values=zip(*data)
    fig=go.Figure(go.Bar(x=[f"{EU_FLAGS[c]} {c}" for c in countries],y=list(values),
        marker=dict(color=list(values),colorscale="Inferno",cmin=0,cmax=max(values),showscale=False,
                    line=dict(color="rgba(255,255,255,0.07)",width=0.5)),
        text=[f"{v:.0f}" for v in values],textposition="outside",textfont=dict(size=15,color="#F8FAFC"),
        hovertemplate="%{x}: %{y:.0f} mg Niacin/100g<extra></extra>"))
    fig.update_layout(**BASE,height=h or 320,bargap=0.35,
        title=dict(text="Niacin in Yeast Extract — Nordic 11× higher than France",font=dict(size=15,color="#F8FAFC")),
        yaxis=dict(title="Niacin Equivalent (mg/100g)",showgrid=True,gridcolor="rgba(255,255,255,0.06)",tickfont=dict(size=13)),
        xaxis=dict(showgrid=False,tickfont=dict(size=13)))
    return fig

def make_i9(h=None):
    fish=df[df["food_category"].str.contains("Fish|seafood",case=False,na=False)]
    vals={c: (lambda v: v.mean() if len(v)>0 else 0)(fish[f"Selenium_{c}"].replace(0,np.nan).dropna())
          for c in EU_COUNTRIES}
    data=sorted(vals.items(),key=lambda x:-x[1]); countries,values=zip(*data)
    fig=go.Figure(go.Bar(x=[f"{EU_FLAGS[c]} {c}" for c in countries],y=list(values),
        marker=dict(color=[EU_COLORS[c] for c in countries],line=dict(color="rgba(255,255,255,0.08)",width=0.5)),
        text=[f"{v:.1f} µg" for v in values],textposition="outside",textfont=dict(size=15,color="#F8FAFC"),
        hovertemplate="%{x}: %{y:.1f} µg Se/100g avg seafood<extra></extra>"))
    fig.update_layout(**BASE,height=h or 320,bargap=0.35,
        title=dict(text="Mean Selenium in Seafood by Country — Netherlands & UK lead",font=dict(size=15,color="#F8FAFC")),
        yaxis=dict(title="Mean Selenium (µg/100g)",showgrid=True,gridcolor="rgba(255,255,255,0.06)",tickfont=dict(size=13)),
        xaxis=dict(showgrid=False,tickfont=dict(size=13)))
    return fig

def make_i10(h=None):
    nuts=df[df["food_category"]=="Legumes, nuts, oilseeds and spices"].copy()
    nuts["_v"]=nuts["Vitamin E_EU_avg"].replace(0,np.nan)
    top=nuts.dropna(subset=["_v"]).nlargest(15,"_v").sort_values("_v")
    fig=go.Figure(go.Bar(y=[_shorten(n,36) for n in top["food_name"]],x=top["_v"].values,orientation="h",
        marker=dict(color=top["_v"].values,colorscale="YlOrRd",showscale=False,
                    line=dict(color="rgba(255,255,255,0.06)",width=0.5)),
        text=[f"{v:.1f} mg" for v in top["_v"]],textposition="auto",
        hovertemplate="<b>%{y}</b><br>%{text} Vit E/100g<extra></extra>"))
    fig.update_layout(**BASE,height=h or 420,bargap=0.28,
        title=dict(text="Vitamin E in Nuts & Seeds — Sunflower seeds dominate at 40 mg/100g",font=dict(size=15,color="#F8FAFC")),
        xaxis=dict(title="Vitamin E (mg/100g)",showgrid=True,gridcolor="rgba(255,255,255,0.06)",tickfont=dict(size=13)),
        yaxis=dict(showgrid=False,tickfont=dict(size=13)))
    return fig


# ── Pre-compute ────────────────────────────────────────────────────────────────
print("⚡ Pre-computing figures…")
fig_scoreboard           = make_scoreboard()
fig_leaders              = make_leaders()
fig_gaps                 = make_gaps()
fig_drinks_radar_main    = make_drinks_radar()
fig_drinks_compare_chart = make_drinks_compare()
fig_drinks_beer          = make_drinks_beer_country()
fig_drinks_radar         = make_drinks_wine_radar()
figs_insights    = [make_i1(),make_i2(),make_i3(),make_i4(),make_i5(),
                    make_i6(),make_i7(),make_i8(),make_i9(),make_i10()]
fig_top_foods = make_top_foods()
fig_rda = make_rda_chart()
print("✓ Done")

# Lookup for modal expansion
_FIGS = {
    "scoreboard":          (make_scoreboard,        {}),
    "leaders":             (make_leaders,           {}),
    "gaps":                (make_gaps,              {}),
    "top-foods":           (make_top_foods,         {}),
    "rda-chart":           (make_rda_chart,         {}),
    "drink-country-radar": (make_drinks_radar,      {}),
    "drink-compare":       (make_drinks_compare,    {}),
    "drink-beer":          (make_drinks_beer_country, {}),
    "drink-radar":         (make_drinks_wine_radar, {}),
    **{f"insight-{i}": (f, {}) for i,(f,_) in enumerate(
        [(make_i1,{}),(make_i2,{}),(make_i3,{}),(make_i4,{}),(make_i5,{}),
         (make_i6,{}),(make_i7,{}),(make_i8,{}),(make_i9,{}),(make_i10,{})]
    )}
}

# ── App ────────────────────────────────────────────────────────────────────────
app = Dash(__name__, suppress_callback_exceptions=True)
app.title = "EU Micronutrient Atlas"

@app.server.route("/videos/<path:filename>")
def serve_video(filename):
    return send_from_directory(VIDEO_DIR, filename)

# ── Layout helpers ─────────────────────────────────────────────────────────────
def _graph(gid, fig, style=None):
    return dcc.Graph(id=gid, figure=fig, config=CFG, style=style or {})

def _expand_btn(chart_id):
    return html.Button("⛶", id={"type":"expand-btn","index":chart_id},
                       n_clicks=0, className="expand-btn", title="Expand to fullscreen")

def _card(children, chart_id=None, cls="", style=None, clickable=True):
    inner = list(children) if isinstance(children,list) else [children]
    kw = {}
    if chart_id:
        if clickable:
            # Whole card is the click target — no expand button needed
            kw = {"id": {"type":"expand-card","index":chart_id}, "n_clicks": 0}
        else:
            # Interactive card (has controls) — keep explicit expand button
            inner = [_expand_btn(chart_id)] + inner
    return html.Div(className=f"glass card-wrap {cls}", style=style or {}, children=inner, **kw)

INSIGHT_META = [
    ("#6EE7B7","Sweden's salt has 12.5× more calcium",
     "Flavoured salt in Sweden hits 3,180 mg calcium/100g — same product, drastically different formulation."),
    ("#38BDF8","Oyster zinc varies 7× across countries",
     "Netherlands/UK oysters (59 mg) vs Finnish oysters (8 mg) — likely a real ecological difference."),
    ("#F97316","Selenium in tuna: France vs Finland",
     "France reports 116 µg/100g vs Finland's 36 µg — different tuna species and fishing regions."),
    ("#FCD34D","Cocoa magnesium: Germany 4.8× France",
     "German cocoa powder reaches 545 mg Mg/100g. French cocoa (114 mg) is likely more processed."),
    ("#818CF8","Healthiest 'fast food' is meat-based",
     "Composite dishes ranked by 16-nutrient score — pork loaf, beef loaf, and seafood salad lead."),
    ("#F472B6","Liver is the most nutrient-dense food",
     "Sheep liver dominates the spider chart on every axis — B12, Iron, Selenium, Riboflavin and more."),
    ("#A78BFA","UK meat extract: 161× more thiamine",
     "UK Marmite-style extracts report 9.7 mg vs Italy's 0.06 mg — log scale required to visualise."),
    ("#34D399","Nordic yeast extract: 11× more niacin",
     "Finland & Sweden record 103 mg niacin/100g in yeast extract vs France's 8.96 mg."),
    ("#FB923C","Netherlands & UK lead selenium in seafood",
     "Mean seafood selenium across hundreds of fish items is consistently highest in NL and UK."),
    ("#FBBF24","Sunflower seeds crush almonds for Vitamin E",
     "40 mg/100g EU average — 1.6× more than almonds, 3× more than hazelnuts."),
]


app.layout = html.Div([

    # ── Expand store + modal ──────────────────────────────────────────────────
    dcc.Store(id="expand-store"),
    html.Div(id="modal-overlay", className="modal-overlay", n_clicks=0, children=[
        html.Div(className="modal-inner", n_clicks=0, children=[
            html.Div(className="modal-header", children=[
                html.P(id="modal-title", className="modal-title-text"),
                html.Button("✕", id="modal-close", n_clicks=0, className="close-btn"),
            ]),
            dcc.Graph(id="modal-graph", config=CFG,
                      style={"height":"82vh","width":"100%"}),
        ]),
    ]),

    # ── Video background ──────────────────────────────────────────────────────
    html.Div(id="video-bg", children=[
        html.Video(id="vid-0", src="/videos/5865597-uhd_3840_2160_25fps.mp4",
                   autoPlay=True, loop=True, muted=True, playsInline=True,
                   style={"opacity":"1"}),
        html.Video(id="vid-1", src="/videos/13153799_3840_2160_30fps.mp4",
                   autoPlay=False, loop=True, muted=True, playsInline=True,
                   style={"opacity":"0"}),
        html.Video(id="vid-2", src="/videos/5865398-uhd_3840_2160_25fps.mp4",
                   autoPlay=False, loop=True, muted=True, playsInline=True,
                   style={"opacity":"0"}),
        html.Div(className="video-overlay"),
    ]),

    # ── Hero ──────────────────────────────────────────────────────────────────
    html.Div(id="hero", children=[
        html.Div(className="hero-eyebrow", children="EFSA Food Composition Database"),
        html.H1("EU Micronutrient Atlas", className="hero-title"),
        html.P("Explore how 16 vitamins and minerals vary across 7 European countries "
               "and 2,500+ foods — ranked, compared, and drilled down.",
               className="hero-subtitle"),
        html.Div(className="chips-row", children=[
            html.Div(className="chip", children=[html.Span(f"{FOODS_COUNT:,}", className="chip-number",
                style={"color":"#6EE7B7"}), html.Span("Foods",className="chip-label")]),
            html.Div(className="chip", children=[html.Span("16",className="chip-number",
                style={"color":"#818CF8"}), html.Span("Nutrients",className="chip-label")]),
            html.Div(className="chip", children=[html.Span("7",className="chip-number",
                style={"color":"#F472B6"}), html.Span("Countries",className="chip-label")]),
            html.Div(className="chip", children=[html.Span("21",className="chip-number",
                style={"color":"#FCD34D"}), html.Span("Categories",className="chip-label")]),
        ]),
        html.Button("⏸ Freeze Video", id="video-freeze-btn", n_clicks=0, className="video-freeze-btn"),
        html.Div("↓", className="scroll-arrow"),
    ]),

    # ── Section 1: Food Fingerprint ───────────────────────────────────────────
    html.Section(className="section reveal", children=[
        html.H2("Food Fingerprint — Foods Are Unique!", className="section-header"),
        html.P("Every food has a nutrient fingerprint. Toggle views, select a category, or search a specific food to compare across countries.",
               className="section-desc"),

        _card(chart_id="hm-chart", cls="heatmap-panel", clickable=False, children=[
            html.Div(className="heatmap-controls", children=[
                html.Div(className="ctrl-group", children=[
                    html.Span("View", className="ctrl-label"),
                    dcc.RadioItems(id="hm-view", value="food",
                        options=[{"label":"By Food","value":"food"},
                                 {"label":"By Country","value":"country"},
                                 {"label":"Single Food","value":"single_food"}],
                        inline=True, className="nutrient-pills", inputStyle={"display":"none"}),
                ]),
                html.Div(id="hm-cat-wrap", className="ctrl-group", style={"flex":"1","minWidth":"260px"}, children=[
                    html.Span("Category", className="ctrl-label"),
                    dcc.Dropdown(id="hm-category", options=[{"label":c,"value":c} for c in CATEGORIES],
                        value="Meat and meat products", clearable=False, searchable=False, className="hm-dropdown"),
                ]),
                html.Div(className="ctrl-group", children=[
                    html.Span("Nutrients", className="ctrl-label"),
                    dcc.RadioItems(id="hm-group", value="all",
                        options=[{"label":"All","value":"all"},
                                 {"label":"Vitamins","value":"vitamins"},
                                 {"label":"Minerals","value":"minerals"}],
                        inline=True, className="nutrient-pills", inputStyle={"display":"none"}),
                ]),
                html.Div(className="ctrl-group", children=[
                    html.Span("Scale", className="ctrl-label"),
                    dcc.RadioItems(id="hm-scale", value="zscore",
                        options=[{"label":"Z-score","value":"zscore"},
                                 {"label":"% of RDA","value":"rda"},
                                 {"label":"Actual Values","value":"values"}],
                        inline=True, className="nutrient-pills", inputStyle={"display":"none"}),
                ]),
            ]),

            html.Div(id="hm-food-controls", style={"display":"none"}, children=[
                html.Div(className="heatmap-controls", style={"paddingTop":"0","borderTop":"none"}, children=[
                    html.Div(className="ctrl-group", style={"flex":"2"}, children=[
                        html.Span("Search Food", className="ctrl-label"),
                        dcc.Dropdown(id="hm-food-search",
                            options=[{"label":n,"value":n} for n in FOOD_NAMES],
                            value="Chicken liver", searchable=True,
                            placeholder="Type to search food…", className="hm-dropdown food-search-dd"),
                    ]),
                    html.Div(className="ctrl-group", style={"flex":"3"}, children=[
                        html.Span("Countries to compare", className="ctrl-label"),
                        dcc.Checklist(id="hm-food-countries",
                            options=[{"label":f"{EU_FLAGS[c]} {c}","value":c} for c in EU_COUNTRIES],
                            value=EU_COUNTRIES,
                            className="nutrient-pills", inputStyle={"display":"none"}),
                    ]),
                ]),
            ]),

            dcc.Loading(type="dot", color="#818CF8", children=[
                _graph("hm-chart", make_heatmap()),
            ]),

            html.Div(id="hm-diff-wrap", style={"display":"none","marginTop":"20px"}, children=[
                html.Div(style={"marginBottom":"12px","paddingBottom":"12px",
                                "borderBottom":"1px solid rgba(255,255,255,0.08)",
                                "display":"flex","alignItems":"center","gap":"16px","flexWrap":"wrap"}, children=[
                    html.Span("Difference chart — % of daily RDA per 100g",
                              style={"color":"#94A3B8","fontSize":"0.8rem",
                                     "textTransform":"uppercase","letterSpacing":"0.1em","flex":"1"}),
                    dcc.RadioItems(id="hm-diff-scale", value="log",
                        options=[{"label":"Linear","value":"linear"},
                                 {"label":"Log scale","value":"log"}],
                        inline=True, className="nutrient-pills", inputStyle={"display":"none"}),
                ]),
                dcc.Loading(type="dot", color="#6EE7B7", children=[
                    dcc.Graph(id="hm-diff-chart", config=CFG),
                ]),
            ]),

            html.Div(id="hm-drill-wrap", style={"display":"none","marginTop":"20px"}, children=[
                html.Div(style={"display":"flex","alignItems":"center",
                                "justifyContent":"space-between","marginBottom":"12px"}, children=[
                    html.P(id="hm-drill-title",
                           style={"color":"#818CF8","fontWeight":600,"margin":0,"fontSize":"0.9rem"}),
                    html.Button("✕ Close", id="hm-drill-close", n_clicks=0, className="close-btn"),
                ]),
                dcc.Graph(id="hm-drill-chart", config=CFG),
            ]),
        ]),
    ]),

    # ── Section 2: Overview ───────────────────────────────────────────────────
    html.Section(className="section reveal", children=[
        html.H2("National Overview", className="section-header"),
        html.P("Which country leads which nutrient? Which foods pack the most? "
               "Where are the biggest data gaps?", className="section-desc"),
        _card([_graph("scoreboard", fig_scoreboard)], chart_id="scoreboard",
              cls="reveal", style={"marginBottom":"24px"}),
        html.Div(className="charts-row reveal", children=[
            _card([_graph("leaders", fig_leaders)], chart_id="leaders"),
            _card([_graph("gaps", fig_gaps)], chart_id="gaps"),
        ]),
    ]),

    # ── Section 3: Top N Foods Rich in X ─────────────────────────────────────
    html.Section(className="section", children=[
        html.H2("Top Foods Rich in a Nutrient", className="section-header reveal"),
        html.P("Find the highest natural sources of any micronutrient — filter by country or EU average.", className="section-desc reveal"),
        html.Div(className="glass card-wrap heatmap-panel reveal", style={"marginBottom":"0"}, children=[
            html.Div(className="heatmap-controls", children=[
                html.Div(className="ctrl-group", children=[
                    html.Span("Nutrient", className="ctrl-label"),
                    dcc.Dropdown(id="tf-nutrient",
                        options=[{"label":n,"value":n} for n in EU_ALL],
                        value="Selenium", clearable=False, searchable=False, className="hm-dropdown"),
                ]),
                html.Div(className="ctrl-group", children=[
                    html.Span("Top N", className="ctrl-label"),
                    dcc.Dropdown(id="tf-topn",
                        options=[{"label":str(n),"value":n} for n in [5,10,15,20,25,30]],
                        value=10, clearable=False, searchable=False, className="hm-dropdown"),
                ]),
                html.Div(className="ctrl-group", children=[
                    html.Span("Country / Source", className="ctrl-label"),
                    dcc.Dropdown(id="tf-country",
                        options=[{"label":"🌍 EU Average","value":"EU_avg"}] +
                                [{"label":f"{EU_FLAGS[c]} {c}","value":c} for c in EU_COUNTRIES],
                        value="EU_avg", clearable=False, searchable=False, className="hm-dropdown"),
                ]),
            ]),
            dcc.Loading(type="dot", color="#818CF8", children=[
                dcc.Graph(id="top-foods-chart", figure=fig_top_foods, config=CFG),
            ]),
        ]),
    ]),

    # ── Section 4: Key Insights carousel ─────────────────────────────────────
    html.Section(className="section", children=[
        html.H2("10 Key Insights", className="section-header reveal"),
        html.P("The most striking patterns in the EFSA data — country anomalies, "
               "nutrient champions, and surprising gaps.", className="section-desc reveal"),
        html.Div(className="carousel-wrap reveal", children=[
            html.Button("‹", id="carousel-prev", className="carousel-arrow carousel-arrow-prev"),
            html.Div(id="insight-carousel", className="insight-carousel", children=[
                html.Div(
                    id={"type":"expand-card","index":f"insight-{i}"},
                    n_clicks=0,
                    className="glass insight-card card-wrap",
                    style={"borderTop":f"3px solid {INSIGHT_META[i][0]}"},
                    children=[
                        html.Div(style={"display":"flex","alignItems":"center","marginBottom":"8px"}, children=[
                            html.Span(f"{i+1:02d}", className="insight-num",
                                      style={"background":_rgba(INSIGHT_META[i][0],0.15),
                                             "color":INSIGHT_META[i][0]}),
                            html.Span(INSIGHT_META[i][1], className="insight-title"),
                        ]),
                        html.P(INSIGHT_META[i][2], className="insight-desc"),
                        _graph(f"insight-{i}", figs_insights[i]),
                    ]) for i in range(10)
            ]),
            html.Button("›", id="carousel-next", className="carousel-arrow carousel-arrow-next"),
        ]),
    ]),

    # ── Section 5: RDA Provocative Chart ─────────────────────────────────────
    html.Section(className="section", children=[
        html.H2("How Much Would You Need To Eat?", className="section-header reveal"),
        html.P("To hit your daily RDA from a single food — the country you're in can change everything. RDA values adjust automatically for your age, sex, and body stats.", className="section-desc reveal"),
        html.Div(className="glass card-wrap heatmap-panel reveal", children=[
            html.Div(className="heatmap-controls", children=[
                html.Div(className="ctrl-group", style={"flex":"2"}, children=[
                    html.Span("Food", className="ctrl-label"),
                    dcc.Dropdown(id="rda-food",
                        options=[{"label":n,"value":n} for n in FOOD_NAMES],
                        value="Tuna and bonito (generic)", searchable=True,
                        clearable=False, className="hm-dropdown food-search-dd"),
                ]),
                html.Div(className="ctrl-group", children=[
                    html.Span("Nutrient", className="ctrl-label"),
                    dcc.Dropdown(id="rda-nutrient",
                        options=[{"label":n,"value":n} for n in EU_ALL],
                        value="Selenium", clearable=False, searchable=False, className="hm-dropdown"),
                ]),
            ]),
            html.Div(className="heatmap-controls", style={"paddingTop":"0","borderTop":"none"}, children=[
                html.Div(className="ctrl-group", children=[
                    html.Span("Age Group", className="ctrl-label"),
                    dcc.Dropdown(id="rda-age",
                        options=[{"label":"18–64 (adult)","value":"18-64"},
                                 {"label":"65+ (elder)","value":"65+"}],
                        value="18-64", clearable=False, searchable=False, className="hm-dropdown",
                        style={"minWidth":"160px"}),
                ]),
                html.Div(className="ctrl-group", children=[
                    html.Span("Sex", className="ctrl-label"),
                    dcc.RadioItems(id="rda-sex", value="male",
                        options=[{"label":"Male","value":"male"},
                                 {"label":"Female","value":"female"}],
                        inline=True, className="nutrient-pills",
                        inputStyle={"display":"none"}),
                ]),
                html.Div(className="ctrl-group", children=[
                    html.Span("Weight (kg)", className="ctrl-label"),
                    dcc.Input(id="rda-weight", type="number", value=70,
                        min=30, max=200, step=1,
                        style={"width":"80px","background":"rgba(255,255,255,0.06)",
                               "border":"1px solid rgba(255,255,255,0.1)",
                               "borderRadius":"8px","color":"#F8FAFC",
                               "fontFamily":"Inter,sans-serif",
                               "fontSize":"0.9rem","padding":"6px 10px"}),
                ]),
                html.Div(className="ctrl-group", children=[
                    html.Span("Height (cm)", className="ctrl-label"),
                    dcc.Input(id="rda-height", type="number", value=175,
                        min=100, max=250, step=1,
                        style={"width":"80px","background":"rgba(255,255,255,0.06)",
                               "border":"1px solid rgba(255,255,255,0.1)",
                               "borderRadius":"8px","color":"#F8FAFC",
                               "fontFamily":"Inter,sans-serif",
                               "fontSize":"0.9rem","padding":"6px 10px"}),
                ]),
            ]),
            dcc.Loading(type="dot", color="#F472B6", children=[
                dcc.Graph(id="rda-chart", figure=fig_rda, config=CFG),
            ]),
        ]),
    ]),

    # ── Section 6: Drinks & Alcohol ───────────────────────────────────────────
    html.Section(className="section", children=[
        html.H2("Drinks & Alcohol", className="section-header reveal"),
        html.P("Select any alcoholic beverage to explore its full nutrient radar. Overlay countries in contrasting colours, or compare multiple drinks side by side.", className="section-desc reveal"),

        # ── Per-drink country radar ───────────────────────────────────────────
        _card(chart_id="drink-country-radar", cls="heatmap-panel reveal", clickable=False, children=[
            html.Div(className="heatmap-controls", children=[
                html.Div(className="ctrl-group", style={"flex":"3"}, children=[
                    html.Span("Drink", className="ctrl-label"),
                    dcc.Dropdown(id="drink-sel",
                        options=[{"label":n,"value":n} for n in DRINK_NAMES],
                        value="Beer, regular", clearable=False, searchable=False,
                        className="hm-dropdown"),
                ]),
                html.Div(className="ctrl-group", children=[
                    html.Span("Nutrients", className="ctrl-label"),
                    dcc.RadioItems(id="drink-nutr-group", value="all",
                        options=[{"label":"All","value":"all"},
                                 {"label":"Vitamins","value":"vitamins"},
                                 {"label":"Minerals","value":"minerals"}],
                        inline=True, className="nutrient-pills", inputStyle={"display":"none"}),
                ]),
            ]),
            html.Div(className="heatmap-controls", style={"paddingTop":"0","borderTop":"none"}, children=[
                html.Div(className="ctrl-group", children=[
                    html.Span("Compare countries", className="ctrl-label"),
                    dcc.Checklist(id="drink-countries",
                        options=[{"label":"🌍 EU Avg","value":"EU_avg"}] +
                                [{"label":f"{EU_FLAGS[c]} {c}","value":c} for c in EU_COUNTRIES],
                        value=["EU_avg"],
                        className="nutrient-pills", inputStyle={"display":"none"}),
                ]),
            ]),
            dcc.Loading(type="dot", color="#C084FC", children=[
                dcc.Graph(id="drink-country-radar-chart",
                          figure=fig_drinks_radar_main, config=CFG),
            ]),
        ]),

        # ── Compare row ───────────────────────────────────────────────────────
        html.Div(className="charts-row reveal", children=[
            _card(chart_id="drink-compare", cls="heatmap-panel", clickable=False, children=[
                html.Div(className="heatmap-controls", children=[
                    html.Div(className="ctrl-group", style={"flex":"1"}, children=[
                        html.Span("Compare drinks (up to 7)", className="ctrl-label"),
                        dcc.Dropdown(id="drinks-compare-sel",
                            options=[{"label":n,"value":n} for n in DRINK_NAMES],
                            value=_DEFAULT_COMPARE_DRINKS,
                            multi=True, clearable=True, searchable=False,
                            className="hm-dropdown"),
                    ]),
                    html.Div(className="ctrl-group", children=[
                        html.Span("Nutrients", className="ctrl-label"),
                        dcc.RadioItems(id="drink-compare-nutr-group", value="all",
                            options=[{"label":"All","value":"all"},
                                     {"label":"Vitamins","value":"vitamins"},
                                     {"label":"Minerals","value":"minerals"}],
                            inline=True, className="nutrient-pills", inputStyle={"display":"none"}),
                    ]),
                ]),
                dcc.Loading(type="dot", color="#FCD34D", children=[
                    dcc.Graph(id="drink-compare-chart",
                              figure=fig_drinks_compare_chart, config=CFG),
                ]),
            ]),
            _card([_graph("drink-radar", fig_drinks_radar)], chart_id="drink-radar"),
        ]),
        _card([_graph("drink-beer", fig_drinks_beer)], chart_id="drink-beer",
              cls="reveal", style={"marginTop":"24px"}),
    ]),

    # ── Collapsible info/about bottom banner ──────────────────────────────────
    html.Div(className="info-banner-wrap", children=[
        # Expandable panel (hidden by default)
        html.Div(id="info-panel", className="info-panel", style={"display":"none"}, children=[
            html.Div(className="info-grid", children=[
                html.Div(className="info-card glass", children=[
                    html.Div(className="info-card-icon", children="📊"),
                    html.H3("Data Source", className="info-card-title"),
                    html.P("All nutrient values come from the EFSA (European Food Safety Authority) "
                           "Food Composition Database — a harmonised, peer-reviewed dataset covering "
                           "7 EU member states, 2,500+ foods, and 16 micronutrients measured per 100g. "
                           "Values represent means reported by national food composition databases.", className="info-card-body"),
                ]),
                html.Div(className="info-card glass", children=[
                    html.Div(className="info-card-icon", children="📐"),
                    html.H3("Z-Score", className="info-card-title"),
                    html.P("Measures how many standard deviations a value sits above or below the mean "
                           "of that nutrient column. Score 0 = average; +2 = exceptionally high; −2 = very low. "
                           "Used in heatmaps and composite rankings. Lets you compare nutrients with different "
                           "units (µg of B12 vs mg of Potassium) on a single scale.", className="info-card-body"),
                ]),
                html.Div(className="info-card glass", children=[
                    html.Div(className="info-card-icon", children="🎨"),
                    html.H3("% of Max", className="info-card-title"),
                    html.P("Each nutrient column is normalised independently: 100% = the highest observed value "
                           "in that column. Useful for within-nutrient ranking. The colour shows relative richness "
                           "per nutrient. Unlike z-score, extreme outliers are not penalised.", className="info-card-body"),
                ]),
                html.Div(className="info-card glass", children=[
                    html.Div(className="info-card-icon", children="🔢"),
                    html.H3("Actual Values", className="info-card-title"),
                    html.P("Shows raw measured quantities (µg or mg per 100g) in each heatmap cell. "
                           "Cell colour still uses per-nutrient % of max so each nutrient column is "
                           "independently shaded — necessary because nutrients span vastly different scales.", className="info-card-body"),
                ]),
                html.Div(className="info-card glass", children=[
                    html.Div(className="info-card-icon", children="🏆"),
                    html.H3("Composite Score", className="info-card-title"),
                    html.P("The sum of z-scores across all 16 nutrients. Foods ranked by this score tend "
                           "to be organ meats, shellfish, and fermented concentrates. It is not a "
                           "calorie-adjusted measure.", className="info-card-body"),
                ]),
                html.Div(className="info-card glass", children=[
                    html.Div(className="info-card-icon", children="🎯"),
                    html.H3("RDA", className="info-card-title"),
                    html.P("Recommended Daily Allowance — the daily intake level considered sufficient "
                           "for 97.5% of healthy individuals. EFSA values are used, adjusted for age group "
                           "and sex. The 'grams needed' chart shows how much of a food you'd eat per day "
                           "to meet your RDA from that source alone.", className="info-card-body"),
                ]),
            ]),
        ]),

        # Sticky bottom bar
        html.Div(className="info-banner-bar", children=[
            html.Div(className="info-banner-left", children=[
                html.Span("EU Micronutrient Atlas", className="footer-title"),
                html.Span("Data: EFSA Food Composition Database — 7 EU countries, 2,504 foods, 16 micronutrients.",
                          className="footer-sub"),
            ]),
            html.Div(className="info-banner-right", children=[
                html.A("EFSA Data Portal",
                       href="https://www.efsa.europa.eu/en/microstrategy/food-composition-data",
                       target="_blank", className="footer-link"),
                html.A("FoodEx2 Classification",
                       href="https://www.efsa.europa.eu/en/data/data-standards",
                       target="_blank", className="footer-link"),
                html.Button("▲ About & Methodology", id="info-toggle-btn", n_clicks=0,
                            className="info-toggle-btn"),
            ]),
        ]),
    ]),
])


# ── Callbacks ─────────────────────────────────────────────────────────────────

@app.callback(
    Output("hm-chart",      "figure"),
    Output("hm-diff-wrap",  "style"),
    Output("hm-diff-chart", "figure"),
    Input("hm-view",           "value"),
    Input("hm-category",       "value"),
    Input("hm-group",          "value"),
    Input("hm-food-search",    "value"),
    Input("hm-food-countries", "value"),
    Input("hm-scale",          "value"),
    Input("hm-diff-scale",     "value"),
)
def update_heatmap(view, category, group, food, countries, scale, diff_scale):
    diff_hidden = {"display":"none","marginTop":"20px"}
    diff_show   = {"display":"block","marginTop":"20px"}
    scale = scale or "zscore"
    if view == "single_food":
        food     = food or "Chicken liver"
        clist    = countries or EU_COUNTRIES
        hm_fig   = make_single_food_heatmap(food, clist, group or "all", scale)
        diff_fig = make_food_diff_chart(food, clist, group or "all", log_scale=(diff_scale == "log"))
        return hm_fig, diff_show, diff_fig
    hm_fig = make_heatmap(view or "food", category or "Meat and meat products", group or "all", scale)
    return hm_fig, diff_hidden, _empty(h=40)


@app.callback(
    Output("hm-cat-wrap",      "style"),
    Output("hm-food-controls", "style"),
    Input("hm-view", "value"),
)
def toggle_hm_controls(view):
    show_cat  = {"flex":"1","minWidth":"260px"}
    hide_cat  = {"flex":"1","minWidth":"260px","opacity":"0.3","pointerEvents":"none"}
    show_food = {"display":"block","marginBottom":"16px","paddingBottom":"16px",
                 "borderBottom":"1px solid rgba(255,255,255,0.08)"}
    hide_food = {"display":"none"}
    if view == "single_food":
        return hide_cat, show_food
    elif view == "country":
        return show_cat, hide_food
    return show_cat, hide_food


@app.callback(
    Output("hm-drill-wrap",  "style"),
    Output("hm-drill-chart", "figure"),
    Output("hm-drill-title", "children"),
    Input("hm-chart",        "clickData"),
    Input("hm-drill-close",  "n_clicks"),
    State("hm-view",         "value"),
    prevent_initial_call=True,
)
def heatmap_drilldown(click_data, _close, view):
    hidden  = {"display":"none","marginTop":"20px"}
    visible = {"display":"block","marginTop":"20px"}
    if ctx.triggered_id == "hm-drill-close" or not click_data:
        return hidden, _empty(), ""
    try:
        pt = click_data["points"][0]
        x_val = pt.get("x","")
        y_val = pt.get("y","")
        y_clean = y_val
        for c in EU_COUNTRIES:
            if c in y_val: y_clean=c; break
        title = f"Drill-down → {x_val} in '{y_clean}'"
        fig   = make_drilldown(y_clean, x_val, view or "food")
        return visible, fig, title
    except Exception:
        return hidden, _empty(), ""


@app.callback(
    Output("expand-store", "data"),
    Input({"type":"expand-btn", "index":ALL}, "n_clicks"),
    Input({"type":"expand-card","index":ALL}, "n_clicks"),
    State("hm-view",           "value"),
    State("hm-category",       "value"),
    State("hm-group",          "value"),
    State("hm-food-search",    "value"),
    State("hm-food-countries", "value"),
    prevent_initial_call=True,
)
def set_expand(btn_clicks, card_clicks, view, cat, grp, food, countries):
    all_clicks = (btn_clicks or []) + (card_clicks or [])
    if not any(n for n in all_clicks if n):
        return None
    triggered = ctx.triggered_id
    if not triggered: return None
    return {"id": triggered["index"], "view":view, "cat":cat, "grp":grp,
            "food":food, "countries":countries}


@app.callback(
    Output("modal-overlay", "className"),
    Output("modal-graph",   "figure"),
    Output("modal-title",   "children"),
    Input("expand-store",   "data"),
    Input("modal-close",    "n_clicks"),
    Input("modal-overlay",  "n_clicks"),
    prevent_initial_call=True,
)
def render_modal(data, _close, _bg_click):
    closed = "modal-overlay"
    opened = "modal-overlay modal-open"
    H = 820
    if ctx.triggered_id in ("modal-close", "modal-overlay") or not data:
        return closed, _empty(), ""
    cid = data.get("id","")
    title = cid.replace("-"," ").replace("insight","Insight").title()

    # Heatmap chart
    if cid == "hm-chart":
        view = data.get("view","food")
        if view == "single_food":
            food     = data.get("food") or "Chicken liver"
            countries= data.get("countries") or EU_COUNTRIES
            fig = make_single_food_heatmap(food, countries, data.get("grp","all"), h=H)
            title = f"Single Food: {food}"
        else:
            fig = make_heatmap(view, data.get("cat","Meat and meat products"),
                               data.get("grp","all"), h=H)
        return opened, fig, title

    # Static figures — look up factory and call with full height
    if cid in _FIGS:
        factory, _ = _FIGS[cid]
        fig = factory(h=H)
        return opened, fig, title

    return closed, _empty(), ""


@app.callback(
    Output("top-foods-chart", "figure"),
    Input("tf-nutrient", "value"),
    Input("tf-topn",     "value"),
    Input("tf-country",  "value"),
)
def update_top_foods(nutrient, top_n, country):
    return make_top_foods(nutrient or "Selenium", top_n or 10, country or "EU_avg")


@app.callback(
    Output("rda-chart", "figure"),
    Input("rda-food",     "value"),
    Input("rda-nutrient", "value"),
    Input("rda-age",      "value"),
    Input("rda-sex",      "value"),
    Input("rda-weight",   "value"),
    Input("rda-height",   "value"),
)
def update_rda_chart(food, nutrient, age_group, sex, weight, height):
    return make_rda_chart(
        food or "Tuna and bonito (generic)",
        nutrient or "Selenium",
        age_group or "18-64",
        sex or "male",
        int(weight) if weight else 70,
        int(height) if height else 175,
    )


@app.callback(
    Output("drink-country-radar-chart", "figure"),
    Input("drink-sel",        "value"),
    Input("drink-countries",  "value"),
    Input("drink-nutr-group", "value"),
)
def update_drink_radar(drink, countries, nutr_group):
    return make_drinks_radar(
        drink or "Beer, regular",
        countries or ["EU_avg"],
        nutr_group or "all",
    )


@app.callback(
    Output("drink-compare-chart", "figure"),
    Input("drinks-compare-sel",       "value"),
    Input("drink-compare-nutr-group", "value"),
)
def update_drinks_compare(drink_names, nutr_group):
    return make_drinks_compare(drink_names or _DEFAULT_COMPARE_DRINKS, nutr_group or "all")


app.clientside_callback(
    """
    function(n) {
        var videos = document.querySelectorAll('#video-bg video');
        if (n % 2 === 1) {
            videos.forEach(function(v) { v.pause(); });
            return '▶ Play Video';
        } else {
            videos.forEach(function(v) { if (v.style.opacity === '1') v.play(); });
            return '⏸ Freeze Video';
        }
    }
    """,
    Output("video-freeze-btn", "children"),
    Input("video-freeze-btn", "n_clicks"),
    prevent_initial_call=True,
)

app.clientside_callback(
    """
    function(n) {
        var panel = document.getElementById('info-panel');
        var btn   = document.getElementById('info-toggle-btn');
        if (!panel) return window.dash_clientside.no_update;
        var opening = n % 2 === 1;
        panel.style.display = opening ? 'block' : 'none';
        return opening ? '▼ About & Methodology' : '▲ About & Methodology';
    }
    """,
    Output("info-toggle-btn", "children"),
    Input("info-toggle-btn", "n_clicks"),
    prevent_initial_call=True,
)


if __name__ == "__main__":
    import threading, webbrowser
    threading.Timer(1.5, lambda: webbrowser.open("http://127.0.0.1:8050")).start()
    app.run(debug=True, port=8050)
