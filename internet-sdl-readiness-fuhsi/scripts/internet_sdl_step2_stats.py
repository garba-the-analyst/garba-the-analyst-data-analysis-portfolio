"""Internet Access & SDL Readiness Study — Phase 2: Statistics."""
import warnings
import os
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.stats import spearmanr, pearsonr, kruskal, mannwhitneyu, chi2_contingency

warnings.filterwarnings("ignore")

BASE = Path("/home/garba-the-analyst/Desktop/Projects/Data analysis ")
os.chdir(BASE)

CLEAN = BASE / "data" / "processed" / "internet_sdl_cleaned.csv"
TAB_DIR = BASE / "reports" / "output" / "tables"
TAB_DIR.mkdir(parents=True, exist_ok=True)

df = pd.read_csv(CLEAN)
N = len(df)

# ---- Helper: freq table ----
def freq_table(series, order=None):
    vc = series.value_counts()
    if order:
        vc = vc.reindex([o for o in order if o in vc.index])
    t = pd.DataFrame({"category": vc.index, "n": vc.values})
    t["pct"] = (t["n"] / len(series) * 100).round(1)
    return t

# ---- T01 Demographics ----
rows = []
for var, label, order in [
    ("age_num", "Age (years)", None),
    ("sex_c", "Sex", ["Male", "Female"]),
    ("level_c", "Academic Level", ["100 level", "200 level", "300 level", "400 level"]),
    ("dept_c", "Department", None),
]:
    if var == "age_num":
        rows.append({"variable": label, "category": "Mean ± SD",
                     "n": f"{df[var].mean():.1f} ± {df[var].std():.1f}", "pct": ""})
        rows.append({"variable": label, "category": "Median (IQR)",
                     "n": f"{df[var].median():.1f} ({df[var].quantile(0.25):.1f}-{df[var].quantile(0.75):.1f})", "pct": ""})
    else:
        t = freq_table(df[var], order)
        for _, r in t.iterrows():
            rows.append({"variable": label, "category": r["category"], "n": int(r["n"]), "pct": r["pct"]})

t01 = pd.DataFrame(rows)
t01.to_csv(TAB_DIR / "T01_demographics.csv", index=False)

# ---- T02 Internet Access ----
rows = []
t = freq_table(df["device_c"])
for _, r in t.iterrows():
    rows.append({"item": "Device ownership", "category": r["category"], "n": int(r["n"]), "pct": r["pct"]})
t = freq_table(df["freq_c"], ["Daily", "Several times a week", "Once a week", "Rarely", "Never"])
for _, r in t.iterrows():
    rows.append({"item": "Frequency of access", "category": r["category"], "n": int(r["n"]), "pct": r["pct"]})
t = freq_table(df["means_c"])
for _, r in t.iterrows():
    rows.append({"item": "Primary means of access", "category": r["category"], "n": int(r["n"]), "pct": r["pct"]})
t = freq_table(df["reliability_c"], ["Very reliable (connects consistently without interruption)",
                                      "Fairly reliable (occasional interruptions)",
                                      "Unreliable (frequent disconnections)",
                                      "Very unreliable (rarely connects when needed)"])
for _, r in t.iterrows():
    rows.append({"item": "Connection reliability", "category": r["category"], "n": int(r["n"]), "pct": r["pct"]})
t = freq_table(df["hours_c"], ["More than 4 hours", "3 to 4 hours", "1 to 2 hours", "Less than 1 hour"])
for _, r in t.iterrows():
    rows.append({"item": "Hours per day (academic)", "category": r["category"], "n": int(r["n"]), "pct": r["pct"]})
t = freq_table(df["satisfaction_c"], ["Very satisfied", "Satisfied", "Neutral", "Dissatisfied", "Very dissatisfied"])
for _, r in t.iterrows():
    rows.append({"item": "Satisfaction with access", "category": r["category"], "n": int(r["n"]), "pct": r["pct"]})

# IA Score summary
rows.append({"item": "IA Composite Score", "category": "Mean ± SD",
             "n": f"{df['ia_score'].mean():.2f} ± {df['ia_score'].std():.2f}", "pct": ""})
rows.append({"item": "IA Composite Score", "category": "Median (IQR)",
             "n": f"{df['ia_score'].median():.2f} ({df['ia_score'].quantile(0.25):.2f}-{df['ia_score'].quantile(0.75):.2f})", "pct": ""})

t02 = pd.DataFrame(rows)
t02.to_csv(TAB_DIR / "T02_internet_access.csv", index=False)

# Internet Uses (multi-select)
from collections import Counter
use_counts = Counter()
for lst in df["uses_list"]:
    for u in lst:
        use_counts[u] += 1
use_df = pd.DataFrame(list(use_counts.items()), columns=["use", "mentions"])
use_df["pct_of_N"] = (use_df["mentions"] / N * 100).round(1)
use_df = use_df.sort_values("mentions", ascending=False)
use_df.to_csv(TAB_DIR / "T02b_internet_uses.csv", index=False)

# Barriers (multi-select)
bar_counts = Counter()
for lst in df["barriers_list"]:
    for b in lst:
        bar_counts[b] += 1
bar_df = pd.DataFrame(list(bar_counts.items()), columns=["barrier", "mentions"])
bar_df["pct_of_N"] = (bar_df["mentions"] / N * 100).round(1)
bar_df = bar_df.sort_values("mentions", ascending=False)
bar_df.to_csv(TAB_DIR / "T02c_barriers.csv", index=False)

# IA Level
t = freq_table(df["ia_cat"], ["Low", "Medium", "High"])
t.to_csv(TAB_DIR / "T02d_ia_level.csv", index=False)

# ---- T03 SDL Readiness ----
rows = []
for name, label in [("sdl_self_mgmt", "Self Management"), ("sdl_desire", "Desire for Learning"), ("sdl_self_ctrl", "Self Control")]:
    rows.append({"subscale": label, "mean": round(df[name].mean(), 2),
                 "sd": round(df[name].std(), 2), "median": round(df[name].median(), 2),
                 "min": round(df[name].min(), 2), "max": round(df[name].max(), 2)})

t03_sub = pd.DataFrame(rows)
t03_sub.to_csv(TAB_DIR / "T03_sdl_subscales.csv", index=False)

# SDL Total
rows = [{"score": "SDL Total (24-120)", "mean": round(df["sdl_total"].mean(), 2),
         "sd": round(df["sdl_total"].std(), 2), "median": round(df["sdl_total"].median(), 2),
         "min": round(df["sdl_total"].min(), 2), "max": round(df["sdl_total"].max(), 2)}]
t03_total = pd.DataFrame(rows)
t03_total.to_csv(TAB_DIR / "T03b_sdl_total.csv", index=False)

# SDL Categories
t = freq_table(df["sdl_cat"], ["Low", "Moderate", "High"])
t.to_csv(TAB_DIR / "T03c_sdl_categories.csv", index=False)

# Item-level SDL
rows = []
for i in range(24):
    col = f"SDL{i+1}"
    rows.append({"item": f"SDL{i+1}", "mean": round(df[f"SDL{i+1}"].mean(), 2),
                 "sd": round(df[f"SDL{i+1}"].std(), 2),
                 "median": round(df[f"SDL{i+1}"].median(), 2)})
pd.DataFrame(rows).to_csv(TAB_DIR / "T03d_sdl_items.csv", index=False)

# ---- T04 Reliability (Cronbach's alpha) ----
def cronbach(item_df):
    d = item_df.dropna()
    k = d.shape[1]
    if k < 2 or len(d) < 3: return np.nan
    iv = d.var(axis=0, ddof=1).sum()
    tv = d.sum(axis=1).var(ddof=1)
    return k / (k - 1) * (1 - iv / tv) if tv > 0 else np.nan

sdl_items = [f"SDL{i+1}" for i in range(24)]
alphas = {
    "SDL Total (24 items)": cronbach(df[sdl_items]),
    "Self Management (8)": cronbach(df[[f"SDL{i+1}" for i in range(8)]]),
    "Desire for Learning (8)": cronbach(df[[f"SDL{i+1}" for i in range(8, 16)]]),
    "Self Control (8)": cronbach(df[[f"SDL{i+1}" for i in range(16, 24)]]),
}
pd.DataFrame([{"scale": k, "alpha": round(v, 3)} for k, v in alphas.items()]).to_csv(
    TAB_DIR / "T04_reliability.csv", index=False)

# ---- T05 Hypothesis 1: Correlation IA Score ↔ SDL Total ----
r_s, p_s = spearmanr(df["ia_score"], df["sdl_total"])
r_p, p_p = pearsonr(df["ia_score"], df["sdl_total"])
h1 = pd.DataFrame([{
    "test": "Spearman", "r": round(r_s, 3), "p": round(p_s, 4),
    "interpretation": "Significant" if p_s < 0.05 else "Not significant"
}, {
    "test": "Pearson", "r": round(r_p, 3), "p": round(p_p, 4),
    "interpretation": "Significant" if p_p < 0.05 else "Not significant"
}])
h1.to_csv(TAB_DIR / "T05_hypothesis1_correlation.csv", index=False)

# Correlation matrix (IA components vs SDL subscales)
ia_comp = ["ia_device", "ia_freq", "ia_means", "ia_reliability", "ia_hours", "ia_score", "sat_num"]
sdl_comp = ["sdl_self_mgmt", "sdl_desire", "sdl_self_ctrl", "sdl_total"]
corr_rows = []
for a in ia_comp:
    for s in sdl_comp:
        r, p = spearmanr(df[a], df[s])
        corr_rows.append({"ia_component": a, "sdl_component": s, "spearman_r": round(r, 3), "p": round(p, 4)})
pd.DataFrame(corr_rows).to_csv(TAB_DIR / "T05b_correlation_matrix.csv", index=False)

# ---- T06 Hypothesis 2: SDL across Academic Levels ----
levels = ["100 level", "200 level", "300 level", "400 level"]
groups = [df.loc[df["level_c"] == l, "sdl_total"].dropna() for l in levels]
h_stat, h_p = kruskal(*groups)
h2_main = pd.DataFrame([{
    "test": "Kruskal-Wallis", "H": round(h_stat, 3), "df": len(levels)-1,
    "p": round(h_p, 4), "significant": "Yes" if h_p < 0.05 else "No"
}])
h2_main.to_csv(TAB_DIR / "T06_hypothesis2_kruskal.csv", index=False)

# Pairwise Mann-Whitney (Bonferroni)
pair_rows = []
for i, l1 in enumerate(levels):
    for l2 in levels[i+1:]:
        g1 = df.loc[df["level_c"] == l1, "sdl_total"].dropna()
        g2 = df.loc[df["level_c"] == l2, "sdl_total"].dropna()
        u, p = mannwhitneyu(g1, g2, alternative="two-sided")
        pair_rows.append({"comparison": f"{l1} vs {l2}", "U": round(u, 1),
                          "p_raw": round(p, 4), "p_bonf": round(min(p*6, 1), 4),
                          "significant": "Yes" if p*6 < 0.05 else "No"})
pd.DataFrame(pair_rows).to_csv(TAB_DIR / "T06b_pairwise.csv", index=False)

# Descriptives by level
rows = []
for l in levels:
    sub = df.loc[df["level_c"] == l, "sdl_total"].dropna()
    rows.append({"level": l, "n": len(sub), "mean": round(sub.mean(), 2),
                 "sd": round(sub.std(), 2), "median": round(sub.median(), 2)})
pd.DataFrame(rows).to_csv(TAB_DIR / "T06c_sdl_by_level.csv", index=False)

# ---- T07 Factors Influencing Internet Access ----
# Barriers already saved in T02c
# Device ownership by level
rows = []
for l in levels:
    sub = df[df["level_c"] == l]
    yes = (sub["device_c"] == "Yes").sum()
    rows.append({"level": l, "n": len(sub), "device_yes_n": int(yes), "device_yes_pct": round(yes/len(sub)*100, 1)})
pd.DataFrame(rows).to_csv(TAB_DIR / "T07a_device_by_level.csv", index=False)

# Means of access by level
rows = []
for l in levels:
    t = freq_table(df.loc[df["level_c"] == l, "means_c"])
    for _, r in t.iterrows():
        rows.append({"level": l, "means": r["category"], "n": int(r["n"]), "pct": r["pct"]})
pd.DataFrame(rows).to_csv(TAB_DIR / "T07b_means_by_level.csv", index=False)

# Reliability by level
rows = []
for l in levels:
    t = freq_table(df.loc[df["level_c"] == l, "reliability_c"])
    for _, r in t.iterrows():
        rows.append({"level": l, "reliability": r["category"], "n": int(r["n"]), "pct": r["pct"]})
pd.DataFrame(rows).to_csv(TAB_DIR / "T07c_reliability_by_level.csv", index=False)

# Satisfaction by level
rows = []
for l in levels:
    t = freq_table(df.loc[df["level_c"] == l, "satisfaction_c"],
                   ["Very satisfied", "Satisfied", "Neutral", "Dissatisfied", "Very dissatisfied"])
    for _, r in t.iterrows():
        rows.append({"level": l, "satisfaction": r["category"], "n": int(r["n"]), "pct": r["pct"]})
pd.DataFrame(rows).to_csv(TAB_DIR / "T07d_satisfaction_by_level.csv", index=False)

# IA Score by level
rows = []
for l in levels:
    sub = df.loc[df["level_c"] == l, "ia_score"].dropna()
    rows.append({"level": l, "n": len(sub), "mean": round(sub.mean(), 2),
                 "sd": round(sub.std(), 2), "median": round(sub.median(), 2)})
pd.DataFrame(rows).to_csv(TAB_DIR / "T07e_ia_score_by_level.csv", index=False)

# ---- T08 IA Score vs SDL by Level (interaction check) ----
rows = []
for l in levels:
    sub = df[df["level_c"] == l]
    r, p = spearmanr(sub["ia_score"], sub["sdl_total"])
    rows.append({"level": l, "n": len(sub), "spearman_r": round(r, 3), "p": round(p, 4)})
pd.DataFrame(rows).to_csv(TAB_DIR / "T08_correlation_by_level.csv", index=False)

# ---- T09 SDL Subscales by Level ----
rows = []
for name, label in [("sdl_self_mgmt", "Self Management"), ("sdl_desire", "Desire for Learning"), ("sdl_self_ctrl", "Self Control")]:
    for l in levels:
        sub = df.loc[df["level_c"] == l, name].dropna()
        rows.append({"subscale": label, "level": l, "n": len(sub),
                     "mean": round(sub.mean(), 2), "sd": round(sub.std(), 2)})
pd.DataFrame(rows).to_csv(TAB_DIR / "T09_sdl_subscales_by_level.csv", index=False)

# ---- T10 IA Components vs SDL Subscales ----
rows = []
ia_items = {"ia_freq": "Frequency", "ia_means": "Means", "ia_reliability": "Reliability",
            "ia_hours": "Hours", "ia_device": "Device", "ia_score": "Composite"}
sdl_items = {"sdl_self_mgmt": "Self Mgmt", "sdl_desire": "Desire", "sdl_self_ctrl": "Self Ctrl", "sdl_total": "Total"}
for ia_key, ia_label in ia_items.items():
    for sdl_key, sdl_label in sdl_items.items():
        r, p = spearmanr(df[ia_key], df[sdl_key])
        rows.append({"IA": ia_label, "SDL": sdl_label, "spearman_r": round(r, 3), "p": round(p, 4)})
pd.DataFrame(rows).to_csv(TAB_DIR / "T10_ia_vs_sdl_subscales.csv", index=False)

# ---- Verification ----
print("--- STATS VERIFICATION ---")
print(f"N = {N}")
print("H1 Spearman:", round(r_s, 3), "p =", round(p_s, 4))
print("H1 Pearson:", round(r_p, 3), "p =", round(p_p, 4))
print("H2 Kruskal-Wallis: H =", round(h_stat, 3), "p =", round(h_p, 4))
print("Tables saved to:", TAB_DIR)