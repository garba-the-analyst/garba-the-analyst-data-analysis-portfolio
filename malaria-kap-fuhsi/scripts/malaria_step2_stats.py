"""Malaria Prevention KAP Study — Phase 2: Statistics."""
import warnings
import os
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.stats import chi2_contingency, fisher_exact, spearmanr, pearsonr, kruskal, mannwhitneyu
from scipy.stats import chi2 as chi2dist

warnings.filterwarnings("ignore")

BASE = Path("/home/garba-the-analyst/Desktop/Projects/Data analysis ")
os.chdir(BASE)

CLEAN = BASE / "data" / "processed" / "malaria_kap_cleaned.csv"
TAB_DIR = BASE / "reports" / "output" / "tables"
TAB_DIR.mkdir(parents=True, exist_ok=True)

df = pd.read_csv(CLEAN, dtype=str, keep_default_na=False)
# Convert numeric columns
num_cols = ["know_score", "know_pct", "prac_score", "mis_score", "gap_score",
            "level_num", "age_ord"] + \
           [f"K{i+1}" for i in range(10)] + \
           [f"P{i+1}" for i in range(8)] + \
           [f"M{i+1}" for i in range(8)]
for c in num_cols:
    if c in df.columns:
        df[c] = pd.to_numeric(df[c], errors="coerce")

N = len(df)

# Original raw column positions preserved in cleaned CSV
K = list(range(7, 17)); P = list(range(17, 25)); M = list(range(25, 33))

# Department to Faculty mapping
DEPT_FAC = {
    "Nursing": "Allied Health", "Audiology": "Allied Health", "Human Nutrition & Dietetics": "Allied Health",
    "MBBS": "Clinical", "MLS": "Basic Medical", "Pharmacology": "Basic Medical",
    "Microbiology": "Basic Medical", "Biochemistry": "Basic Medical",
    "Human Nutrition & Dietetics": "Allied Health",
    "Information Technology & Health": "Basic Medical",
}
df["faculty_grp"] = df["dept_c"].map(DEPT_FAC).fillna("Other")

# ---- Helper ----
def freq_table(s, order=None):
    vc = s.value_counts()
    if order:
        vc = vc.reindex([o for o in order if o in vc.index])
    t = pd.DataFrame({"category": vc.index, "n": vc.values})
    t["pct"] = (t["n"] / len(s) * 100).round(1)
    return t

def cramers_v(chi2, n, ct):
    return np.sqrt((chi2 / n) / (min(ct.shape) - 1)) if min(ct.shape) > 1 else np.nan

def chi2_run(name, r, c, subset=None, note=""):
    d = df if subset is None else df.loc[subset]
    ct = pd.crosstab(d[r], d[c])
    if ct.shape[0] < 2 or ct.shape[1] < 2:
        return {"test": name, "chi2": "", "dof": "", "p": "", "cramers_v": "",
                "min_expected": "", "note": "insufficient categories " + note}
    chi2, p, dof, expf = chi2_contingency(ct)
    n = ct.values.sum()
    fins = ""
    if ct.shape == (2, 2) and expf.min() < 5:
        odds, fins = fisher_exact(ct)
    row = {"test": name, "variables": f"{r} x {c}", "n": int(n),
           "chi2": round(chi2, 3), "dof": int(dof), "p": round(float(p), 4),
           "cramers_v": round(cramers_v(chi2, n, ct), 3),
           "min_expected": round(expf.min(), 2),
           "note": ("Fisher_exact_used(2x2,exp<5):p=" + str(round(fins, 4)) if fins != "" else
             ("some_cells_expected<5" if expf.min() < 5 else "valid"))}
    row["table_flat"] = "; ".join(f"{a}|{b}:{ct.loc[a, b]}" for a in ct.index for b in ct.columns)
    return row

# ---- T01 Demographics ----
rows = []
for var, label, order in [
    ("age_band", "Age Group", ["16 – 20 years", "21 – 25 years", "26 – 30 years"]),
    ("gender_c", "Gender", ["Male", "Female"]),
    ("level_c", "Academic Level", ["100 Level", "200 Level", "300 Level", "400 Level"]),
    ("residence_c", "Residence", ["University Hostel (on-campus)", "Off-campus Hostel/Lodge", "Living with Family/Guardian"]),
    ("faculty_grp", "Faculty Group", ["Allied Health", "Basic Medical", "Clinical", "Other"]),
    ("dept_c", "Department", None),
]:
    t = freq_table(df[var], order)
    for _, r in t.iterrows():
        rows.append({"section": label, "category": r["category"], "n": int(r["n"]), "pct": r["pct"]})
t01 = pd.DataFrame(rows)
t01.to_csv(TAB_DIR / "T01_demographics.csv", index=False)

# ---- T02 Knowledge Items ----
rows = []
for i in range(10):
    v = df[f"K{i+1}"]
    rows.append({"item": f"K{i+1}", "statement": df[f"K{i+1}_raw"].iloc[0] if f"K{i+1}_raw" in df.columns else "",
                 "correct_n": int(v.sum()), "correct_pct": round(v.mean() * 100, 1),
                 "incorrect_n": int((v == 0).sum()), "incorrect_pct": round((v == 0).mean() * 100, 1)})
pd.DataFrame(rows).to_csv(TAB_DIR / "T02_knowledge_items.csv", index=False)

# Knowledge score summary
summ = pd.DataFrame([{
    "score": "Knowledge Score (0-10)", "mean": round(df["know_score"].mean(), 2),
    "sd": round(df["know_score"].std(), 2), "median": df["know_score"].median(),
    "min": df["know_score"].min(), "max": df["know_score"].max(),
    "Good_fixed_n": int((df["know_cat_fixed"] == "Good (≥8)").sum()),
    "Moderate_fixed_n": int((df["know_cat_fixed"] == "Moderate (5-7)").sum()),
    "Poor_fixed_n": int((df["know_cat_fixed"] == "Poor (<5)").sum()),
    "Good_median_n": int((df["know_cat_median"] == "Good (≥median)").sum()),
    "Poor_median_n": int((df["know_cat_median"] == "Poor (<median)").sum()),
}])
summ.to_csv(TAB_DIR / "T02b_knowledge_summary.csv", index=False)

# ---- T03 Practice Items ----
rows = []
prac_labels = {
    1: "Sleep under ITN every night",
    2: "Clear stagnant water/bushes",
    3: "Use mosquito repellent",
    4: "Screen/close windows & doors at night",
    5: "Dispose refuse/empty containers properly",
    6: "Seek testing/treatment for fever",
    7: "Complete full antimalarial course",
    8: "Wear long-sleeved clothing in evening",
}
for i in range(8):
    v = df[f"P{i+1}_raw"]
    rows.append({"item": f"P{i+1}", "description": prac_labels[i+1],
                 "Always_n": int((v == "Always").sum()), "Always_pct": round((v == "Always").mean() * 100, 1),
                 "Often_n": int((v == "Often").sum()), "Often_pct": round((v == "Often").mean() * 100, 1),
                 "Sometimes_n": int((v == "Sometimes").sum()), "Sometimes_pct": round((v == "Sometimes").mean() * 100, 1),
                 "Rarely_n": int((v == "Rarely").sum()), "Rarely_pct": round((v == "Rarely").mean() * 100, 1),
                 "Never_n": int((v == "Never").sum()), "Never_pct": round((v == "Never").mean() * 100, 1),
                 "mean_1to5": round(df[f"P{i+1}"].mean(), 2)})
pd.DataFrame(rows).to_csv(TAB_DIR / "T03_practice_items.csv", index=False)

# Practice score summary
summ = pd.DataFrame([{
    "score": "Practice Score (8-40)", "mean": round(df["prac_score"].mean(), 2),
    "sd": round(df["prac_score"].std(), 2), "median": df["prac_score"].median(),
    "min": df["prac_score"].min(), "max": df["prac_score"].max(),
    "Good_fixed_n": int((df["prac_cat_fixed"] == "Good (≥30)").sum()),
    "Moderate_fixed_n": int((df["prac_cat_fixed"] == "Moderate (18-29)").sum()),
    "Poor_fixed_n": int((df["prac_cat_fixed"] == "Poor (<18)").sum()),
    "Good_median_n": int((df["prac_cat_median"] == "Good (≥median)").sum()),
    "Poor_median_n": int((df["prac_cat_median"] == "Poor (<median)").sum()),
}])
summ.to_csv(TAB_DIR / "T03b_practice_summary.csv", index=False)

# ---- T04 Misconceptions ----
rows = []
for i in range(8):
    col_idx = M[i]  # actual column position for header text
    v = df[f"M{i+1}_raw"]
    # Reverse-coded: SD=5, D=4, N=3, A=2, SA=1
    rows.append({"item": f"M{i+1}", "statement": str(df.columns[col_idx]).split("[")[-1].rstrip("] ")[:100],
                 "SA_n": int((v == "Strongly Agree").sum()), "SA_pct": round((v == "Strongly Agree").mean() * 100, 1),
                 "A_n": int((v == "Agree").sum()), "A_pct": round((v == "Agree").mean() * 100, 1),
                 "N_n": int((v == "Neutral").sum()), "N_pct": round((v == "Neutral").mean() * 100, 1),
                 "D_n": int((v == "Disagree").sum()), "D_pct": round((v == "Disagree").mean() * 100, 1),
                 "SD_n": int((v == "Strongly Disagree").sum()), "SD_pct": round((v == "Strongly Disagree").mean() * 100, 1),
                 "mean_1to5": round(df[f"M{i+1}"].mean(), 2)})
pd.DataFrame(rows).to_csv(TAB_DIR / "T04_misconceptions.csv", index=False)

summ = pd.DataFrame([{
    "score": "Misconception Score (8-40, higher=fewer)", "mean": round(df["mis_score"].mean(), 2),
    "sd": round(df["mis_score"].std(), 2), "median": df["mis_score"].median(),
    "min": df["mis_score"].min(), "max": df["mis_score"].max(),
}])
summ.to_csv(TAB_DIR / "T04b_misconceptions_summary.csv", index=False)

# ---- T05 Training / Experience / ITN ----
t05 = pd.DataFrame()
rows = []
for var, label in [("training_c", "Formal Training"), ("source_c", "Knowledge Source"),
                    ("diagnosed_c", "Ever Diagnosed"), ("itn_own_c", "ITN Ownership"),
                    ("access_c", "Access to Preventives")]:
    t = freq_table(df[var])
    t["section"] = label
    rows.append(pd.DataFrame({"section": [label]*len(t), "category": t["category"].values,
                              "n": t["n"].values, "pct": t["pct"].values}))
pd.concat(rows, ignore_index=True).to_csv(TAB_DIR / "T05_training_experience.csv", index=False)

# ITN ownership by level/dept
for var, label in [("itn_own_c", "ITN Ownership"), ("access_c", "Access Rating")]:
    rows = []
    for l in ["100 Level", "200 Level", "300 Level", "400 Level"]:
        t = freq_table(df.loc[df["level_c"] == l, var])
        for _, r in t.iterrows():
            rows.append({"level": l, "category": r["category"], "n": int(r["n"]), "pct": r["pct"]})
    pd.DataFrame(rows).to_csv(TAB_DIR / f"T05b_{label.lower().replace(' ', '_')}_by_level.csv", index=False)

# ---- T06 Barriers / Intent ----
rows = []
for var, label in [("net_purchase_c", "Likely to purchase or replace ITN"),
                    ("comfort_c", "Comfort sleeping under ITN"), ("treat24_c", "Likely to seek treatment within 24h"),
                    ("sanit_c", "Willing to participate in sanitation"), ("talk_c", "Likely to attend health talk")]:
    t = freq_table(df[var])
    t["section"] = label
    for _, r in t.iterrows():
        rows.append({"section": label, "category": r["category"], "n": int(r["n"]), "pct": r["pct"]})
pd.DataFrame(rows).to_csv(TAB_DIR / "T06_barriers_intent.csv", index=False)

# ---- T07 H1: Knowledge vs Practice (Chi-square) ----
rows = []
for k_cat, p_cat, name in [
    ("know_cat_fixed", "prac_cat_fixed", "Knowledge (Fixed) x Practice (Fixed)"),
    ("know_cat_median", "prac_cat_median", "Knowledge (Median) x Practice (Median)"),
]:
    rows.append(chi2_run("H1 Primary", k_cat, p_cat))
    # By level
    for l in ["100 Level", "200 Level", "300 Level", "400 Level"]:
        rows.append(chi2_run(f"H1 by Level ({l})", k_cat, p_cat,
                             subset=df["level_c"] == l, note=f"level={l}"))
    # By faculty
    for f in df["faculty_grp"].unique():
        rows.append(chi2_run(f"H1 by Faculty ({f})", k_cat, p_cat,
                             subset=df["faculty_grp"] == f, note=f"faculty={f}"))
pd.DataFrame(rows).to_csv(TAB_DIR / "T07_hypothesis1_chi2.csv", index=False)

# Continuous correlation (H1 supplementary)
r_s, p_s = spearmanr(df["know_score"], df["prac_score"])
r_p, p_p = pearsonr(df["know_score"], df["prac_score"])
pd.DataFrame([{
    "test": "Spearman", "r": round(r_s, 3), "p": round(p_s, 4),
    "interpretation": "Significant" if p_s < 0.05 else "Not significant"
}, {
    "test": "Pearson", "r": round(r_p, 3), "p": round(p_p, 4),
    "interpretation": "Significant" if p_p < 0.05 else "Not significant"
}]).to_csv(TAB_DIR / "T07b_correlation_continuous.csv", index=False)

# ---- T08 H2: Knowledge/Practice by Level & Dept ----
# Kruskal-Wallis
rows = []
for score, label in [("know_score", "Knowledge"), ("prac_score", "Practice"), ("mis_score", "Misconceptions")]:
    groups = [df.loc[df["level_c"] == l, score].dropna() for l in ["100 Level", "200 Level", "300 Level", "400 Level"]]
    h, p = kruskal(*groups)
    rows.append({"variable": label, "test": "Kruskal-Wallis (Level)", "H": round(h, 3), "df": 3, "p": round(p, 4)})
    # Pairwise Mann-Whitney
    for i, l1 in enumerate(["100 Level", "200 Level", "300 Level", "400 Level"]):
        for l2 in ["200 Level", "300 Level", "400 Level"][i:]:
            g1 = df.loc[df["level_c"] == l1, score].dropna()
            g2 = df.loc[df["level_c"] == l2, score].dropna()
            if len(g1) > 1 and len(g2) > 1:
                u, p = mannwhitneyu(g1, g2, alternative="two-sided")
                rows.append({"variable": label, "test": "Mann-Whitney (Level)", "comparison": f"{l1} vs {l2}",
                             "U": round(u, 1), "p_raw": round(p, 4), "p_bonf": round(min(p*6, 1), 4)})
pd.DataFrame(rows).to_csv(TAB_DIR / "T08_kruskal_level.csv", index=False)

# By Faculty Group
rows = []
for score, label in [("know_score", "Knowledge"), ("prac_score", "Practice")]:
    groups = [df.loc[df["faculty_grp"] == f, score].dropna() for f in df["faculty_grp"].unique() if f != "Other"]
    if len(groups) > 1:
        h, p = kruskal(*groups)
        rows.append({"variable": label, "test": "Kruskal-Wallis (Faculty)", "H": round(h, 3), "df": len(groups)-1, "p": round(p, 4)})
pd.DataFrame(rows).to_csv(TAB_DIR / "T08b_kruskal_faculty.csv", index=False)

# Chi-square: Knowledge/Practice categories by Level
rows = []
for k_cat in ["know_cat_fixed", "prac_cat_fixed"]:
    for demo in ["level_c", "faculty_grp", "gender_c", "residence_c"]:
        rows.append(chi2_run(f"Category x Demographics", k_cat, demo))
pd.DataFrame(rows).to_csv(TAB_DIR / "T08c_category_demographics.csv", index=False)

# ---- T09 Sources of Information ----
t = freq_table(df["source_c"])
t.to_csv(TAB_DIR / "T09_info_sources.csv", index=False)

# ---- T10 ITN Ownership ----
# Logistic regression (supplementary)
try:
    import statsmodels.api as sm
    X = df[["know_score", "level_num"]].copy()
    X["male"] = (df["gender_c"] == "Male").astype(int)
    X["level_num"] = pd.to_numeric(X["level_num"], errors="coerce")
    X["know_score"] = pd.to_numeric(X["know_score"], errors="coerce")
    X["const"] = 1
    y = (df["itn_own_c"] == "Yes").astype(int)
    keep = X.notna().all(axis=1)
    logit = sm.Logit(y[keep], X[keep]).fit(disp=0)
    conf = logit.conf_int()
    rows = [{"predictor": i, "OR": round(np.exp(logit.params[i]), 2),
             "CI_low": round(np.exp(conf.loc[i, 0]), 2), "CI_high": round(np.exp(conf.loc[i, 1]), 2),
             "p": round(logit.pvalues[i], 4)} for i in X.columns]
    pd.DataFrame(rows).to_csv(TAB_DIR / "T10_logistic_itn.csv", index=False)
except Exception as e:
    print("Logistic skipped:", e)

# ---- T11 Supplementary: Gap Score Analysis ----
rows = []
for l in ["100 Level", "200 Level", "300 Level", "400 Level"]:
    sub = df.loc[df["level_c"] == l, "gap_score"].dropna()
    rows.append({"level": l, "n": len(sub), "mean_gap": round(sub.mean(), 3), "sd": round(sub.std(), 3)})
pd.DataFrame(rows).to_csv(TAB_DIR / "T11_gap_by_level.csv", index=False)

# ---- T12 Supplementary: Misconceptions by Level ----
rows = []
for l in ["100 Level", "200 Level", "300 Level", "400 Level"]:
    sub = df.loc[df["level_c"] == l, "mis_score"].dropna()
    rows.append({"level": l, "n": len(sub), "mean": round(sub.mean(), 2), "sd": round(sub.std(), 2)})
pd.DataFrame(rows).to_csv(TAB_DIR / "T12_mis_by_level.csv", index=False)

# ---- T13 Supplementary: Logistic Practice Good ~ Knowledge + Covariates ----
try:
    import statsmodels.api as sm
    y = (df["prac_cat_fixed"] == "Good (≥30)").astype(int)
    X = df[["know_score", "level_num", "mis_score"]].copy()
    X["male"] = (df["gender_c"] == "Male").astype(int)
    X = X.apply(pd.to_numeric, errors="coerce")
    X["const"] = 1
    keep = X.notna().all(axis=1) & y.notna()
    logit = sm.Logit(y[keep], X[keep]).fit(disp=0)
    conf = logit.conf_int()
    rows = [{"predictor": i, "OR": round(np.exp(logit.params[i]), 2),
             "CI_low": round(np.exp(conf.loc[i, 0]), 2), "CI_high": round(np.exp(conf.loc[i, 1]), 2),
             "p": round(logit.pvalues[i], 4)} for i in X.columns]
    pd.DataFrame(rows).to_csv(TAB_DIR / "T13_logistic_practice.csv", index=False)
except Exception as e:
    print("Logistic practice skipped:", e)

# ---- Verification ----
print("\n--- STATS VERIFICATION ---")
print(f"N = {N}")
print("H1 Fixed:", pd.read_csv(TAB_DIR / "T07_hypothesis1_chi2.csv").head(2).to_string())
print("H1 Continuous: Spearman r=", round(r_s, 3), "p=", round(p_s, 4), "Pearson r=", round(r_p, 3), "p=", round(p_p, 4))
print("H2 Kruskal:", pd.read_csv(TAB_DIR / "T08_kruskal_level.csv").head(5).to_string())
print("Tables saved:", len(list(TAB_DIR.glob("*.csv"))))