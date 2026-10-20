"""Substance Abuse Study — Step 3: visualizations (16 charts).
Run: cd "/home/garba-the-analyst/Desktop/Projects/Data analysis " && /home/garba-the-analyst/.venvs/global/bin/python sub_step3_figures.py
"""
import warnings
import os
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter

warnings.filterwarnings("ignore")
sns.set_theme(style="whitegrid")
plt.rcParams.update({"figure.dpi": 120, "savefig.bbox": "tight", "savefig.dpi": 150, "font.size": 9})
PAL = sns.color_palette("viridis", 8)
CAT = sns.color_palette("Set2")

PROJECT_ROOT = "/home/garba-the-analyst/Desktop/Projects/Data analysis "
os.chdir(PROJECT_ROOT)

df = pd.read_csv("data/processed/substance_abuse_cleaned_full.csv", dtype=str, keep_default_na=False)
# Restore numeric
num_cols = [c for c in df.columns if c.startswith("factor_") or c.startswith("health_") or c.startswith("prev_") or c in ["freq_c", "problem_use", "any_substance_3mo"] or c.endswith("_score")]
for c in num_cols:
    if c in df.columns:
        df[c] = pd.to_numeric(df[c], errors="coerce")

FACTOR_LABELS = ["Peer pressure", "Academic stress", "Curiosity/experimentation",
    "Easy availability", "Family member use", "Social media exposure",
    "Emotional distress", "Coping with pain/stress/sleep",
    "Social gatherings/parties", "Low self-esteem",
    "Limited parental monitoring", "Boredom/unstructured time",
    "Inadequate policy enforcement"]

HEALTH_LABELS = ["Dependence/addiction", "Cardiovascular problems", "Respiratory problems",
    "Anxiety/depression/mental health", "Sleep disturbances",
    "Impaired concentration/memory", "Impaired judgement/decision-making",
    "Risky sexual behaviour", "Accidents/injuries",
    "Long-term organ damage", "Relationship problems", "Academic performance"]

PREV_LABELS = ["Counselling/mental health", "Education/awareness campaigns",
    "Peer-led education/support", "University policies/disciplinary measures",
    "Early identification/screening/referral", "Parental/family involvement",
    "Religious/spiritual support", "Recreational/extracurricular activities"]

N = len(df)
FIG_DIR = Path("reports/output/figures")
FIG_DIR.mkdir(parents=True, exist_ok=True)

def save(name):
    plt.savefig(FIG_DIR / name)
    plt.close()
    print("saved", name)

# ============================ F01 Sampling fidelity ============================
# Faculty population vs achieved
fac_pop = {"Science": 932, "Allied Health Sciences": 1640, 
           "Basic Medical Sciences": 371, "Clinical Sciences": 389}
# From proposal Table 2 (proportionate allocation of 359)
fac_quota = {"Science": 100, "Allied Health Sciences": 176,
             "Basic Medical Sciences": 40, "Clinical Sciences": 42}
fac_ach = df["faculty_c"].value_counts().to_dict()

fig, ax = plt.subplots(1, 2, figsize=(11, 4))
fac_list = list(fac_pop.keys())
x = np.arange(len(fac_list))
ax[0].bar(x - 0.2, [fac_quota.get(f, 0) for f in fac_list], 0.4, label="Quota (n=359)", color=PAL[0])
ax[0].bar(x + 0.2, [fac_ach.get(f, 0) for f in fac_list], 0.4, label=f"Achieved (n={N})", color=PAL[1])
ax[0].set_xticks(x)
ax[0].set_xticklabels(["Science", "Allied Health", "Basic Medical", "Clinical"], fontsize=8)
ax[0].set_ylabel("Respondents")
ax[0].set_title("Faculty quota vs achieved")
ax[0].legend(fontsize=8)

# Response rate
distributed = 395
ax[1].pie([N, distributed - N], labels=[f"Achieved ({N})", f"Shortfall ({distributed - N})"],
          colors=[PAL[2], "#e0e0e0"], startangle=90, wedgeprops=dict(width=0.45))
ax[1].set_title(f"Response rate: {N}/{distributed} ({N/distributed*100:.1f}%)")
fig.suptitle("F01 — Sampling fidelity")
save("sub_F01_sampling.png")

# ============================ F02 Demographics ============================
fig, ax = plt.subplots(2, 2, figsize=(11, 8))
# Sex
s = df["sex_c"].value_counts()
ax[0,0].pie(s.values, labels=[f"{i} ({v/N*100:.1f}%)" for i,v in zip(s.index, s.values)],
            colors=[PAL[0], PAL[1]], startangle=90, wedgeprops=dict(width=0.45))
ax[0,0].set_title("Sex")
# Age
o = df["age_c"].value_counts().reindex(["16-18 years", "19-21 years", "22-24 years", "25 years and above"])
ax[0,1].bar(o.index, o.values, color=PAL)
ax[0,1].set_title("Age band")
ax[0,1].tick_params(axis="x", rotation=15, labelsize=8)
# Level
o = df["level_c"].value_counts().reindex(["100 Level", "200 Level", "300 Level", "400 Level", "500 Level"])
ax[1,0].bar(o.index, o.values, color=PAL[::-1])
ax[1,0].set_title("Level of study")
ax[1,0].tick_params(axis="x", rotation=15, labelsize=8)
# Faculty
o = df["faculty_c"].value_counts()
ax[1,1].barh(o.index, o.values, color=PAL[2])
ax[1,0].set_ylabel("Respondents")
ax[1,1].set_title("Faculty")
fig.suptitle("F02 — Demographics")
save("sub_F02_demographics.png")

# ============================ F03 Substance use cascade ============================
fig, ax = plt.subplots(1, 2, figsize=(11, 4))
# Ever use
eu = df["ever_use_c"].value_counts()
ax[0].pie(eu.values, labels=[f"{i} ({v/N*100:.1f}%)" for i,v in zip(eu.index, eu.values)],
          colors=[PAL[0], "#e0e0e0"], startangle=90, wedgeprops=dict(width=0.45))
ax[0].set_title("Ever used any psychoactive substance")
# Past 3 months
p3 = df["past_3mo_c"].replace("", "No").value_counts()
ax[1].pie(p3.values, labels=[f"{i} ({v/N*100:.1f}%)" for i,v in zip(p3.index, p3.values)],
          colors=[PAL[1], "#e0e0e0"], startangle=90, wedgeprops=dict(width=0.45))
ax[1].set_title("Used in past 3 months")
fig.suptitle("F03 — Substance use cascade (n=132)")
save("sub_F03_cascade.png")

# ============================ F04 Substance-specific prevalence ============================
import ast
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
subs = list(sub_counts.keys())
vals = [sub_counts[s] for s in subs]

fig, ax = plt.subplots(figsize=(10, 5))
ax.barh(subs, vals, color=PAL[2])
ax.set_xlabel(f"Mentions (n={N})")
ax.set_title("F04 — Substances used in past 3 months (multi-response)")
for i, v in enumerate(vals):
    ax.text(v + 0.2, i, f"{v} ({v/N*100:.1f}%)", va="center", fontsize=8)
save("sub_F04_substances.png")

# ============================ F05 Frequency of use ============================
freq_num = pd.to_numeric(df["freq_c"], errors="coerce")
freq_labels = ["Never/Not applicable/Not stated", "Less than once a week",
               "1–2 times per week", "3–6 times per week"]
df["freq_label"] = freq_num.map({0: freq_labels[0], 1: freq_labels[1],
                                 2: freq_labels[2], 3: freq_labels[3]})
df["freq_label"] = df["freq_label"].fillna(freq_labels[0])
fo = df["freq_label"].value_counts().reindex(freq_labels)
fig, ax = plt.subplots(figsize=(9, 4))
ax.bar(range(len(fo)), fo.values, color=PAL[3])
ax.set_xticks(range(len(fo)))
ax.set_xticklabels(fo.index, rotation=20, ha="right", fontsize=8)
ax.set_title("F05 — Frequency of most-used substance (past 30 days)")
for i, v in enumerate(fo.values):
    ax.text(i, v + 1, f"{v} ({v/N*100:.1f}%)", ha="center", fontsize=8)
ax.set_ylabel("Respondents")
save("sub_F05_frequency.png")

# ============================ F06 Influencing factors ranking ============================
FACTOR_LABELS = ["Peer pressure", "Academic stress", "Curiosity/experimentation",
    "Easy availability", "Family member use", "Social media exposure",
    "Emotional distress", "Coping with pain/stress/sleep",
    "Social gatherings/parties", "Low self-esteem",
    "Limited parental monitoring", "Boredom/unstructured time",
    "Inadequate policy enforcement"]

LIKERT_MAP = {"SA": 5, "A": 4, "U": 3, "D": 2, "SD": 1}
def norm_likert(s):
    s = str(s).strip().upper()
    return {"SA": 5, "A": 4, "U": 3, "D": 2, "SD": 1}.get(s, np.nan)

factor_cols = [f"factor_{i+1:02d}" for i in range(13)]
sa_a_pct = []
for i, col in enumerate([f"factor_{i+1:02d}" for i in range(13)]):
    s_num = pd.to_numeric(df[col], errors="coerce")
    total = s_num.notna().sum()
    sa_a = int((s_num == 5).sum() + (s_num == 4).sum())
    sa_a_pct.append(round(sa_a / total * 100, 1) if total else 0)

fig, ax = plt.subplots(figsize=(9, 6))
order = np.argsort(sa_a_pct)
ax.barh(np.array(FACTOR_LABELS)[order], np.array(sa_a_pct)[order], color=PAL[4])
ax.set_xlabel("% Strongly Agree + Agree")
ax.set_title("F06 — Factors influencing substance abuse (% SA + A)")
for i, v in enumerate(np.array(sa_a_pct)[order]):
    ax.text(v + 1, i, f"{v:.1f}%", va="center", fontsize=8)
ax.set_xlim(0, 110)
save("sub_F06_factors_ranking.png")

# ============================ F07 Factors Likert stacked ============================
fig, ax = plt.subplots(figsize=(9, 6))
mat = np.array([[(pd.to_numeric(df[f"factor_{i+1:02d}"], errors="coerce") == v).sum() / N * 100
                 for v in [5, 4, 3, 2, 1]] for i in range(13)])
cols = {"SA": "#1a9850", "A": "#a6d96a", "U": "#ffffbf", "D": "#fdae61", "SD": "#d73027"}
LKV = {"SA": 5, "A": 4, "U": 3, "D": 2, "SD": 1}
left = np.zeros(13)
for j, lv in enumerate(["SA", "A", "U", "D", "SD"]):
    ax.barh(FACTOR_LABELS, mat[:, j], left=left, label=lv, color=cols[lv])
    left += mat[:, j]
ax.set_xlabel("% of respondents")
ax.set_title("F07 — Factors: full response mix")
ax.legend(ncol=5, loc="lower center", bbox_to_anchor=(0.5, -0.15), fontsize=8)
save("sub_F07_factors_stacked.png")

# ============================ F08 Health implications ranking ============================
HEALTH_LABELS = ["Dependence/addiction", "Cardiovascular problems", "Respiratory problems",
    "Anxiety/depression/mental health", "Sleep disturbances",
    "Impaired concentration/memory", "Impaired judgement/decision-making",
    "Risky sexual behaviour", "Accidents/injuries",
    "Long-term organ damage", "Relationship problems", "Academic performance"]

sa_a_pct_h = []
for i, col in enumerate([f"health_{i+1:02d}" for i in range(12)]):
    s_num = pd.to_numeric(df[col], errors="coerce")
    total = s_num.notna().sum()
    sa_a = int((s_num == 5).sum() + (s_num == 4).sum())
    sa_a_pct_h.append(round(sa_a / total * 100, 1) if total else 0)

fig, ax = plt.subplots(figsize=(9, 6))
order = np.argsort(sa_a_pct_h)
ax.barh(np.array(HEALTH_LABELS)[order], np.array(sa_a_pct_h)[order], color=PAL[1])
ax.set_xlabel("% Strongly Agree + Agree")
ax.set_title("F08 — Perceived health implications (% SA + A)")
for i, v in enumerate(np.array(sa_a_pct_h)[order]):
    ax.text(v + 1, i, f"{v:.1f}%", va="center", fontsize=8)
ax.set_xlim(0, 110)
save("sub_F08_health_ranking.png")

# ============================ F09 Health domains ============================
fig, ax = plt.subplots(figsize=(8, 4))
domains = ["physical", "psychological", "social", "academic"]
means = [df[f"health_{d}"].mean() for d in domains]
sds = [df[f"health_{d}"].std() for d in domains]
ax.bar(domains, means, yerr=sds, capsize=4, color=PAL[:4])
ax.set_ylabel("Mean (1-5)")
ax.set_title("F09 — Health implication domains (mean ± SD)")
for i, (m, s) in enumerate(zip(means, sds)):
    ax.text(i, m + s + 0.05, f"{m:.2f}", ha="center", fontsize=8)
save("sub_F09_health_domains.png")

# ============================ F10 Prevention strategies ranking ============================
PREV_LABELS = ["Counselling/mental health", "Education/awareness campaigns",
    "Peer-led education/support", "University policies/disciplinary measures",
    "Early identification/screening/referral", "Parental/family involvement",
    "Religious/spiritual support", "Recreational/extracurricular activities"]

sa_a_pct_p = []
for i, col in enumerate([f"prev_{i+1:02d}" for i in range(8)]):
    s_num = pd.to_numeric(df[col], errors="coerce")
    total = s_num.notna().sum()
    sa_a = int((s_num == 5).sum() + (s_num == 4).sum())
    sa_a_pct_p.append(round(sa_a / total * 100, 1) if total else 0)

fig, ax = plt.subplots(figsize=(9, 5))
order = np.argsort(sa_a_pct_p)
ax.barh(np.array(PREV_LABELS)[order], np.array(sa_a_pct_p)[order], color=PAL[3])
ax.set_xlabel("% Strongly Agree + Agree")
ax.set_title("F10 — Prevention strategies (% SA + A)")
for i, v in enumerate(np.array(sa_a_pct_p)[order]):
    ax.text(v + 1, i, f"{v:.1f}%", va="center", fontsize=8)
ax.set_xlim(0, 110)
save("sub_F10_prevention_ranking.png")

# ============================ F10b Prevention stacked ============================
fig, ax = plt.subplots(figsize=(9, 5))
mat = np.array([[(pd.to_numeric(df[f"prev_{i+1:02d}"], errors="coerce") == LKV[lv]).sum() / N * 100
                 for lv in ["SA", "A", "U", "D", "SD"]] for i in range(8)])
left = np.zeros(8)
for j, lv in enumerate(["SA", "A", "U", "D", "SD"]):
    ax.barh(PREV_LABELS, mat[:, j], left=left, label=lv, color=cols[lv])
    left += mat[:, j]
ax.set_xlabel("% of respondents")
ax.set_title("F10b — Prevention: full response mix")
ax.legend(ncol=5, loc="lower center", bbox_to_anchor=(0.5, -0.15), fontsize=8)
save("sub_F10b_prevention_stacked.png")

# ============================ F11 Subgroup prevalence ============================
fig, ax = plt.subplots(2, 2, figsize=(11, 8))
# By sex
for i, (grp, title) in enumerate([("sex_c", "Sex"), ("level_c", "Level"), ("faculty_c", "Faculty"), ("age_c", "Age")]):
    ax_flat = ax.flat[i]
    rates = df.groupby(grp)["any_substance_3mo"].mean() * 100
    ax_flat.bar(rates.index, rates.values, color=PAL)
    ax_flat.set_title(f"F11 — Any substance (past 3mo) by {title}")
    ax_flat.tick_params(axis="x", rotation=20, labelsize=8)
    ax_flat.set_ylim(0, 100)
    for i, v in enumerate(rates.values):
        ax_flat.text(i, v + 1, f"{v:.1f}%", ha="center", fontsize=8)
fig.suptitle("F11 — Substance use by demographics")
save("sub_F11_subgroup.png")

# ============================ F12 Factor scores by level/faculty ============================
fig, ax = plt.subplots(1, 2, figsize=(11, 4))
# By level
rate = df.groupby("level_c")["factor_score"].mean()
rate = rate.reindex(["100 Level", "200 Level", "300 Level", "400 Level", "500 Level"])
ax[0].bar(rate.index, rate.values, color=PAL)
ax[0].set_title("Mean factor score by level")
ax[0].tick_params(axis="x", rotation=15, labelsize=8)
# By faculty
rate = df.groupby("faculty_c")["factor_score"].mean().sort_values()
ax[1].barh(rate.index, rate.values, color=PAL[2])
ax[1].set_title("Mean factor score by faculty")
fig.suptitle("F12 — Factor scores by level and faculty")
save("sub_F12_factor_scores.png")

# ============================ F13 Correlation heatmap ============================
scales = df[["factor_score", "factor_peer_social", "factor_academic", "factor_emotional",
             "factor_availability", "factor_family", "factor_social_media", "factor_boredom", "factor_policy",
             "health_score", "health_physical", "health_psychological", "health_social", "health_academic",
             "prev_score"]].apply(pd.to_numeric, errors="coerce")

fig, ax = plt.subplots(figsize=(10, 8))
sns.heatmap(scales.corr(method="spearman").round(2), annot=True, fmt=".2f",
            cmap="coolwarm", vmin=-0.3, vmax=1.0, ax=ax, annot_kws={"size": 7})
ax.set_title("F13 — Spearman correlations (factor/health/prevention subscales)")
save("sub_F13_corr_heatmap.png")

# ============================ F14 Theory mapping radar ============================
# Problem Behaviour Theory constructs: peer, academic, emotional, availability, coping, family, media, boredom, policy
# Social Learning Theory: peer norms, social media, family modelling
pbt = {
    "Peer norms": df["factor_peer_social"].mean(),
    "Academic stress": df["factor_academic"].mean(),
    "Emotional distress": df["factor_emotional"].mean(),
    "Availability": df["factor_availability"].mean(),
    "Coping": df["factor_emotional"].mean(),
    "Family": df["factor_family"].mean(),
    "Social media": df["factor_social_media"].mean(),
    "Boredom": df["factor_boredom"].mean(),
    "Policy": df["factor_policy"].mean(),
}
slt = {
    "Peer norms": df["factor_peer_social"].mean(),
    "Social media": df["factor_social_media"].mean(),
    "Family modelling": df["factor_family"].mean(),
}

fig, ax = plt.subplots(1, 2, figsize=(11, 5), subplot_kw=dict(projection='polar'))
for ax_p, data, title in [(ax[0], pbt, "Problem Behaviour Theory"), (ax[1], slt, "Social Learning Theory")]:
    angles = np.linspace(0, 2*np.pi, len(data), endpoint=False).tolist()
    values = list(data.values())
    values += values[:1]
    angles += angles[:1]
    ax_p.plot(angles, values, 'o-', linewidth=2, color=PAL[0])
    ax_p.fill(angles, values, alpha=0.25, color=PAL[0])
    ax_p.set_xticks(angles[:-1])
    ax_p.set_xticklabels(list(data.keys()), fontsize=8)
    ax_p.set_ylim(0, 5)
    ax_p.set_title(title, fontsize=10, pad=20)
fig.suptitle("F14 — Theory construct scores (1-5 scale)")
save("sub_F14_theory_radar.png")

# ============================ F15 Problem use cascade ============================
fig, ax = plt.subplots(1, 2, figsize=(11, 4))
# Problem use
pu = df["problem_use"].map({1: "Yes", 0: "No"}).value_counts()
ax[0].pie(pu.values, labels=[f"{i} ({v/N*100:.1f}%)" for i,v in zip(pu.index, pu.values)],
          colors=[PAL[0], "#e0e0e0"], startangle=90, wedgeprops=dict(width=0.45))
ax[0].set_title("Problem use (CAGE-type)")

# CAGE items
cage1 = df["should_reduce_c"].replace("", "No").value_counts()
cage2 = df["withdrawal_c"].replace("", "No").value_counts()
ax[1].bar(["Should reduce", "Withdrawal"], 
          [cage1.get("Yes", 0), cage2.get("Yes", 0)], color=[PAL[0], PAL[1]])
ax[1].set_title("CAGE-type items (Yes responses)")
ax[1].set_ylabel("Respondents")
for i, v in enumerate([cage1.get("Yes", 0), cage2.get("Yes", 0)]):
    ax[1].text(i, v + 0.5, str(v), ha="center", fontsize=8)
fig.suptitle("F15 — Problem use indicators")
save("sub_F15_problem_use.png")

# ============================ F16 Key subgroup comparison grid ============================
fig, ax = plt.subplots(2, 3, figsize=(13, 8))
# Any substance by sex
r = df.groupby("sex_c")["any_substance_3mo"].mean() * 100
ax[0,0].bar(r.index, r.values, color=[PAL[0], PAL[1]])
ax[0,0].set_title("Any substance by sex"); ax[0,0].set_ylim(0, 50)

# By level
r = df.groupby("level_c")["any_substance_3mo"].mean() * 100
r = r.reindex(["100 Level", "200 Level", "300 Level", "400 Level", "500 Level"])
ax[0,1].bar(r.index, r.values, color=PAL[2])
ax[0,1].set_title("By level"); ax[0,1].tick_params(axis="x", rotation=20, labelsize=7); ax[0,1].set_ylim(0, 50)

# By faculty
r = df.groupby("faculty_c")["any_substance_3mo"].mean() * 100
ax[0,2].bar(r.index, r.values, color=PAL[3])
ax[0,2].set_title("By faculty"); ax[0,2].tick_params(axis="x", rotation=20, labelsize=7); ax[0,2].set_ylim(0, 50)

# Problem use by sex
r = df.groupby("sex_c")["problem_use"].mean() * 100
ax[1,0].bar(r.index, r.values, color=[PAL[0], PAL[1]])
ax[1,0].set_title("Problem use by sex"); ax[1,0].set_ylim(0, 20)

# Problem use by faculty
r = df.groupby("faculty_c")["problem_use"].mean() * 100
ax[1,1].bar(r.index, r.values, color=PAL[3])
ax[1,1].set_title("Problem use by faculty"); ax[1,1].tick_params(axis="x", rotation=20, labelsize=7); ax[1,1].set_ylim(0, 20)

# Mean factor score by sex
r = df.groupby("sex_c")["factor_score"].mean()
ax[1,2].bar(r.index, r.values, color=[PAL[0], PAL[1]])
ax[1,2].set_title("Mean factor score by sex"); ax[1,2].set_ylim(0, 5)

fig.suptitle("F16 — Key subgroup comparisons")
fig.tight_layout()
save("sub_F16_subgroup_grid.png")

print("ALL FIGURES DONE")