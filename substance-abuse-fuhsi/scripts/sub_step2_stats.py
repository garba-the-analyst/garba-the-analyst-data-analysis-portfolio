"""Substance Abuse Study — Step 2: statistics (descriptives + bivariate).
Run: cd "/home/garba-the-analyst/Desktop/Projects/Data analysis " && /home/garba-the-analyst/.venvs/global/bin/python sub_step2_stats.py
"""
import warnings
import os
import sys
import ast
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.stats import chi2_contingency, fisher_exact, spearmanr, pearsonr, mannwhitneyu, kruskal
from statsmodels.stats.proportion import proportion_confint

warnings.filterwarnings("ignore")
PROJECT_ROOT = "/home/garba-the-analyst/Desktop/Projects/Data analysis "
os.chdir(PROJECT_ROOT)

PROC_DIR = Path(os.path.join(PROJECT_ROOT, "data/processed"))
TAB_DIR = Path(os.path.join(PROJECT_ROOT, "reports/output/tables"))
TAB_DIR.mkdir(parents=True, exist_ok=True)

df = pd.read_csv(PROC_DIR / "substance_abuse_cleaned_full.csv", dtype=str, keep_default_na=False)
# Restore numeric columns (EXCLUDE categorical _c columns: ever_use_c, past_3mo_c, etc.)
EXCLUDE_NUMERIC = {"ever_use_c", "past_3mo_c", "age_c", "sex_c", "level_c", "faculty_c", 
                    "religion_c", "marital_c", "living_c", "allowance_c", "freq_c",
                    "poly_use_c", "should_reduce_c", "withdrawal_c", "primary_substance",
                    "problem_use", "any_substance_3mo"}
num_cols = [c for c in df.columns if (c.endswith("_c") or c.endswith("_score") or 
            c.startswith("factor_") or c.startswith("health_") or c.startswith("prev_")) 
            and c not in EXCLUDE_NUMERIC]
for c in num_cols:
    if c in df.columns:
        df[c] = pd.to_numeric(df[c], errors="coerce")

# Lists for scales
factor_cols = [f"factor_{i+1:02d}" for i in range(13)]
health_cols = [f"health_{i+1:02d}" for i in range(12)]
prev_cols = [f"prev_{i+1:02d}" for i in range(8)]

N = len(df)
print(f"Analysing N = {N}")

# Wilson CI helper
def wilson_ci(count, nobs, alpha=0.05):
    if nobs == 0:
        return (np.nan, np.nan)
    lo, hi = proportion_confint(count, nobs, alpha=alpha, method="wilson")
    return round(lo * 100, 1), round(hi * 100, 1)

def freq_table(series, name, order=None):
    vc = series.value_counts(dropna=False)
    if order:
        vc = vc.reindex(order, fill_value=0)
    rows = []
    for k, v in vc.items():
        lo, hi = wilson_ci(int(v), N)
        rows.append({"category": str(k), "n": int(v), "pct": round(v / N * 100, 1),
                     "ci95_lo": lo, "ci95_hi": hi})
    return pd.DataFrame(rows).assign(variable=name)

# ============================================================
# D01 Demographics
# ============================================================
demo_vars = ["age_c", "sex_c", "level_c", "faculty_c", "religion_c", "marital_c", "living_c", "allowance_c"]
demos = pd.concat([freq_table(df[c], c) for c in demo_vars], ignore_index=True)
demos.to_csv(TAB_DIR / "D01_demographics.csv", index=False)
print("D01 saved")

# ============================================================
# D02 Substance Use (Objective 1)
# ============================================================
# Ever use
D02_ever = freq_table(df["ever_use_c"], "ever_use", order=["Yes", "No"])
D02_ever.to_csv(TAB_DIR / "D02_ever_use.csv", index=False)

# Past 3 months
df["past_3mo_c_clean"] = df["past_3mo_c"].fillna("No").replace("", "No")
D02_past = freq_table(df["past_3mo_c_clean"], "past_3mo", order=["Yes", "No"])
D02_past.to_csv(TAB_DIR / "D02_past_3mo.csv", index=False)

# Problem use
D02_prob = freq_table(pd.to_numeric(df["problem_use"], errors="coerce").map({1: "Yes", 0: "No"}), "problem_use", order=["Yes", "No"])
D02_prob.to_csv(TAB_DIR / "D02_problem_use.csv", index=False)

# Frequency of use
freq_num = pd.to_numeric(df["freq_c"], errors="coerce")
freq_order = ["0 (Never/Not applicable/Not stated)", "1 (Less than once a week)",
              "2 (1–2 times per week)", "3 (3–6 times per week)"]
df["freq_label"] = freq_num.map({0: freq_order[0], 1: freq_order[1],
                                  2: freq_order[2], 3: freq_order[3]})
df["freq_label"] = df["freq_label"].fillna(freq_order[0])
D02_freq = freq_table(df["freq_label"], "frequency", order=freq_order)
D02_freq.to_csv(TAB_DIR / "D02_frequency.csv", index=False)

# Poly-use
df["poly_use_c_clean"] = df["poly_use_c"].fillna("No").replace("", "No")
D02_poly = freq_table(df["poly_use_c_clean"], "poly_use", order=["Yes", "No"])
D02_poly.to_csv(TAB_DIR / "D02_poly_use.csv", index=False)

# CAGE-type items
for col, name in [("should_reduce_c", "should_reduce"), ("withdrawal_c", "withdrawal")]:
    df[f"{col}_clean"] = df[col].fillna("No").replace("", "No")
    t = freq_table(df[f"{col}_clean"], name, order=["Yes", "No"])
    t.to_csv(TAB_DIR / f"D02_{name}.csv", index=False)

# Problem use flag
D02_prob_flag = freq_table(pd.to_numeric(df["problem_use"], errors="coerce").map({1: "Yes", 0: "No"}), "problem_use_flag", order=["Yes", "No"])
D02_prob_flag.to_csv(TAB_DIR / "D02_problem_use_flag.csv", index=False)

# Substance-specific (multi-response)
from collections import Counter
def parse_subs(s):
    s = str(s).strip()
    if s in ("", "None", "none", "Not applicable", "Not at all", "[]"):
        return []
    if s.startswith("[") and s.endswith("]"):   # legacy str(list) form
        try:
            return [str(x).strip() for x in ast.literal_eval(s) if str(x).strip()]
        except Exception:
            pass
    return [p.strip() for p in s.split(";") if p.strip() and p.strip() != "None"]

all_subs = []
for lst in df["substances_list"]:
    all_subs.extend(parse_subs(lst))
sub_counts = Counter(all_subs)
sub_rows = []
for sub, cnt in sub_counts.most_common():
    lo, hi = wilson_ci(cnt, N)
    sub_rows.append({"substance": sub, "mentions": cnt, "pct_of_respondents": round(cnt/N*100, 1),
                     "ci95_lo": lo, "ci95_hi": hi})
pd.DataFrame(sub_rows).to_csv(TAB_DIR / "D02_substance_specific.csv", index=False)

# Any substance past 3mo
D02_any = freq_table(pd.to_numeric(df["any_substance_3mo"], errors="coerce").map({1: "Yes", 0: "No"}), "any_substance_3mo", order=["Yes", "No"])
D02_any.to_csv(TAB_DIR / "D02_any_substance_3mo.csv", index=False)

print("D02 saved")

# ============================================================
# D03 Influencing Factors (Objective 2)
# ============================================================
FACTOR_LABELS = ["Peer pressure", "Academic stress", "Curiosity/experimentation",
    "Easy availability", "Family member use", "Social media exposure",
    "Emotional distress", "Coping with pain/stress/sleep",
    "Social gatherings/parties", "Low self-esteem",
    "Limited parental monitoring", "Boredom/unstructured time",
    "Inadequate policy enforcement"]

# Likert mapping (used throughout)
LIKERT_MAP = {"SA": 5, "A": 4, "U": 3, "D": 2, "SD": 1}
def norm_likert(s):
    s = str(s).strip().upper()
    return {"SA": 5, "A": 4, "U": 3, "D": 2, "SD": 1}.get(s, np.nan)

factor_rows = []
for i, col in enumerate([f"factor_{i+1:02d}" for i in range(13)]):
    label = FACTOR_LABELS[i] if i < len(FACTOR_LABELS) else f"Factor {i+1}"
    s = df[col].dropna()
    factor_rows.append({"factor": f"Factor {i+1}", "label": label,
                        "mean": round(s.mean(), 2), "sd": round(s.std(), 2),
                        "median": round(s.median(), 2), "n": int(s.notna().sum())})
pd.DataFrame(factor_rows).to_csv(TAB_DIR / "D03_factors_descriptive.csv", index=False)

# Factor item % SA/A
item_rows = []
for i, col in enumerate([f"factor_{i+1:02d}" for i in range(13)]):
    label = FACTOR_LABELS[i] if i < len(FACTOR_LABELS) else f"Factor {i+1}"
    s = pd.to_numeric(df[col], errors="coerce")
    total = s.notna().sum()
    sa = int((s == 5).sum())
    a = int((s == 4).sum())
    u = int((s == 3).sum())
    d = int((s == 2).sum())
    sd = int((s == 1).sum())
    item_rows.append({"factor": f"Factor {i+1}", "label": FACTOR_LABELS[i],
                      "n": int(total), "SA_n": sa, "A_n": a, "U_n": u, "D_n": d, "SD_n": sd,
                      "SA_pct": round(sa/total*100, 1) if total else 0,
                      "A_pct": round(a/total*100, 1) if total else 0,
                      "SA_A_pct": round((sa+a)/total*100, 1) if total else 0})
pd.DataFrame(item_rows).to_csv(TAB_DIR / "D03_factors_sa_a.csv", index=False)

print("D03 saved")

# ============================================================
# D04 Health Implications (Objective 3)
# ============================================================
HEALTH_LABELS = ["Dependence/addiction", "Cardiovascular problems", "Respiratory problems",
    "Anxiety/depression/mental health", "Sleep disturbances",
    "Impaired concentration/memory", "Impaired judgement/decision-making",
    "Risky sexual behaviour", "Accidents/injuries",
    "Long-term organ damage", "Relationship problems", "Academic performance"]

HEALTH_DOMAINS = {
    "physical": [0, 1, 2, 8, 9],
    "psychological": [3, 4, 6],
    "social": [7, 10],
    "academic": [5, 11],
}

health_rows = []
for i, col in enumerate([f"health_{i+1:02d}" for i in range(12)]):
    label = HEALTH_LABELS[i] if i < len(HEALTH_LABELS) else f"Health {i+1}"
    s = df[col].dropna()
    health_rows.append({"health": f"Health {i+1}", "label": label,
                        "mean": round(s.mean(), 2), "sd": round(s.std(), 2),
                        "median": round(s.median(), 2), "n": int(s.notna().sum())})
pd.DataFrame(health_rows).to_csv(TAB_DIR / "D04_health_descriptive.csv", index=False)

# Health domains
domain_rows = []
for domain, idxs in HEALTH_DOMAINS.items():
    m = df[[f"health_{i+1:02d}" for i in idxs]].mean(axis=1)
    domain_rows.append({"domain": domain, "mean": round(m.mean(), 2), "sd": round(m.std(), 2),
                        "median": round(m.median(), 2), "n": int(m.notna().sum())})
pd.DataFrame(domain_rows).to_csv(TAB_DIR / "D04_health_domains.csv", index=False)

# Health item % SA/A
health_item_rows = []
for i, col in enumerate([f"health_{i+1:02d}" for i in range(12)]):
    label = HEALTH_LABELS[i] if i < len(HEALTH_LABELS) else f"Health {i+1}"
    s = pd.to_numeric(df[col], errors="coerce")
    total = s.notna().sum()
    sa = int((s == 5).sum()); a = int((s == 4).sum())
    health_item_rows.append({"health": f"Health {i+1}", "label": label, "n": int(total),
                             "SA_n": sa, "A_n": a, "SA_A_pct": round((sa+a)/total*100, 1) if total else 0})
pd.DataFrame(health_item_rows).to_csv(TAB_DIR / "D04_health_sa_a.csv", index=False)

print("D04 saved")

# ============================================================
# D05 Prevention Strategies (Objective 4)
# ============================================================
PREV_LABELS = ["Counselling/mental health", "Education/awareness campaigns",
    "Peer-led education/support", "University policies/disciplinary measures",
    "Early identification/screening/referral", "Parental/family involvement",
    "Religious/spiritual support", "Recreational/extracurricular activities"]

prev_rows = []
for i, col in enumerate([f"prev_{i+1:02d}" for i in range(8)]):
    label = PREV_LABELS[i] if i < len(PREV_LABELS) else f"Prevention {i+1}"
    s = df[col].dropna()
    prev_rows.append({"prevention": f"Prevention {i+1}", "label": label,
                      "mean": round(s.mean(), 2), "sd": round(s.std(), 2),
                      "median": round(s.median(), 2), "n": int(s.notna().sum())})
pd.DataFrame(prev_rows).to_csv(TAB_DIR / "D05_prevention_descriptive.csv", index=False)

# Prevention item % SA/A
prev_item_rows = []
for i, col in enumerate([f"prev_{i+1:02d}" for i in range(8)]):
    label = PREV_LABELS[i] if i < len(PREV_LABELS) else f"Prevention {i+1}"
    s = pd.to_numeric(df[col], errors="coerce")
    total = s.notna().sum()
    sa = int((s == 5).sum()); a = int((s == 4).sum())
    prev_item_rows.append({"prevention": f"Prevention {i+1}", "label": label, "n": int(total),
                           "SA_n": sa, "A_n": a, "SA_A_pct": round((sa+a)/total*100, 1) if total else 0})
pd.DataFrame(prev_item_rows).to_csv(TAB_DIR / "D05_prevention_sa_a.csv", index=False)

print("D05 saved")

# ============================================================
# D06 Reliability
# ============================================================
def cronbach(items_df):
    m = items_df.values.astype(float)
    m = m[~np.isnan(m).any(axis=1)]
    if m.shape[0] < 2 or m.shape[1] < 2: return np.nan, m.shape[0]
    k = m.shape[1]
    item_vars = m.var(axis=0, ddof=1).sum()
    total_var = m.sum(axis=1).var(ddof=1)
    if total_var == 0: return np.nan, m.shape[0]
    alpha = (k / (k - 1)) * (1 - item_vars / total_var)
    return alpha, m.shape[0]

factor_cols = [f"factor_{i+1:02d}" for i in range(13)]
health_cols = [f"health_{i+1:02d}" for i in range(12)]
prev_cols = [f"prev_{i+1:02d}" for i in range(8)]

alpha_f, n_f = cronbach(df[factor_cols])
alpha_h, n_h = cronbach(df[health_cols])
alpha_p, n_p = cronbach(df[prev_cols])

pd.DataFrame([{"scale": "Factors (13 items)", "alpha": round(alpha_f, 3), "n": n_f, "threshold": 0.70, "verdict": "Excellent" if alpha_f >= 0.9 else "Good" if alpha_f >= 0.8 else "Acceptable"},
              {"scale": "Health Implications (12 items)", "alpha": round(alpha_h, 3), "n": n_h, "threshold": 0.70, "verdict": "Excellent" if alpha_h >= 0.9 else "Good" if alpha_h >= 0.8 else "Acceptable"},
              {"scale": "Prevention Strategies (8 items)", "alpha": round(alpha_p, 3), "n": n_p, "threshold": 0.70, "verdict": "Excellent" if alpha_p >= 0.9 else "Good" if alpha_p >= 0.8 else "Acceptable"}]).to_csv(TAB_DIR / "D06_reliability.csv", index=False)
print("D06 saved")

# ============================================================
# D07 Bivariate: Ever Use × Demographics (Chi-square/Fisher)
# ============================================================
def chi2_test(outcome, group, data):
    d = data[[outcome, group]].dropna()
    if len(d) < 2: return {"comparison": f"{outcome} x {group}", "error": "insufficient data"}
    ct = pd.crosstab(d[outcome], d[group])
    if ct.size == 0: return {"comparison": f"{outcome} x {group}", "error": "empty crosstab"}
    chi2, p, dof, exp = chi2_contingency(ct)
    test = "Chi-square"
    if ct.shape == (2, 2) and (exp < 5).any():
        _, p = fisher_exact(ct)
        test = "Fisher exact"
    flag = "OK" if (exp >= 5).all() else "WARN: expected<5"
    v = np.sqrt(chi2 / (ct.values.sum() * (min(ct.shape) - 1))) if min(ct.shape) > 1 else np.nan
    return {"comparison": f"{outcome} x {group}", "test": test, "chi2": round(chi2, 3),
            "dof": int(dof), "p": round(float(p), 4), "cramers_v": round(float(v), 3),
            "validity": flag, "n": int(ct.values.sum()), "sig05": "Yes" if p < 0.05 else "No"}

demo_groups = ["sex_c", "level_c", "faculty_c", "religion_c", "living_c", "allowance_c", "age_c"]
outcomes = ["ever_use_c", "past_3mo_c", "problem_use", "any_substance_3mo"]

bivar_rows = []
for out in outcomes:
    for grp in demo_groups:
        res = chi2_test(out, grp, df)
        res["outcome"] = out
        res["group"] = grp
        bivar_rows.append(res)

pd.DataFrame(bivar_rows).to_csv(TAB_DIR / "D07_bivariate_demographics.csv", index=False)

# Detail row-% tables
for out in outcomes:
    for grp in demo_groups:
        d = df[[out, grp]].dropna()
        if len(d) > 0:
            pct = pd.crosstab(d[grp], d[out], normalize="index").round(3) * 100
            pct.to_csv(TAB_DIR / f"DX_{out}_x_{grp}.csv")

print("D07 saved")

# ============================================================
# D08 Factor/Health/Prevention scores by demographics (Kruskal-Wallis/MW)
# ============================================================
score_cols = ["factor_score", "factor_peer_social", "factor_academic", "factor_emotional",
              "factor_availability", "factor_family", "factor_social_media", "factor_boredom", "factor_policy",
              "health_score", "health_physical", "health_psychological", "health_social", "health_academic",
              "prev_score"]

group_cols = ["sex_c", "level_c", "faculty_c", "religion_c", "living_c", "allowance_c", "age_c"]

comp_rows = []
for score in score_cols:
    for grp in group_cols:
        d = df[[score, grp]].dropna()
        if len(d) < 2: continue
        groups = [d.loc[d[grp] == v, score].values for v in d[grp].unique() if len(d.loc[d[grp] == v, score]) > 0]
        if len(groups) < 2: continue
        if len(groups) == 2:
            stat, p = mannwhitneyu(groups[0], groups[1], alternative="two-sided")
            test = "Mann-Whitney U"
        else:
            stat, p = kruskal(*groups)
            test = "Kruskal-Wallis"
        comp_rows.append({"score": score, "group": grp, "test": test,
                          "stat": round(float(stat), 2), "p": round(float(p), 4),
                          "sig05": "Yes" if p < 0.05 else "No"})
pd.DataFrame(comp_rows).to_csv(TAB_DIR / "D08_score_by_demographics.csv", index=False)
print("D08 saved")

# ============================================================
# D09 Factor/Health/Prevention correlations (Spearman + Pearson)
# ============================================================
scales = df[["factor_score", "factor_peer_social", "factor_academic", "factor_emotional",
             "factor_availability", "factor_family", "factor_social_media", "factor_boredom", "factor_policy",
             "health_score", "health_physical", "health_psychological", "health_social", "health_academic",
             "prev_score"]].apply(pd.to_numeric, errors="coerce")

corr_rows = []
names = list(scales.columns)
for i in range(len(names)):
    for j in range(i+1, len(names)):
        x, y = scales[names[i]], scales[names[j]]
        rs, ps = spearmanr(x, y)
        rp, pp = pearsonr(x.dropna(), y.dropna()) if x.notna().sum() > 3 and y.notna().sum() > 3 else (np.nan, np.nan)
        corr_rows.append({"pair": f"{names[i]} vs {names[j]}",
                          "spearman_r": round(rs, 3), "spearman_p": round(ps, 4),
                          "pearson_r": round(rp, 3), "pearson_p": round(pp, 4),
                          "sig05": "Yes" if ps < 0.05 else "No"})
pd.DataFrame(corr_rows).to_csv(TAB_DIR / "D09_correlations.csv", index=False)

# Correlation matrix
scales.corr(method="spearman").round(3).to_csv(TAB_DIR / "D09b_spearman_matrix.csv")
scales.corr(method="pearson").round(3).to_csv(TAB_DIR / "D09c_pearson_matrix.csv")
print("D09 saved")

# ============================================================
# D10 Logistic Regression (Supplementary)
# ============================================================
import statsmodels.api as sm
from statsmodels.stats.outliers_influence import variance_inflation_factor

def fit_logit(data, y, predictors, label):
    d = data[[y] + predictors].dropna().copy()
    if len(d) < 10: return pd.DataFrame([{"model": label, "error": "insufficient data"}])
    # Normalize target to 0/1 regardless of dtype (str/object/int)
    yv = pd.to_numeric(d[y], errors="coerce")
    if yv.isna().any() or (yv.dropna() < 0).any() or (yv.dropna() > 1).any():
        yv = d[y].astype(str).str.strip().str.lower().map({"yes": 1, "no": 0, "1": 1, "0": 0})
    mask = yv.notna()
    if mask.sum() < 10: return pd.DataFrame([{"model": label, "error": "insufficient valid Y"}])
    d, yv = d[mask], yv[mask].astype(float)
    X = pd.get_dummies(d[predictors], drop_first=True, dtype=float)
    if X.shape[1] == 0: return pd.DataFrame([{"model": label, "error": "no predictors"}])
    X = sm.add_constant(X, has_constant="add")
    try:
        res = sm.Logit(yv, X).fit(disp=0, maxiter=100)
    except Exception as e:
        return pd.DataFrame([{"model": label, "error": str(e)[:200]}])
    ci = res.conf_int()
    out = pd.DataFrame({"model": label, "term": res.params.index,
                        "aOR": np.exp(res.params).round(3),
                        "ci_lo": np.exp(ci[0]).round(3), "ci_hi": np.exp(ci[1]).round(3),
                        "p": res.pvalues.round(4)})
    out["sig05"] = np.where(out["p"] < 0.05, "Yes", "No")
    return out

# Predictors (merge sparse categories)
df["age_c2"] = np.where(df["age_c"].isin(["16-18 years", "19-21 years"]), "16-21", "22+")
df["level_c2"] = np.where(df["level_c"].isin(["100 Level", "200 Level"]), "100/200", 
                          np.where(df["level_c"].isin(["300 Level", "400 Level"]), "300/400", "Other"))
df["allowance_c2"] = np.where(df["allowance_c"].isin(["Less than ₦20,000", "₦20,000–₦39,999"]), "Low (<₦40k)", 
                              np.where(df["allowance_c"].isin(["₦40,000–₦59,999", "₦60,000–₦79,999"]), "Medium", "High"))

PRED = ["sex_c", "age_c2", "level_c2", "faculty_c", "living_c", "allowance_c2"]

# Model 1: Ever use
m1 = fit_logit(df, "ever_use_c", PRED, "M1: Ever use (binary logistic)")
# Model 2: Past 3mo use
m2 = fit_logit(df, "past_3mo_c", PRED, "M2: Past 3mo use")
# Model 3: Problem use
m3 = fit_logit(df, "problem_use", PRED, "M3: Problem use (CAGE-type)")
# Model 4: Any substance 3mo
m4 = fit_logit(df, "any_substance_3mo", PRED, "M4: Any substance past 3mo")

pd.concat([m1, m2, m3, m4], ignore_index=True).to_csv(TAB_DIR / "D10_logistic_models.csv", index=False)
print("D10 saved")

print("\nALL STATISTICS DONE")