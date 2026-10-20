"""FUHSI KAP study — Phase 2: statistics per thesis §3.11 (descriptives, chi-square,
Pearson) + clearly-labelled supplemental analyses.
Run:  .venv/bin/python kap_step2_stats.py
Input:  data/processed/kap_cleaned_full.csv, data/processed/kap_item_labels.json
Output: reports/output/tables/T01..T11*.csv
"""
from pathlib import Path
import json
import warnings
import numpy as np
import pandas as pd
from scipy.stats import chi2_contingency, fisher_exact, pearsonr, spearmanr, kruskal, mannwhitneyu
from scipy.stats import chi2 as chi2dist

warnings.filterwarnings("ignore")

BASE = Path(__file__).resolve().parent
CLEAN = BASE / "data" / "processed" / "kap_cleaned_full.csv"
TAB = BASE / "reports" / "output" / "tables"
TAB.mkdir(parents=True, exist_ok=True)

df = pd.read_csv(CLEAN, dtype=str, keep_default_na=False)
df["age_num"] = pd.to_numeric(df["age_num"], errors="coerce")
df["level_num"] = pd.to_numeric(df["level_num"], errors="coerce")
df["know_score"] = pd.to_numeric(df["know_score"], errors="coerce")
df["know_pct"] = pd.to_numeric(df["know_pct"], errors="coerce")
df["att_score"] = pd.to_numeric(df["att_score"], errors="coerce")
for c in df.columns:
    if c.startswith("A") and c.endswith("__n"):
        df[c] = pd.to_numeric(df[c], errors="coerce")
    if c.startswith("E") and c.endswith("__n"):
        df[c] = pd.to_numeric(df[c], errors="coerce")
    if c.startswith("hbm_"):
        df[c] = pd.to_numeric(df[c], errors="coerce")
    if c == "type_n":
        df[c] = pd.to_numeric(df[c], errors="coerce")

L = json.loads((BASE / "data" / "processed" / "kap_item_labels.json").read_text())
N = len(df)
GROUPS = list(L["hbm_groups"].keys())
HBMVARS = [f"hbm_{g}" for g in GROUPS]

def freq(s, order=None):
    vc = s.value_counts()
    if order:
        vc = vc.reindex([o for o in order if o in vc.index])
    t = pd.DataFrame({"category": vc.index, "n": vc.values})
    t["pct"] = (t["n"] / len(s) * 100).round(1)
    return t

# ---------------------------------------------------------------- T01 demographics
rows = []
def add(rows, var, sub):
    for _, r in sub.iterrows():
        rows.append({"section": var, "category": r.iloc[0], "n": int(r["n"]), "pct": r["pct"]})

d_ageband = freq(df["age_band"], ["16-20 years", "21-24 years", "25-30 years", "Above 30 years", "Not stated"])
add(rows, "Age group", d_ageband)
rows.append({"section": "Age (completed years, exact n=164)", "category": "Mean +/- SD",
             "n": round(df["age_num"].mean(), 2), "pct": round(df["age_num"].std(), 2)})
d_level = freq(df["level_c"], ["100 level", "200 level", "300 level", "400 level"])
add(rows, "Level", d_level)
d_mar = freq(df["marital_c"])
add(rows, "Marital status", d_mar)
d_eth = freq(df["ethnicity_c"])
add(rows, "Ethnicity", d_eth)
d_men = freq(df["menarche_c"], ["Below 9 years", "9-13 years", "13-18 years", "18 years and above"])
add(rows, "Age at menarche", d_men)
rows.append({"section": "Department", "category": df["dept_c"].value_counts().index[0],
             "n": int(df["dept_c"].value_counts().iloc[0]), "pct": ""})
t01a = pd.DataFrame(rows)

dept = df["dept_c"].value_counts().reset_index()
dept.columns = ["department", "n"]
dept["pct"] = (dept["n"] / N * 100).round(1)
t01a.to_csv(TAB / "T01a_demographics_categorical.csv", index=False)
dept.to_csv(TAB / "T01b_departments.csv", index=False)

# ---------------------------------------------------------------- T02 knowledge
K_N = ["K1", "K2", "K3", "K4", "K5", "K6", "K7", "K8", "K9", "K10", "K11", "K12"]
rows = []
for i in range(12):
    v = df[f"K{i+1}"]
    rows.append({"item": f"K{i+1}", "statement": L["k"][i],
                 "correct_answer": L["k_key"][str(i)],
                 "correct_n": int((v == L["k_key"][str(i)]).sum()),
                 "correct_pct": round((v == L["k_key"][str(i)]).mean() * 100, 1),
                 "incorrect_n": int((v == ("False" if L["k_key"][str(i)] == "True" else "True")).sum()),
                 "incorrect_pct": round((v == ("False" if L["k_key"][str(i)] == "True" else "True")).mean() * 100, 1),
                 "dont_know_n": int((v == "Don't know").sum()),
                 "dont_know_pct": round((v == "Don't know").mean() * 100, 1)})
pd.DataFrame(rows).to_csv(TAB / "T02a_knowledge_items.csv", index=False)

summ = pd.DataFrame([
    {"summary": "Knowledge score (0-12)", "mean": round(df["know_score"].mean(), 2),
     "sd": round(df["know_score"].std(), 2), "median": df["know_score"].median(),
     "min": df["know_score"].min(), "max": df["know_score"].max()},
    {"summary": "Knowledge % (0-100)", "mean": round(df["know_pct"].mean(), 2),
     "sd": round(df["know_pct"].std(), 2), "median": round(df["know_pct"].median(), 2),
     "min": round(df["know_pct"].min(), 1), "max": round(df["know_pct"].max(), 1)}])
mean_row = pd.DataFrame([{"summary": f"Mean split (>= {round(df['know_score'].mean(),2)})",
                          "Good": int((df["know_cat_mean"] == "Good").sum()),
                          "Poor": int((df["know_cat_mean"] == "Poor").sum())},
                         {"summary": f"Median split (>= {round(df['know_score'].median(),2)})",
                          "Good": int((df["know_cat_median"] == "Good").sum()),
                          "Poor": int((df["know_cat_median"] == "Poor").sum())}])
mean_row.to_csv(TAB / "T02b_knowledge_scores.csv", index=False)
summ.to_csv(TAB / "T02c_knowledge_summary.csv", index=False)

# ---------------------------------------------------------------- T03 attitude (5-point scale as fielded)
LIK_ORDER = ["SA", "A", "U", "D", "SD"]
rows = []
for i in range(10):
    v = df[f"A{i+1}_raw"].str.strip().str.upper()
    r = {"item": f"A{i+1}", "statement": L["a"][i],
         "reverse_scored": "yes" if i in L["a_rev"] else "no"}
    for lv in LIK_ORDER:
        r[lv + "_n"] = int((v == lv).sum())
        r[lv + "_pct"] = round((v == lv).mean() * 100, 1)
    r["mean_1to5"] = round(df[f"A{i+1}__n"].mean(), 2)
    rows.append(r)
pd.DataFrame(rows).to_csv(TAB / "T03a_attitude_items.csv", index=False)

at_mean, at_med = df["att_score"].mean(), df["att_score"].median()
summ = pd.DataFrame([
    {"summary": "Attitude score (10-50)", "mean": round(at_mean, 2), "sd": round(df["att_score"].std(), 2),
     "median": at_med, "min": df["att_score"].min(), "max": df["att_score"].max()},
    {"summary": f"Mean split (>= {round(at_mean,2)}) Positive n/{N}", "Positive": int((df["att_cat_mean"] == "Positive").sum()),
     "Negative": int((df["att_cat_mean"] == "Negative").sum())},
    {"summary": f"Median split (>= {round(at_med,2)}) Positive n/{N}", "Positive": int((df["att_cat_median"] == "Positive").sum()),
     "Negative": int((df["att_cat_median"] == "Negative").sum())}])
summ.to_csv(TAB / "T03b_attitude_scores.csv", index=False)

# ---------------------------------------------------------------- T04 HBM
rows = []
for i in range(14):
    v = df[f"E{i+1}_raw"].str.strip().str.upper()
    r = {"item": f"E{i+1}", "statement": L["hbm"][i]}
    grp = [g for g, ii in L["hbm_groups"].items() if i + 1 in ii][0]
    r["hbm_domain"] = grp
    for lv in LIK_ORDER:
        r[lv + "_n"] = int((v == lv).sum())
        r[lv + "_pct"] = round((v == lv).mean() * 100, 1)
    r["mean_1to5"] = round(df[f"E{i+1}__n"].mean(), 2)
    rows.append(r)
pd.DataFrame(rows).to_csv(TAB / "T04a_hbm_items.csv", index=False)

rows = []
for g in GROUPS:
    rows.append({"subscale": g, "items": len(L["hbm_groups"][g]),
                 "mean": round(df[f"hbm_{g}"].mean(), 2), "sd": round(df[f"hbm_{g}"].std(), 2),
                 "median": round(df[f"hbm_{g}"].median(), 2),
                 "cronbach_alpha": round(L["alphas"][f"hbm_{g}"], 2)})
pd.DataFrame(rows).to_csv(TAB / "T04b_hbm_subscales.csv", index=False)

# ---------------------------------------------------------------- T05 HSB battery
exp_yes = df[df["exp_c"] == "Yes"]

freq(df["exp_c"]).assign(variable="experienced_any_MIs").to_csv(TAB / "T05a_experienced.csv", index=False)

type_rows = df["type_list"][df["type_list"] != ""].str.split(";").explode()
tc = type_rows.value_counts()
t = pd.DataFrame({"type_of_irregularity": tc.index, "mentions": tc.values})
t["pct_of_285_reporting"] = (t["mentions"] / (df["type_list"] != "").sum() * 100).round(1)
t["pct_of_N376"] = (t["mentions"] / N * 100).round(1)
t.to_csv(TAB / "T05b_types.csv", index=False)

act = freq(exp_yes["action_c"])
act.assign(variable="first_action_among_experienced").to_csv(TAB / "T05c_first_action.csv", index=False)

tl = freq(exp_yes["time_c"])
s = freq(exp_yes["sought_ever"])
(pd.concat([tl.assign(variable="time_to_seek_help").rename(columns={"category": "value"}),
            s.assign(variable="ever_sought_professional_help").rename(columns={"category": "value"})],
           ignore_index=True)).to_csv(TAB / "T05d_timeliness.csv", index=False)

info_rows = df["info_list"][df["info_list"] != ""].str.split(";").explode()
ic = info_rows.value_counts()
t = pd.DataFrame({"source": ic.index, "mentions": ic.values})
t["pct_of_376"] = (t["mentions"] / N * 100).round(1)
t.to_csv(TAB / "T05e_info_sources.csv", index=False)

freq(df["campus_c"]).assign(variable="ever_visited_campus_health_center").to_csv(
    TAB / "T05f_campus_health_center.csv", index=False)
freq(df["facility_c"]).assign(variable="preferred_facility").to_csv(
    TAB / "T05g_preferred_facility.csv", index=False)

fu = freq(df["future_c"], ["Yes", "Not sure", "No"])
fu.assign(variable="would_seek_professional_help_in_future").to_csv(
    TAB / "T05h_future_intent.csv", index=False)

bar_rows = df["barrier_list"][df["barrier_list"] != ""].str.split(";").explode()
bc = bar_rows.value_counts()
t = pd.DataFrame({"barrier": bc.index, "mentions": bc.values})
t["pct_of_376"] = (t["mentions"] / N * 100).round(1)
t.to_csv(TAB / "T05i_barriers.csv", index=False)

# ---------------------------------------------------------------- T06 chi-square (document-mandated tests)
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

know_m = df["know_cat_mean"]
df["future2"] = np.where(df["future_c"] == "Yes", "Yes", "Not sure / No")
df["know2"] = df["know_cat_mean"]
df["att2"] = df["att_cat_mean"]
rows = []
rows.append(chi2_run("H1 primary (3-cat)", "know_cat_mean", "future_c",
                     note="knowledge(mean split) x future intent, 3 levels"))
rows.append(chi2_run("H1 primary (binary)", "know2", "future2",
                     note="knowledge(Good/Poor) x would seek (Yes vs Not sure/No)"))
rows.append(chi2_run("H1 secondary", "know_cat_mean", "sought_ever",
                     subset=df["exp_c"] == "Yes", note="knowledge x ever sought help, experienced only"))
rows.append(chi2_run("H2 primary (3-cat)", "att_cat_mean", "future_c",
                     note="attitude(mean split) x future intent, 3 levels"))
rows.append(chi2_run("H2 primary (binary)", "att2", "future2",
                     note="attitude(Positive/Negative) x would seek (Yes vs Not sure/No)"))
rows.append(chi2_run("H2 secondary", "att_cat_mean", "sought_ever",
                     subset=df["exp_c"] == "Yes", note="attitude x ever sought help, experienced only"))
pd.DataFrame(rows).to_csv(TAB / "T06a_hypotheses_chi_square.csv", index=False)

DEPT_GROUP = {"MBBS": "Clinical", "Nursing": "Clinical", "MLS": "Clinical"}
df["dept_group"] = df["dept_c"].map(DEPT_GROUP).fillna("Non-clinical")
df["eth_group"] = np.where(df["ethnicity_c"] == "Yoruba", "Yoruba", "Other")
df["age_grp"] = np.select([df["age_band"] == "16-20 years", df["age_band"] == "21-24 years"],
                          ["16-20", "21-24"], default="25+")
tel = df["exp_c"] == "Yes"
rows = []
for score in ["know_cat_mean", "att_cat_mean"]:
    for demo in ["level_c", "age_grp", "dept_group", "eth_group"]:
        rows.append(chi2_run("Score category x demographics", score, demo))
for demo in ["level_c", "age_grp", "dept_group", "eth_group"]:
    rows.append(chi2_run("HSB variable x demographics", "future_c", demo))
    rows.append(chi2_run("Sought help x demographics", "sought_ever", demo,
                         subset=tel, note="experienced only"))
pd.DataFrame(rows).to_csv(TAB / "T06b_demographic_chi_square.csv", index=False)

# ---------------------------------------------------------------- T07 Pearson correlations
VARS = ["age_num", "level_num", "know_score", "att_score"] + HBMVARS
sub = df[VARS]
out_r = pd.DataFrame(index=VARS, columns=VARS, dtype=float)
out_p = out_r.copy()
out_n = out_r.copy()
for a in VARS:
    for b in VARS:
        pair = sub[[a, b]].dropna()
        n = len(pair)
        out_n.loc[a, b] = n
        if n >= 3:
            r = pearsonr(pair[a], pair[b])
            out_r.loc[a, b] = round(float(np.asarray(r[0]).flatten()[0]), 3)
            out_p.loc[a, b] = round(float(np.asarray(r[1]).flatten()[0]), 4)
out_r.round(2).to_csv(TAB / "T07a_pearson_r.csv")
out_p.to_csv(TAB / "T07b_pearson_p.csv")
out_n.to_csv(TAB / "T07c_pearson_n.csv")

# ---------------------------------------------------------------- SUPPLEMENTARY S01: Bloom grading
rows = []
grade = np.where(df["know_pct"] >= 70, "Good (>=70%)",
                 np.where(df["know_pct"] >= 50, "Moderate (50-69.9%)", "Poor (<50%)"))
grade50 = np.where(df["know_pct"] >= 50, "Adequate (>=50%)", "Inadequate (<50%)")
rows.append({"level": "Bloom grade (supplementary)", "category": "Good (>=70%)",
             "n": int((grade == "Good (>=70%)").sum()),
             "pct": round((grade == "Good (>=70%)").mean() * 100, 1)})
rows.append({"level": "Bloom grade (supplementary)", "category": "Moderate (50-69.9%)",
             "n": int((grade == "Moderate (50-69.9%)").sum()),
             "pct": round((grade == "Moderate (50-69.9%)").mean() * 100, 1)})
rows.append({"level": "Bloom grade (supplementary)", "category": "Poor (<50%)",
             "n": int((grade == "Poor (<50%)").sum()),
             "pct": round((grade == "Poor (<50%)").mean() * 100, 1)})
rows.append({"level": "Adequacy (supplementary)", "category": "Adequate (>=50%)",
             "n": int((grade50 == "Adequate (>=50%)").sum()),
             "pct": round((grade50 == "Adequate (>=50%)").mean() * 100, 1)})
pd.DataFrame(rows).to_csv(TAB / "S01_bloom_grades_supplementary.csv", index=False)

# ---------------------------------------------------------------- SUPPLEMENTARY S02: Spearman matrix
out_s = pd.DataFrame(index=VARS, columns=VARS, dtype=float)
out_sp = out_s.copy()
for a in VARS:
    for b in VARS:
        pair = sub[[a, b]].dropna()
        if len(pair) >= 3:
            rs = spearmanr(pair[a], pair[b])
            out_s.loc[a, b] = round(float(np.asarray(rs[0]).flatten()[0]), 3)
            out_sp.loc[a, b] = round(float(np.asarray(rs[1]).flatten()[0]), 4)
out_s.round(2).to_csv(TAB / "S02a_spearman_r_supplementary.csv")
out_sp.to_csv(TAB / "S02b_spearman_p_supplementary.csv")

# ---------------------------------------------------------------- SUPPLEMENTARY S03: group comparisons
rows = []
def kw(name, var, groups, labels):
    g = [df.loc[df[groups] == lv, var].dropna() for lv in sorted(set(df[groups].dropna()))]
    g = [x for x in g if len(x) > 1]
    if len(g) > 1:
        s, p = kruskal(*g)
        rows.append({"comparison": name, "groups": groups, "variable": var,
                     "test": "Kruskal-Wallis", "stat": round(s, 3), "p": round(p, 4)})

def mw(name, var, gcol):
    d = df[[var, gcol]].dropna()
    vals = sorted(d[gcol].unique())
    if len(vals) != 2:
        return
    x, y = d.loc[d[gcol] == vals[0], var], d.loc[d[gcol] == vals[1], var]
    if len(x) > 1 and len(y) > 1:
        s, p = mannwhitneyu(x, y, alternative="two-sided")
        rows.append({"comparison": f"{vals[0]} vs {vals[1]}", "groups": gcol, "variable": var,
                     "test": "Mann-Whitney", "stat": round(s, 1), "p": round(p, 4)})

for var in ["know_score", "att_score", "hbm_barrier"]:
    kw(f"By level", var, "level_c", None)
    kw(f"By age group", var, "age_grp", None)
    kw(f"By dept-group", var, "dept_group", None)
    mw(f"By experience", var, "exp_c")
    kw(f"By future intent", var, "future_c", None)
    mw(f"By ever sought help", var, "sought_ever")
pd.DataFrame(rows).to_csv(TAB / "S03_group_comparisons_supplementary.csv", index=False)

# ---------------------------------------------------------------- SUPPLEMENTARY S04: logistic
try:
    import statsmodels.api as sm
    X = df[["know_score", "att_score", "hbm_barrier"]].copy()
    X["age_21_24"] = (df["age_grp"] == "21-24").astype(int)
    X["age_25plus"] = (df["age_grp"] == "25+").astype(int)
    X["level_per100"] = df["level_num"] / 100
    X["const"] = 1
    ybin = (df["future_c"] == "Yes").astype(int)
    keep = X.notna().all(axis=1)
    xl, yl = X[keep], ybin[keep]
    logit = sm.Logit(yl, xl).fit(disp=0)
    conf = logit.conf_int()
    rows = [{"predictor": i, "OR": round(np.exp(logit.params[i]), 2),
             "CI_low": round(np.exp(conf.loc[i, 0]), 2), "CI_high": round(np.exp(conf.loc[i, 1]), 2),
             "p": round(logit.pvalues[i], 4)} for i in xl.columns]
    t = pd.DataFrame(rows)
    t.insert(0, "model", "future help-seeking intent, n=%d" % len(yl))
    t["note"] = "supplementary"
    t.to_csv(TAB / "S04_logistic_future_intent_supplementary.csv", index=False)
    print("logit nukes:", t.to_string(index=False))
except Exception as e:
    print("logistic skipped:", e)

# ---------------------------------------------------------------- verification
print("\n--- STEP2 VERIFICATION ---")
print("N:", N)
print(pd.read_csv(TAB / "T06a_hypotheses_chi_square.csv").to_string(index=False))
print("Pearson r matrix diagonal:")
print(pd.read_csv(TAB / "T07a_pearson_r.csv", index_col=0).values[:4, :4])
print("Saved tables:", sorted(p.name for p in TAB.glob("*.csv")))
