"""FUHSI KAP study — Phase 3: figures (~16 charts).
Run:  .venv/bin/python kap_step3_figures.py
Input: data/processed/kap_cleaned_full.csv, data/processed/kap_item_labels.json, reports/output/tables/
Output: reports/output/figures/F*.png
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

LAB = __import__("json").loads(Path("data/processed/kap_item_labels.json").read_text())

df = pd.read_csv("data/processed/kap_cleaned_full.csv", dtype=str, keep_default_na=False)
for c in ["age_num", "level_num", "know_score", "know_pct", "att_score", "type_n",
          "A1__n", "A2__n", "A3__n", "A4__n", "A5__n", "A6__n", "A7__n", "A8__n",
          "A9__n", "A10__n", "E1__n", "E2__n", "E3__n", "E4__n", "E5__n", "E6__n",
          "E7__n", "E8__n", "E9__n", "E10__n", "E11__n", "E12__n", "E13__n", "E14__n",
          "hbm_susceptibility", "hbm_severity", "hbm_benefit", "hbm_barrier", "hbm_cues",
          "hbm_self_efficacy"]:
    df[c] = pd.to_numeric(df[c], errors="coerce")
N = len(df)
FIG = Path("reports/output/figures")
FIG.mkdir(parents=True, exist_ok=True)
TAB = Path("reports/output/tables")

def save(fig, name):
    fig.tight_layout()
    fig.savefig(FIG / name, dpi=150)
    plt.close(fig)
    print("saved", name)

def rd(name):
    d = pd.read_csv(TAB / name, keep_default_na=False)
    for c in d.columns:
        if d[c].dtype == object and d[c].str.fullmatch(r"-?\d+(\.\d+)?").all():
            d[c] = pd.to_numeric(d[c])
    return d

# F01 sampling attainment -------------------------------
fig, ax = plt.subplots(figsize=(7, 4))
levels = ["100", "200", "300", "400"]
target = [144, 108, 69, 53]
achieved = [int((df["level_c"] == l).sum()) for l in ["100 level", "200 level", "300 level", "400 level"]]
x = np.arange(4)
ax.bar(x - 0.2, target, 0.38, label="Stratum target (374 framework)", color=PAL[1])
ax.bar(x + 0.2, achieved, 0.38, label=f"Achieved (n={N})", color=PAL[4])
for i, (t_, a_) in enumerate(zip(target, achieved)):
    ax.text(i - 0.2, t_ + 2, str(t_), ha="center", fontsize=8)
    ax.text(i + 0.2, a_ + 2, str(a_), ha="center", fontsize=8)
ax.set_xticks(x); ax.set_xticklabels([f"{l} level" for l in levels])
ax.set_ylabel("Respondents")
ax.set_title("Stratified sampling framework vs achieved sample (Yamane target n=340)")
ax.legend()
save(fig, "F01_sampling.png")

# F02 demographics 2x2 -----------------------------------
fig, axes = plt.subplots(2, 2, figsize=(11, 8))
band_order = ["16-20 years", "21-24 years", "25-30 years", "Above 30 years", "Not stated"]
d = df["age_band"].value_counts().reindex(band_order).fillna(0)
axes[0, 0].bar(band_order, d.values, color=PAL[2])
axes[0, 0].set_title("Age group"); axes[0, 0].set_ylabel("Frequency")
axes[0, 0].tick_params(axis="x", rotation=20)
lev = ["100 level", "200 level", "300 level", "400 level"]
d = df["level_c"].value_counts().reindex(lev)
axes[0, 1].bar([l.split()[0] for l in lev], d.values, color=PAL[3])
axes[0, 1].set_title("Level of study")
d = df["marital_c"].value_counts()
axes[1, 0].bar(d.index, d.values, color=PAL[0])
axes[1, 0].set_title("Marital status")
d = df["dept_c"].value_counts()
axes[1, 1].barh(d.index[::-1], d.values[::-1], color=CAT[2])
axes[1, 1].set_title("Department")
for axx in [axes[0, 0], axes[0, 1], axes[1, 0]]:
    for k, v in zip(axx.patches, range(len(axx.patches))):
        pass
fig.suptitle(f"Demographic profile of respondents (n={N})", fontsize=12)
save(fig, "F02_demographics.png")

# F03 knowledge items -------------------------------------
fig, ax = plt.subplots(figsize=(9.5, 6))
pct = []
for i in range(12):
    v = df[f"K{i+1}"]
    pct.append(round((v == LAB["k_key"][str(i)]).mean() * 100, 1))
labels = [f"K{i+1}. {LAB['k'][i][:72]}" for i in range(12)]
y = np.arange(12)[::-1]
ax.barh(y, pct, color=PAL[4], edgecolor="white")
ax.barh(y, [100 - p for p in pct], left=pct, color="#d95f5f", alpha=0.55)
for yy, p in zip(y, pct):
    ax.text(p + 1, yy, f"{p}%", va="center", fontsize=8)
ax.set_yticks(y); ax.set_yticklabels(labels, fontsize=7.5)
ax.set_xlabel("% of respondents answering correctly")
ax.set_title("Knowledge items — % correct (key: all True except K10=False)")
ax.set_xlim(0, 105)
save(fig, "F03_knowledge_items.png")

# F04 knowledge score distribution ------------------------
fig, ax = plt.subplots(figsize=(8, 4.4))
sns.histplot(df["know_score"], bins=np.arange(-0.5, 13.5, 1), color=PAL[4], discrete=True, ax=ax)
ax.axvline(df["know_score"].mean(), color=CAT[0], ls="--", label=f"Mean {df['know_score'].mean():.2f}")
ax.axvline(df["know_score"].median(), color=CAT[1], ls="-.", label=f"Median {df['know_score'].median():.0f}")
good = int((df["know_cat_mean"] == "Good").sum())
ax.set_title(f"Knowledge score distribution — Good {good} ({good/N*100:.1f}%) vs Poor {N-good} ({(N-good)/N*100:.1f}%) [mean or median split]")
ax.set_xlabel("Knowledge score (0-12)"); ax.set_ylabel("Respondents")
ax.legend()
save(fig, "F04_knowledge_scores.png")

# F05 attitude items stacked ------------------------------
fig, ax = plt.subplots(figsize=(9.5, 5.5))
order = ["SA", "A", "U", "D", "SD"]
cols = ["#35b779", "#66c2a5", "#b8b8b8", "#fc8d62", "#d95f5f"]
left = np.zeros(10)
items = [f"A{i+1}{' (r)' if i in LAB['a_rev'] else ''}. {LAB['a'][i][:60]}" for i in range(10)]
for li, lv in enumerate(order):
    pctv = np.array([sum(str(s).strip().upper() == lv for s in df[f"A{j+1}_raw"]) / N * 100
                     for j in range(10)])
    ax.barh(np.arange(10), pctv, left=left, color=cols[li], label=lv, height=0.72)
    left += pctv
ax.set_yticks(np.arange(10)); ax.set_yticklabels(items, fontsize=6.8)
ax.set_xlim(0, 100); ax.set_xlabel("% respondents")
ax.invert_yaxis()
ax.set_title("Attitude items — response distribution (5-point Likert as fielded; (r)=reverse-scored)")
ax.legend(ncol=5, loc="lower center", bbox_to_anchor=(0.5, -0.14))
save(fig, "F05_attitude_items.png")

# F06 attitude score distribution -------------------------
fig, ax = plt.subplots(figsize=(8, 4.2))
sns.histplot(df["att_score"], bins=np.arange(9.5, 51.5, 1), color=PAL[6], discrete=True, ax=ax)
ax.axvline(df["att_score"].mean(), color=CAT[0], ls="--", label=f"Mean {df['att_score'].mean():.2f}")
ax.axvline(df["att_score"].median(), color=CAT[1], ls="-.", label=f"Median {df['att_score'].median():.0f}")
pos = int((df["att_cat_mean"] == "Positive").sum())
ax.set_title(f"Attitude score distribution — Positive {pos} ({pos/N*100:.1f}%) vs Negative {N-pos}")
ax.set_xlabel("Attitude score (10-50)"); ax.set_ylabel("Respondents"); ax.legend()
save(fig, "F06_attitude_scores.png")

# F07 HBM subscales ---------------------------------------
fig, ax = plt.subplots(figsize=(7.5, 4))
subs = list(LAB["hbm_groups"].keys())
means = [df[f"hbm_{g}"].mean() for g in subs]
sds = [df[f"hbm_{g}"].std() for g in subs]
ax.bar(subs, means, yerr=sds, capsize=4, color=PAL[:6], edgecolor="white")
for i, (m, s) in enumerate(zip(means, sds)):
    ax.text(i, m, f"{m:.2f}", ha="center", va="bottom", fontsize=8, fontweight="bold")
ax.set_ylim(0, 5.6); ax.set_ylabel("Mean (1-5)")
ax.axhline(3.0, color="grey", ls=":", lw=1)
ax.set_title("HBM construct scores (mean ± SD)")
save(fig, "F07_hbm_subscale.png")

# F08 HBM item means by domain ----------------------------
fig, ax = plt.subplots(figsize=(9.5, 6.5))
means = [df[f"E{i+1}__n"].mean() for i in range(14)]
grp_of = {}
for g, ids in LAB["hbm_groups"].items():
    for i in ids:
        grp_of[f"E{i}"] = g
cmap = {g: c for g, c in zip(LAB["hbm_groups"], CAT[:6])}
labels = [f"{i+1}. {LAB['hbm'][i][:78]}" for i in range(14)]
y = np.arange(14)[::-1]
ax.barh(y, means, color=[cmap[grp_of[f"E{i+1}"]] for i in range(14)], edgecolor="white")
for yy, m in zip(y, means):
    ax.text(max(m, 0) + 0.05, yy, f"{m:.2f}", va="center", fontsize=8)
ax.set_yticks(y); ax.set_yticklabels(labels, fontsize=7.5)
ax.set_xlabel("Mean (1-5)"); ax.set_xlim(0, 5.7)
handles = [plt.Rectangle((0, 0), 1, 1, color=cmap[g]) for g in cmap]
u = cmap
ax.legend(handles, list(cmap.keys()), fontsize=8, loc="lower right")
ax.set_title("HBM statements — item means by construct (higher barrier items = greater barrier)")
save(fig, "F08_hbm_items.png")

# F09 experienced + types ----------------------------------
fig, axes = plt.subplots(1, 2, figsize=(11, 4.4), gridspec_kw={"width_ratios": [1, 2]})
d = df["exp_c"].value_counts()
axes[0].pie(d.values, labels=d.index, autopct=lambda p: f"{p:.1f}%",
            colors=[CAT[0], CAT[3]], startangle=90)
axes[0].set_title(f"Ever experienced menstrual irregularity (n={N})")
types = rd("T05b_types.csv").head(8)
axes[1].barh(types["type_of_irregularity"][::-1], types["mentions"][::-1], color=PAL[5])
tot = int((df["type_list"] != "").sum())
for yy, (m, p) in enumerate(zip(types["mentions"][::-1],
                                (types["mentions"][::-1] / tot * 100).round(1))):
    axes[1].text(m + 1, yy, f"{m} ({p}%)", va="center", fontsize=8)
axes[1].set_xlabel("Mentions (multi-select)")
axes[1].set_title(f"Types of irregularity reported (n={tot} respondents listing types)")
save(fig, "F09_experience_types.png")

# F10 first action -----------------------------------------
fig, ax = plt.subplots(figsize=(9, 4.6))
act = rd("T05c_first_action.csv")
ax.barh(act["category"][::-1], act["n"][::-1], color=CAT[:len(act)][::-1])
e = (df["exp_c"] == "Yes").sum()
for yy, (n_, p) in enumerate(zip(act["n"][::-1], act["pct"][::-1])):
    ax.text(n_ + 1, yy, f"{n_} ({p}%)", va="center", fontsize=8)
ax.set_xlabel(f"Respondents (experienced group, n={df['exp_c'].value_counts()['Yes']})")
ax.set_title("Q3 — What did you do when you first noticed the irregularity?")
save(fig, "F10_first_action.png")

# F11 timeliness --------------------------------------------
fig, ax = plt.subplots(figsize=(8.5, 4))
tl = pd.read_csv(TAB / "T05d_timeliness.csv")
tl = tl[tl["variable"] == "time_to_seek_help"]
order = ["Immediately", "Within a week", "Within a month", "More than a month", "Did not seek", "Not stated"]
d = df.loc[df["exp_c"] == "Yes", "time_c"].value_counts().reindex(order).fillna(0)
ax.bar(order, d.values, color=[CAT[0]] * 4 + [CAT[1]] + ["#bbb"])
for i, v in enumerate(d.values):
    ax.text(i, v + 1, f"{int(v)}\n({v/257*100:.0f}%)", ha="center", fontsize=8)
ax.set_ylabel("Respondents"); ax.set_ylim(0, d.max() * 1.25)
ax.set_title("Q4 — Timeliness of professional help-seeking (among experienced, n=257)")
ax.tick_params(axis="x", rotation=15)
save(fig, "F11_timeliness.png")

# F12 info sources ------------------------------------------
fig, ax = plt.subplots(figsize=(8.5, 4.4))
info = rd("T05e_info_sources.csv")
ax.barh(info["source"][::-1], info["mentions"][::-1], color=PAL[1])
for yy, (m, p) in enumerate(zip(info["mentions"][::-1], info["pct_of_376"][::-1])):
    ax.text(m + 1, yy, f"{m} ({p}%)", va="center", fontsize=8)
ax.set_xlabel("Mentions (multi-select) — % of all 376")
ax.set_title("Q5 — Where do you usually get information about menstrual health?")
save(fig, "F12_info_sources.png")

# F13 campus + facility --------------------------------------
fig, axes = plt.subplots(1, 2, figsize=(11, 4.2))
d = df["campus_c"].value_counts()
axes[0].pie(d.values, labels=["No", "Yes"], colors=[CAT[1], CAT[0]], autopct=lambda p: f"{p:.1f}%", startangle=90)
axes[0].set_title(f"Q6 — Ever visited FUHSI campus health centre ({int(d['Yes'])} of {N})")
fac = rd("T05g_preferred_facility.csv")
axes[1].barh(fac["category"][::-1], fac["n"][::-1], color=PAL[3])
for yy, (n_, p) in enumerate(zip(fac["n"][::-1], fac["pct"][::-1])):
    axes[1].text(n_ + 2, yy, f"{n_} ({p}%)", va="center", fontsize=8)
axes[1].set_xlabel("Respondents")
axes[1].set_title("Q7 — Preferred facility for menstrual care")
save(fig, "F13_campus_facility.png")

# F14 barriers -------------------------------------------------
fig, ax = plt.subplots(figsize=(9, 4.6))
bar = rd("T05i_barriers.csv")
ax.barh(bar["barrier"][::-1], bar["mentions"][::-1], color=PAL[2])
for yy, (m, p) in enumerate(zip(bar["mentions"][::-1], bar["pct_of_376"][::-1])):
    ax.text(m + 1.5, yy, f"{m} ({p}%)", va="center", fontsize=8)
ax.set_xlabel("Mentions (multi-select) — % of all 376")
ax.set_title("Q8 — Main reasons that would prevent seeking medical care")
save(fig, "F14_barriers.png")

# F15 hypotheses stacked ---------------------------------------
fig, axes = plt.subplots(1, 2, figsize=(11.5, 4.6))
for axx, cat, title, ttl in [(axes[0], "know_cat_mean", "future_c",
        f"H1: Knowledge category x future intent (n={N})"),
        (axes[1], "att_cat_mean", "future_c",
        f"H2: Attitude category x future intent (n={N})")]:
    ct = pd.crosstab(df[cat], df["future_c"], normalize="index") * 100
    bottom = np.zeros(len(ct.index))
    cset = [CAT[0], "#b8b8b8", CAT[3]]
    for k, (col, colr) in enumerate(zip(["Yes", "Not sure", "No"], cset)):
        if col in ct.columns:
            axx.bar(ct.index, ct[col], bottom=bottom, color=colr, label=col, width=0.5)
            for i, v in enumerate(ct[col]):
                axx.text(i, bottom[i] + v / 2, f"{v:.0f}%", ha="center", fontsize=7.5)
            bottom += ct[col].values
    axx.set_ylim(0, 100); axx.set_ylabel("% within category"); axx.legend(fontsize=8)
    axx.set_title(ttl)
p_k = rd("T06a_hypotheses_chi_square.csv")
pk = p_k[p_k["test"] == "H1 primary (binary)"].iloc[0]
ph = p_k[p_k["test"] == "H2 primary (binary)"].iloc[0]
axes[0].set_xlabel(f"chi2(1)={pk['chi2']}, p={pk['p']}, V={pk['cramers_v']}")
axes[1].set_xlabel(f"chi2(1)={ph['chi2']}, p={ph['p']}, V={ph['cramers_v']}")
fig.suptitle("Hypothesis tests — chi-square association with would-seek in future (binary)", fontsize=11)
save(fig, "F15_hypotheses.png")

# F16 Pearson heatmap -------------------------------------------
r = pd.read_csv(TAB / "T07a_pearson_r.csv", index_col=0)
p = pd.read_csv(TAB / "T07b_pearson_p.csv", index_col=0)
names = {"age_num": "Age", "level_num": "Level", "know_score": "Knowledge", "att_score": "Attitude",
         **{f"hbm_{g}": g.capitalize() for g in LAB["hbm_groups"]}}
r = r.rename(index=names, columns=names)
p = p.rename(index=names, columns=names)
mask = p.isna() | (r.isna())
annot = r.copy().astype(object)
for i in annot.index:
    for j in annot.columns:
        try:
            ap = float(p.loc[i, j])
            rr = r.loc[i, j]
            annot.loc[i, j] = f"{rr:.2f}" + ("*" if ap < 0.05 else "") + ("**" if ap < 0.001 else "")
        except Exception:
            annot.loc[i, j] = ""
fig, ax = plt.subplots(figsize=(9.5, 8))
sns.heatmap(r.astype(float), mask=mask, annot=annot, fmt="", cmap="RdBu_r",
            vmin=-1, vmax=1, center=0, square=True, ax=ax,
            cbar_kws={"label": "Pearson r"}, linewidths=0.5, annot_kws={"fontsize": 7.5})
ax.set_title("Pearson correlation matrix (* p<0.05, ** p<0.001, pairwise n)\n"
             "Document-mandated analysis (§3.11)")
save(fig, "F16_pearson_heatmap.png")

print("Figures complete:", len(list(FIG.glob('F*.png'))))
