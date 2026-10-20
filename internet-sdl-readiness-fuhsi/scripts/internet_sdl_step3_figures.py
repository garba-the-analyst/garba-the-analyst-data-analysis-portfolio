"""Internet Access & SDL Readiness Study — Phase 3: Figures."""
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
from scipy.stats import spearmanr
plt.rcParams.update({"figure.dpi": 120, "savefig.bbox": "tight", "savefig.dpi": 150, "font.size": 9})
PAL = sns.color_palette("viridis", 8)
CAT = sns.color_palette("Set2")

BASE = Path("/home/garba-the-analyst/Desktop/Projects/Data analysis ")
os.chdir(BASE)

CLEAN = BASE / "data" / "processed" / "internet_sdl_cleaned.csv"
FIG_DIR = BASE / "reports" / "output" / "figures"
FIG_DIR.mkdir(parents=True, exist_ok=True)

df = pd.read_csv(CLEAN)
N = len(df)

def save(fig, name):
    fig.tight_layout()
    fig.savefig(FIG_DIR / name, dpi=150)
    plt.close(fig)
    print("saved", name)

# F01 Sampling / Demographics
fig, axes = plt.subplots(2, 2, figsize=(11, 8))
# Level
lev_order = ["100 level", "200 level", "300 level", "400 level"]
df["level_c"].value_counts().reindex(lev_order).plot(kind="bar", ax=axes[0,0], color=PAL[2])
axes[0,0].set_title("Academic Level"); axes[0,0].set_ylabel("Frequency"); axes[0,0].tick_params(rotation=0)
# Sex
df["sex_c"].value_counts().plot(kind="pie", ax=axes[0,1], autopct="%1.1f%%", colors=CAT[:2], startangle=90)
axes[0,1].set_title("Sex"); axes[0,1].set_ylabel("")
# Department (top 10)
df["dept_c"].value_counts().head(10).plot(kind="barh", ax=axes[1,0], color=PAL[4])
axes[1,0].set_title("Department (Top 10)"); axes[1,0].invert_yaxis()
# Age
axes[1,1].hist(df["age_num"].dropna(), bins=range(16, 31), color=PAL[5], edgecolor="white")
axes[1,1].set_title("Age Distribution"); axes[1,1].set_xlabel("Age"); axes[1,1].set_ylabel("Frequency")
fig.suptitle(f"Demographics (N={N})", fontsize=12)
save(fig, "F01_demographics.png")

# F02 Internet Access Overview
fig, axes = plt.subplots(2, 3, figsize=(14, 9))
t = df["freq_c"].value_counts().reindex(["Daily", "Several times a week", "Once a week", "Rarely", "Never"])
axes[0,0].bar(t.index, t.values, color=PAL[0])
axes[0,0].set_title("Frequency of Access"); axes[0,0].tick_params(rotation=45)
t = df["means_c"].value_counts()
axes[0,1].bar(t.index, t.values, color=PAL[1])
axes[0,1].set_title("Primary Means of Access"); axes[0,1].tick_params(rotation=45)
t = df["reliability_c"].value_counts()
axes[0,2].bar(t.index, t.values, color=PAL[2])
axes[0,2].set_title("Reliability"); axes[0,2].tick_params(rotation=45)
t = df["hours_c"].value_counts().reindex(["More than 4 hours", "3 to 4 hours", "1 to 2 hours", "Less than 1 hour"])
axes[1,0].bar(t.index, t.values, color=PAL[3])
axes[1,0].set_title("Hours/Day (Academic)"); axes[1,0].tick_params(rotation=45)
t = df["satisfaction_c"].value_counts().reindex(["Very satisfied", "Satisfied", "Neutral", "Dissatisfied", "Very dissatisfied"])
axes[1,1].bar(t.index, t.values, color=PAL[4])
axes[1,1].set_title("Satisfaction"); axes[1,1].tick_params(rotation=45)
t = df["device_c"].value_counts()
axes[1,2].pie(t.values, labels=t.index, autopct="%1.1f%%", colors=CAT[:2], startangle=90)
axes[1,2].set_title("Device Ownership")
fig.suptitle("Internet Access Profile", fontsize=12)
save(fig, "F02_internet_access.png")

# F03 Internet Uses (multi-select)
from collections import Counter
use_counts = Counter()
for lst in df["uses_list"]:
    for u in lst:
        use_counts[u] += 1
use_df = pd.DataFrame(list(use_counts.items()), columns=["use", "mentions"]).sort_values("mentions", ascending=True)
fig, ax = plt.subplots(figsize=(10, 6))
ax.barh(use_df["use"], use_df["mentions"], color=PAL[5])
for i, v in enumerate(use_df["mentions"]):
    ax.text(v + 1, i, f"{v} ({v/N*100:.1f}%)", va="center", fontsize=8)
ax.set_xlabel("Mentions (out of 379)")
ax.set_title("Academic Internet Uses (Multi-select)")
save(fig, "F03_internet_uses.png")

# F04 Barriers
bar_counts = Counter()
for lst in df["barriers_list"]:
    for b in lst:
        bar_counts[b] += 1
bar_df = pd.DataFrame(list(Counter(bar_counts).items()), columns=["barrier", "mentions"]).sort_values("mentions", ascending=True)
fig, ax = plt.subplots(figsize=(10, 6))
ax.barh(bar_df["barrier"], bar_df["mentions"], color=PAL[1])
for i, v in enumerate(bar_df["mentions"]):
    ax.text(v + 1, i, f"{v} ({v/N*100:.1f}%)", va="center", fontsize=8)
ax.set_xlabel("Mentions (out of 379)")
ax.set_title("Barriers to Internet Access (Multi-select)")
save(fig, "F04_barriers.png")

# F05 IA Score Distribution
fig, ax = plt.subplots(figsize=(8, 4))
sns.histplot(df["ia_score"].dropna(), bins=20, kde=True, color=PAL[2], ax=ax)
ax.axvline(df["ia_score"].mean(), color=CAT[0], ls="--", label=f"Mean {df['ia_score'].mean():.2f}")
ax.axvline(df["ia_score"].median(), color=CAT[1], ls="-.", label=f"Median {df['ia_score'].median():.2f}")
ax.set_xlabel("IA Composite Score (1-5)"); ax.set_ylabel("Frequency"); ax.legend()
ax.set_title("Internet Access Composite Score Distribution")
save(fig, "F05_ia_score_dist.png")

# F06 SDL Total Distribution
fig, ax = plt.subplots(figsize=(8, 4))
sns.histplot(df["sdl_total"].dropna(), bins=20, kde=True, color=PAL[4], ax=ax)
ax.axvline(df["sdl_total"].mean(), color=CAT[0], ls="--", label=f"Mean {df['sdl_total'].mean():.1f}")
ax.axvline(df["sdl_total"].median(), color=CAT[1], ls="-.", label=f"Median {df['sdl_total'].median():.1f}")
ax.axvline(65, color="gray", ls=":", label="Low/Mod cutoff (65)")
ax.axvline(89, color="gray", ls=":", label="Mod/High cutoff (89)")
ax.set_xlabel("SDL Total Score (24-120)"); ax.set_ylabel("Frequency"); ax.legend()
ax.set_title("SDL Readiness Total Score Distribution")
save(fig, "F06_sdl_total_dist.png")

# F07 SDL Categories
fig, axes = plt.subplots(1, 2, figsize=(10, 4))
t = df["sdl_cat"].value_counts().reindex(["Low", "Moderate", "High"])
axes[0].pie(t.values, labels=t.index, autopct="%1.1f%%", colors=CAT[:3], startangle=90)
axes[0].set_title("SDL Readiness Categories (N=379)")
t = df["ia_cat"].value_counts().reindex(["Low", "Medium", "High"])
axes[1].pie(t.values, labels=t.index, autopct="%1.1f%%", colors=CAT[3:6], startangle=90)
axes[1].set_title("Internet Access Level (Tertiles)")
fig.suptitle("Categorical Distributions", fontsize=11)
save(fig, "F07_categories.png")

# F08 SDL Subscales
fig, ax = plt.subplots(figsize=(8, 4))
subs = ["sdl_self_mgmt", "sdl_desire", "sdl_self_ctrl"]
labels = ["Self Management", "Desire for Learning", "Self Control"]
means = [df[s].mean() for s in subs]
sds = [df[s].std() for s in subs]
ax.bar(labels, means, yerr=sds, capsize=4, color=PAL[:3], edgecolor="white")
for i, (m, s) in enumerate(zip(means, sds)):
    ax.text(i, m + s + 0.02, f"{m:.2f} ± {s:.2f}", ha="center", va="bottom", fontweight="bold")
ax.set_ylim(0, 5.5); ax.set_ylabel("Mean (1-5)")
ax.set_title("SDL Subscale Means (± SD)")
save(fig, "F08_sdl_subscales.png")

# F09 H1: Correlation Scatter
fig, ax = plt.subplots(figsize=(7, 6))
ax.scatter(df["ia_score"], df["sdl_total"], alpha=0.5, color=PAL[0], s=20)
# Trend line
z = np.polyfit(df["ia_score"].dropna(), df["sdl_total"].dropna(), 1)
p = np.poly1d(z)
x_trend = np.linspace(df["ia_score"].min(), df["ia_score"].max(), 100)
ax.plot(x_trend, p(x_trend), color="red", ls="--", lw=2, label=f"Linear fit")
ax.set_xlabel("Internet Access Score (1-5)")
ax.set_ylabel("SDL Total Score (24-120)")
ax.set_title(f"H1: IA Score vs SDL Total\nSpearman r = 0.163 (p = 0.0015)\nPearson r = 0.371 (p < 0.001)")
ax.legend()
save(fig, "F09_correlation_scatter.png")

# F10 H2: SDL by Academic Level
fig, axes = plt.subplots(1, 2, figsize=(11, 4))
lev_order = ["100 level", "200 level", "300 level", "400 level"]
lev_short = [l.split()[0] for l in lev_order]
data = [df.loc[df["level_c"] == l, "sdl_total"].dropna() for l in lev_order]
bp = axes[0].boxplot(data, patch_artist=True)
axes[0].set_xticklabels(lev_short)
for patch, color in zip(bp["boxes"], PAL[:4]):
    patch.set_facecolor(color)
axes[0].set_ylabel("SDL Total Score")
axes[0].set_title("H2: SDL Total by Academic Level\nKruskal-Wallis H=11.75, p=0.0083")
# Means with error bars
means = [d.mean() for d in data]
sems = [d.std() / np.sqrt(len(d)) for d in data]
x = range(4)
axes[1].errorbar(x, means, yerr=sems, fmt="o", capsize=5, color=PAL[5], label="Mean ± SEM")
axes[1].set_xticks(x); axes[1].set_xticklabels(lev_short)
axes[1].set_ylabel("Mean SDL Total")
axes[1].set_title("Mean SDL Total by Level (± SEM)")
axes[1].grid(True, alpha=0.3)
save(fig, "F10_sdl_by_level.png")

# F10b SDL Subscales by Level
fig, axes = plt.subplots(1, 3, figsize=(12, 4))
for ax, (sub, label) in zip(axes, [("sdl_self_mgmt", "Self Management"), ("sdl_desire", "Desire for Learning"), ("sdl_self_ctrl", "Self Control")]):
    data = [df.loc[df["level_c"] == l, sub].dropna() for l in lev_order]
    bp = ax.boxplot(data, patch_artist=True)
    ax.set_xticklabels(lev_short)
    for patch, color in zip(bp["boxes"], PAL[:4]):
        patch.set_facecolor(color)
    ax.set_ylabel("Mean (1-5)")
    ax.set_title(label)
fig.suptitle("SDL Subscales by Academic Level", fontsize=11)
save(fig, "F10b_sdl_subscales_by_level.png")

# F11 IA Score by Level
fig, ax = plt.subplots(figsize=(8, 4))
data = [df.loc[df["level_c"] == l, "ia_score"].dropna() for l in lev_order]
bp = ax.boxplot(data, patch_artist=True)
ax.set_xticklabels(lev_short)
for patch, color in zip(bp["boxes"], PAL[:4]):
    patch.set_facecolor(color)
ax.set_ylabel("IA Composite Score (1-5)")
ax.set_title("Internet Access Score by Academic Level")
save(fig, "F11_ia_by_level.png")

# F12 Correlation Heatmap (IA components vs SDL Subscales)
ia_comp = ["ia_device", "ia_freq", "ia_means", "ia_reliability", "ia_hours", "ia_score", "sat_num"]
ia_labels = ["Device", "Frequency", "Means", "Reliability", "Hours", "IA Composite", "Satisfaction"]
sdl_comp = ["sdl_self_mgmt", "sdl_desire", "sdl_self_ctrl", "sdl_total"]
sdl_labels = ["Self Mgmt", "Desire", "Self Ctrl", "Total"]

corr_mat = pd.DataFrame(index=ia_labels, columns=sdl_labels, dtype=float)
p_mat = pd.DataFrame(index=ia_labels, columns=sdl_labels, dtype=float)
for i, ic in enumerate(ia_comp):
    for j, sc in enumerate(sdl_comp):
        r, p = spearmanr(df[ic], df[sc])
        corr_mat.iloc[i, j] = r
        p_mat.iloc[i, j] = p

fig, ax = plt.subplots(figsize=(8, 10))
annot = corr_mat.copy().astype(object)
for i in range(len(ia_labels)):
    for j in range(len(sdl_labels)):
        ap = p_mat.iloc[i, j]
        rr = corr_mat.iloc[i, j]
        annot.iloc[i, j] = f"{rr:.2f}" + ("*" if ap < 0.05 else "") + ("**" if ap < 0.01 else "")
sns.heatmap(corr_mat.astype(float), annot=annot, fmt="", cmap="RdBu_r",
            vmin=-1, vmax=1, center=0, ax=ax, linewidths=0.5,
            cbar_kws={"label": "Spearman ρ"}, annot_kws={"fontsize": 8})
ax.set_title("Spearman Correlations: IA Components vs SDL Subscales\n* p<0.05, ** p<0.01")
save(fig, "F12_correlation_heatmap.png")

# F13 Internet Uses by Level (stacked bar)
fig, ax = plt.subplots(figsize=(10, 6))
uses_ordered = list(reversed(list(use_df["use"])))
lev_order_short = [l.split()[0] for l in lev_order]
mat = pd.DataFrame(index=uses_ordered, columns=lev_order_short, dtype=int)
for l in lev_order_short:
    sub = df[df["level_c"] == l + " level"]
    cnt = Counter()
    for lst in sub["uses_list"]:
        for u in lst:
            cnt[u] += 1
    for u in uses_ordered:
        mat.loc[u, l] = cnt.get(u, 0)
mat = mat.astype(float)
for u in uses_ordered:
    total = mat.loc[u].sum()
    if total > 0:
        mat.loc[u] = mat.loc[u] / total * 100
mat.plot(kind="barh", stacked=True, ax=ax, colormap="viridis")
ax.set_xlabel("% of respondents at level")
ax.set_title("Academic Internet Uses by Level (% within level)")
ax.legend(title="Level", bbox_to_anchor=(1.02, 1), loc="upper left")
save(fig, "F13_uses_by_level.png")

# F14 Barriers by Level
fig, ax = plt.subplots(figsize=(10, 6))
bar_ordered = list(reversed(list(bar_df["barrier"])))
mat = pd.DataFrame(index=bar_ordered, columns=lev_order_short, dtype=int)
for l in lev_order_short:
    sub = df[df["level_c"] == l + " level"]
    cnt = Counter()
    for lst in sub["barriers_list"]:
        for b in lst:
            cnt[b] += 1
    for b in bar_ordered:
        mat.loc[b, l] = cnt.get(b, 0)
mat = mat.astype(float)
for b in bar_ordered:
    total = mat.loc[b].sum()
    if total > 0:
        mat.loc[b] = mat.loc[b] / total * 100
mat.plot(kind="barh", stacked=True, ax=ax, colormap="plasma")
ax.set_xlabel("% of respondents at level")
ax.set_title("Barriers to Internet Access by Level (% within level)")
ax.legend(title="Level", bbox_to_anchor=(1.02, 1), loc="upper left")
save(fig, "F14_barriers_by_level.png")

# F15 Satisfaction by IA Level
fig, ax = plt.subplots(figsize=(8, 4))
sat_order = ["Very satisfied", "Satisfied", "Neutral", "Dissatisfied", "Very dissatisfied"]
ia_levels = ["Low", "Medium", "High"]
ct = pd.crosstab(df["ia_cat"], df["satisfaction_c"], normalize="index") * 100
ct = ct.reindex(index=ia_levels, columns=sat_order)
bottom = np.zeros(len(ct.index))
colors = ["#d95f5f", "#fc8d62", "#b8b8b8", "#66c2a5", "#35b779"]
for i, col in enumerate(sat_order):
    if col in ct.columns:
        ax.bar(ct.index, ct[col], bottom=bottom, color=colors[i], label=col, width=0.6)
        for j, v in enumerate(ct[col]):
            if v > 5:
                ax.text(j, bottom[j] + v/2, f"{v:.0f}%", ha="center", fontsize=8)
        bottom += ct[col].values
ax.set_ylabel("% within IA level"); ax.set_ylim(0, 100)
ax.set_title("Satisfaction with Internet Access by IA Level")
ax.legend(fontsize=8, bbox_to_anchor=(1.02, 1), loc="upper left")
save(fig, "F15_satisfaction_by_ia.png")

# F16 SDL Subscale Correlation
fig, ax = plt.subplots(figsize=(6, 5))
subs = ["sdl_self_mgmt", "sdl_desire", "sdl_self_ctrl", "sdl_total"]
labels = ["Self Mgmt", "Desire", "Self Ctrl", "Total"]
corr_sub = df[subs].corr(method="spearman")
corr_sub.index = labels; corr_sub.columns = labels
annot = corr_sub.copy().astype(object)
for i in range(4):
    for j in range(4):
        annot.iloc[i, j] = f"{corr_sub.iloc[i, j]:.2f}"
sns.heatmap(corr_sub, annot=annot, fmt="", cmap="RdBu_r", vmin=-1, vmax=1, center=0,
            ax=ax, linewidths=0.5, cbar_kws={"label": "Spearman ρ"}, annot_kws={"fontsize": 9})
ax.set_title("SDL Subscale Inter-correlations (Spearman)")
save(fig, "F16_sdl_intercorr.png")

print("All figures saved:", len(list(FIG_DIR.glob("*.png"))))