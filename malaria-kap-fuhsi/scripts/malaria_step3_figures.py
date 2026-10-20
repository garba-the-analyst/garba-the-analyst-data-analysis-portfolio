"""Malaria Prevention KAP Study — Phase 3: Figures."""
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
from scipy.stats import spearmanr, pearsonr

warnings.filterwarnings("ignore")
sns.set_theme(style="whitegrid")
plt.rcParams.update({"figure.dpi": 120, "savefig.bbox": "tight", "savefig.dpi": 150, "font.size": 9})
PAL = sns.color_palette("viridis", 8)
CAT = sns.color_palette("Set2")

BASE = Path("/home/garba-the-analyst/Desktop/Projects/Data analysis ")
os.chdir(BASE)

CLEAN = BASE / "data" / "processed" / "malaria_kap_cleaned.csv"
TAB_DIR = BASE / "reports" / "output" / "tables"
FIG_DIR = BASE / "reports" / "output" / "figures"
FIG_DIR.mkdir(parents=True, exist_ok=True)

df = pd.read_csv(CLEAN, dtype=str, keep_default_na=False)
num_cols = ["know_score", "know_pct", "prac_score", "mis_score", "gap_score",
            "level_num", "age_ord"] + \
           [f"K{i+1}" for i in range(10)] + \
           [f"P{i+1}" for i in range(8)] + \
           [f"M{i+1}" for i in range(8)]
for c in num_cols:
    if c in df.columns:
        df[c] = pd.to_numeric(df[c], errors="coerce")
N = len(df)

# Recreate faculty_grp
DEPT_FAC = {
    "Nursing": "Allied Health", "Audiology": "Allied Health", "Human Nutrition & Dietetics": "Allied Health",
    "MBBS": "Clinical", "MLS": "Basic Medical", "Pharmacology": "Basic Medical",
    "Microbiology": "Basic Medical", "Biochemistry": "Basic Medical",
    "Human Nutrition & Dietetics": "Allied Health",
    "Information Technology & Health": "Basic Medical",
}
df["faculty_grp"] = df["dept_c"].map(DEPT_FAC).fillna("Other")

def save(fig, name):
    fig.tight_layout()
    fig.savefig(FIG_DIR / name, dpi=150)
    plt.close(fig)
    print("saved", name)

# F01 Demographics
fig, axes = plt.subplots(2, 2, figsize=(11, 8))
lev_order = ["100 Level", "200 Level", "300 Level", "400 Level"]
df["level_c"].value_counts().reindex(lev_order).plot(kind="bar", ax=axes[0,0], color=PAL[2])
axes[0,0].set_title("Academic Level"); axes[0,0].set_ylabel("Frequency")
df["gender_c"].value_counts().plot(kind="pie", ax=axes[0,1], autopct="%1.1f%%", colors=CAT[:2], startangle=90)
axes[0,1].set_title("Gender"); axes[0,1].set_ylabel("")
df["residence_c"].value_counts().plot(kind="bar", ax=axes[1,0], color=PAL[4])
axes[1,0].set_title("Residence"); axes[1,0].tick_params(rotation=20)
df["dept_c"].value_counts().head(10).plot(kind="barh", ax=axes[1,1], color=PAL[5])
axes[1,1].set_title("Department (Top 10)"); axes[1,1].invert_yaxis()
fig.suptitle(f"Demographics (N={N})", fontsize=12)
save(fig, "F01_demographics.png")

# F02 Knowledge Items
fig, ax = plt.subplots(figsize=(9.5, 6))
pct = []
for i in range(10):
    v = df[f"K{i+1}"]
    pct.append(round(v.mean() * 100, 1))
labels = [f"K{i+1}" for i in range(10)]
y = np.arange(10)[::-1]
ax.barh(y, pct, color=PAL[4], edgecolor="white")
for yy, p in zip(y, pct):
    ax.text(p + 1, yy, f"{p}%", va="center", fontsize=8)
ax.set_yticks(y); ax.set_yticklabels(labels)
ax.set_xlabel("% Correct"); ax.set_xlim(0, 105)
ax.set_title("Knowledge Items — % Correct")
save(fig, "F02_knowledge_items.png")

# F03 Practice Items (stacked)
fig, ax = plt.subplots(figsize=(10, 5))
prac_labels = ["ITN every night", "Clear stagnant water", "Use repellent", "Screen windows/doors",
               "Dispose refuse", "Seek testing for fever", "Complete antimalarial course", "Long sleeves evening"]
order = ["Always", "Often", "Sometimes", "Rarely", "Never"]
cols = ["#35b779", "#66c2a5", "#b8b8b8", "#fc8d62", "#d95f5f"]
left = np.zeros(8)
for li, lv in enumerate(order):
    pctv = np.array([sum(str(s).strip() == lv for s in df[f"P{j+1}_raw"]) / N * 100 for j in range(8)])
    ax.barh(np.arange(8), pctv, left=left, color=cols[li], label=lv, height=0.72)
    left += pctv
ax.set_yticks(np.arange(8)); ax.set_yticklabels(prac_labels)
ax.set_xlim(0, 100); ax.set_xlabel("% respondents")
ax.invert_yaxis()
ax.set_title("Practice Items — Frequency Distribution")
ax.legend(ncol=5, loc="lower center", bbox_to_anchor=(0.5, -0.14))
save(fig, "F03_practice_items.png")

# F04 Knowledge Score Distribution
fig, ax = plt.subplots(figsize=(8, 4.4))
sns.histplot(df["know_score"], bins=np.arange(-0.5, 11.5, 1), color=PAL[4], discrete=True, ax=ax)
ax.axvline(df["know_score"].mean(), color=CAT[0], ls="--", label=f"Mean {df['know_score'].mean():.2f}")
ax.axvline(df["know_score"].median(), color=CAT[1], ls="-.", label=f"Median {df['know_score'].median():.0f}")
ax.set_xlabel("Knowledge Score (0-10)"); ax.set_ylabel("Respondents"); ax.legend()
ax.set_title("Knowledge Score Distribution")
save(fig, "F04_knowledge_scores.png")

# F05 Practice Score Distribution
fig, ax = plt.subplots(figsize=(8, 4.2))
sns.histplot(df["prac_score"], bins=np.arange(7.5, 41.5, 1), color=PAL[6], discrete=True, ax=ax)
ax.axvline(df["prac_score"].mean(), color=CAT[0], ls="--", label=f"Mean {df['prac_score'].mean():.2f}")
ax.axvline(df["prac_score"].median(), color=CAT[1], ls="-.", label=f"Median {df['prac_score'].median():.0f}")
ax.set_xlabel("Practice Score (8-40)"); ax.set_ylabel("Respondents"); ax.legend()
ax.set_title("Practice Score Distribution")
save(fig, "F05_practice_scores.png")

# F06 Misconceptions
fig, ax = plt.subplots(figsize=(9.5, 5))
mis_labels = ["Sunlight causes malaria", "Oily food causes malaria", "Person-to-person transmission",
              "Single episode = lifelong immunity", "Herbal concoctions cure malaria",
              "Nets only needed in rainy season", "Prophylactic antimalarials safe",
              "Malaria is spiritual affliction"]
order = ["Strongly Agree", "Agree", "Neutral", "Disagree", "Strongly Disagree"]
cols = ["#d95f5f", "#fc8d62", "#b8b8b8", "#66c2a5", "#35b779"]
left = np.zeros(8)
for li, lv in enumerate(order):
    pctv = np.array([sum(str(s).strip() == lv for s in df[f"M{j+1}_raw"]) / N * 100 for j in range(8)])
    ax.barh(np.arange(8), pctv, left=left, color=cols[li], label=lv, height=0.72)
    left += pctv
ax.set_yticks(np.arange(8)); ax.set_yticklabels(mis_labels)
ax.set_xlim(0, 100); ax.set_xlabel("% respondents")
ax.invert_yaxis()
ax.set_title("Misconceptions — Agreement Distribution (reverse-scored)")
ax.legend(ncol=5, loc="lower center", bbox_to_anchor=(0.5, -0.14))
save(fig, "F06_misconceptions.png")

# F07 Knowledge vs Practice Scatter
fig, ax = plt.subplots(figsize=(7, 6))
ax.scatter(df["know_score"], df["prac_score"], alpha=0.5, color=PAL[0], s=20)
z = np.polyfit(df["know_score"].dropna(), df["prac_score"].dropna(), 1)
p_fit = np.poly1d(z)
x_trend = np.linspace(df["know_score"].min(), df["know_score"].max(), 100)
ax.plot(x_trend, p_fit(x_trend), color="red", ls="--", lw=2, label="Linear fit")
ax.set_xlabel("Knowledge Score (0-10)")
ax.set_ylabel("Practice Score (8-40)")
r_s, p_s = spearmanr(df["know_score"], df["prac_score"])
r_p, p_p = pearsonr(df["know_score"], df["prac_score"])
ax.set_title(f"Knowledge vs Practice\nSpearman ρ = {r_s:.3f} (p = {p_s:.4f})\nPearson r = {r_p:.3f} (p < 0.001)")
ax.legend()
save(fig, "F07_knowledge_practice_scatter.png")

# F08 Knowledge by Level & Faculty
fig, axes = plt.subplots(1, 2, figsize=(11, 4))
lev_order = ["100 Level", "200 Level", "300 Level", "400 Level"]
data = [df.loc[df["level_c"] == l, "know_score"].dropna() for l in lev_order]
bp = axes[0].boxplot(data, patch_artist=True)
axes[0].set_xticklabels([l.split()[0] for l in lev_order])
for patch, color in zip(bp["boxes"], PAL[:4]):
    patch.set_facecolor(color)
axes[0].set_ylabel("Knowledge Score (0-10)")
axes[0].set_title("Knowledge Score by Academic Level")
# Faculty
fac_order = ["Allied Health", "Basic Medical", "Clinical", "Other"]
data = [df.loc[df["faculty_grp"] == f, "know_score"].dropna() for f in ["Allied Health", "Basic Medical", "Clinical"]]
bp = axes[1].boxplot(data, patch_artist=True)
axes[1].set_xticklabels(["Allied Health", "Basic Medical", "Clinical"])
for patch, color in zip(bp["boxes"], CAT[:3]):
    patch.set_facecolor(color)
axes[1].set_ylabel("Knowledge Score (0-10)")
axes[1].set_title("Knowledge Score by Faculty Group")
fig.suptitle("Knowledge Score by Level & Faculty", fontsize=11)
save(fig, "F08_knowledge_by_level_faculty.png")

# F09 Practice by Level & Faculty
fig, axes = plt.subplots(1, 2, figsize=(11, 4))
data = [df.loc[df["level_c"] == l, "prac_score"].dropna() for l in lev_order]
bp = axes[0].boxplot(data, patch_artist=True)
axes[0].set_xticklabels([l.split()[0] for l in lev_order])
for patch, color in zip(bp["boxes"], PAL[:4]):
    patch.set_facecolor(color)
axes[0].set_ylabel("Practice Score (8-40)")
axes[0].set_title("Practice Score by Academic Level")
data = [df.loc[df["faculty_grp"] == f, "prac_score"].dropna() for f in ["Allied Health", "Basic Medical", "Clinical"]]
bp = axes[1].boxplot(data, patch_artist=True)
axes[1].set_xticklabels(["Allied Health", "Basic Medical", "Clinical"])
for patch, color in zip(bp["boxes"], CAT[:3]):
    patch.set_facecolor(color)
axes[1].set_ylabel("Practice Score (8-40)")
axes[1].set_title("Practice Score by Faculty Group")
fig.suptitle("Practice Score by Level & Faculty", fontsize=11)
save(fig, "F09_practice_by_level_faculty.png")

# F10 ITN Ownership by Level
fig, ax = plt.subplots(figsize=(8, 4))
itn_by_lev = pd.crosstab(df["level_c"], df["itn_own_c"], normalize="index") * 100
itn_by_lev = itn_by_lev.reindex(index=lev_order, columns=["Yes", "No"])
bottom = np.zeros(len(itn_by_lev.index))
for col, color in zip(["Yes", "No"], [CAT[0], CAT[3]]):
    if col in itn_by_lev.columns:
        ax.bar(itn_by_lev.index, itn_by_lev[col], bottom=bottom, color=color, label=col, width=0.5)
        for i, v in enumerate(itn_by_lev[col]):
            ax.text(i, bottom[i] + v / 2, f"{v:.0f}%", ha="center", fontsize=8)
        bottom += itn_by_lev[col].values
ax.set_ylabel("% within level"); ax.set_ylim(0, 100)
ax.set_title("ITN Ownership by Academic Level")
ax.legend()
save(fig, "F10_itn_ownership_by_level.png")

# F11 Information Sources
fig, ax = plt.subplots(figsize=(8.5, 4))
src = df["source_c"].value_counts()
ax.barh(src.index[::-1], src.values[::-1], color=PAL[1])
for yy, (v, p) in enumerate(zip(src.values[::-1], (src.values[::-1] / N * 100).round(1))):
    ax.text(v + 2, yy, f"{v} ({p}%)", va="center", fontsize=8)
ax.set_xlabel("Respondents"); ax.set_title("Primary Source of Malaria Prevention Knowledge")
save(fig, "F11_info_sources.png")

# F12 Barriers / Future Intent
fig, axes = plt.subplots(2, 3, figsize=(13, 8))
for ax, var, label in zip(axes.flatten(),
                           ["net_purchase_c", "comfort_c", "treat24_c", "sanit_c", "talk_c"],
                           ["Likely to purchase or replace ITN", "Comfort sleeping under ITN",
                            "Likely to seek treatment within 24h",
                            "Willing to participate in sanitation", "Likely to attend health talk"]):
    t = df[var].value_counts()
    ax.barh(t.index[::-1], t.values[::-1], color=PAL[:len(t)])
    for yy, v in enumerate(t.values[::-1]):
        ax.text(v + 1, yy, f"{v} ({v/N*100:.0f}%)", va="center", fontsize=8)
    ax.set_xlabel("Respondents")
    ax.set_title(label, fontsize=9)
axes.flatten()[5].axis("off")
fig.suptitle("Barriers & Future Intent", fontsize=11)
save(fig, "F12_barriers_intent.png")

# F12b Misconceptions by Level
fig, ax = plt.subplots(figsize=(8, 4))
data = [df.loc[df["level_c"] == l, "mis_score"].dropna() for l in lev_order]
bp = ax.boxplot(data, patch_artist=True)
ax.set_xticklabels([l.split()[0] for l in lev_order])
for patch, color in zip(bp["boxes"], PAL[:4]):
    patch.set_facecolor(color)
ax.set_ylabel("Misconception Score (higher = fewer)")
ax.set_title("Misconception Score by Academic Level")
save(fig, "F13_misconceptions_by_level.png")

# F14 Knowledge x Practice Stacked
fig, ax = plt.subplots(figsize=(8, 5))
ct = pd.crosstab(df["know_cat_fixed"], df["prac_cat_fixed"], normalize="index") * 100
bottom = np.zeros(len(ct.index))
cats = ["Good (≥30)", "Moderate (18-29)", "Poor (<18)"]
colors = [CAT[0], "#b8b8b8", CAT[3]]
for col, colr in zip(cats, colors):
    if col in ct.columns:
        ax.bar(ct.index, ct[col], bottom=bottom, color=colr, label=col, width=0.5)
        for i, v in enumerate(ct[col]):
            ax.text(i, bottom[i] + v / 2, f"{v:.0f}%", ha="center", fontsize=8)
        bottom += ct[col].values
ax.set_ylabel("% within knowledge category"); ax.set_ylim(0, 100)
ax.legend(fontsize=8)
ax.set_title("Practice Category within Knowledge Category\nχ²=20.75, p=0.0004, V=0.18")
save(fig, "F14_know_practice_stacked.png")

# F15 Correlation Heatmap
ia_vars = ["know_score", "prac_score", "mis_score", "gap_score", "age_ord", "level_num"]
corr = df[ia_vars].corr(method="spearman")
p_mat = df[ia_vars].corr(method=lambda x, y: spearmanr(x, y)[1])
labels = ["Knowledge", "Practice", "Misconceptions\n(rev)", "Gap\n(P-K)", "Age", "Level"]
corr.index = labels; corr.columns = labels
p_mat.index = labels; p_mat.columns = labels
annot = corr.copy().astype(object)
for i in range(len(labels)):
    for j in range(len(labels)):
        ap = p_mat.iloc[i, j]
        rr = corr.iloc[i, j]
        annot.iloc[i, j] = f"{rr:.2f}" + ("*" if ap < 0.05 else "") + ("**" if ap < 0.01 else "")
fig, ax = plt.subplots(figsize=(7.5, 6.5))
sns.heatmap(corr.astype(float), annot=annot, fmt="", cmap="RdBu_r",
            vmin=-1, vmax=1, center=0, square=True, ax=ax,
            cbar_kws={"label": "Spearman ρ"}, linewidths=0.5, annot_kws={"fontsize": 8})
ax.set_title("Spearman Correlations (* p<0.05, ** p<0.01)\nKnowledge-Practice Gap Analysis")
save(fig, "F15_correlation_heatmap.png")

# F16 Knowledge-Practice Gap by Level
fig, ax = plt.subplots(figsize=(8, 4))
data = [df.loc[df["level_c"] == l, "gap_score"].dropna() for l in lev_order]
bp = ax.boxplot(data, patch_artist=True)
ax.set_xticklabels([l.split()[0] for l in lev_order])
for patch, color in zip(bp["boxes"], PAL[:4]):
    patch.set_facecolor(color)
ax.axhline(0, color="gray", ls=":", lw=1)
ax.set_ylabel("Gap Score (Practice_z - Knowledge_z)")
ax.set_title("Knowledge-Practice Gap by Academic Level\n(Positive = Practice > Knowledge)")
save(fig, "F16_gap_by_level.png")

print("Figures complete:", len(list(FIG_DIR.glob("*.png"))))