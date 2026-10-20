"""Internet Access & SDL Readiness Study — Phase 1: Clean, Score & Save."""
import warnings
import os
from pathlib import Path
import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")

BASE = Path("/home/garba-the-analyst/Desktop/Projects/Data analysis ")
os.chdir(BASE)

RAW_DIR = BASE / "data" / "raw" / "EFFECT OF INTERNET ACCESS ON SELF-DIRECTED LEARNING READINESS AMONG UNDERGRADUATE STUDENTS OF FEDERAL UNIVERSITY OF HEALTH SCIENCES ILA-ORANGUN"
RAW_FILE = RAW_DIR / "Unreseracgd_form_Responses_379.xlsx"
PROC_DIR = BASE / "data" / "processed"
PROC_DIR.mkdir(parents=True, exist_ok=True)

df_raw = pd.read_excel(RAW_FILE, dtype=str)
print("RAW shape:", df_raw.shape)

# ---- Column mapping ----
C = {
    "timestamp": 0, "consent": 1, "age": 2, "sex": 3, "dept": 4, "level": 5,
    "device": 6, "freq": 7, "means": 8, "reliability": 9, "hours": 10,
    "uses": 11, "barriers": 12, "satisfaction": 13,
}
SDL = list(range(14, 38))  # 24 items
SDL_SUB = {
    "self_mgmt": list(range(1, 9)),    # SDL1-SDL8
    "desire": list(range(9, 17)),      # SDL9-SDL16
    "self_ctrl": list(range(17, 25)),  # SDL17-SDL24
}

# ---- Consent ----
print("Consent:", df_raw.iloc[:, 1].value_counts().to_dict())
df = df_raw[df_raw.iloc[:, 1].str.strip().str.lower() == "i consent"].copy().reset_index(drop=True)
N = len(df)
print("Valid N:", N)

# ---- Demographics ----
def clean_dept(s):
    s = str(s).strip().lower()
    if "nursing" in s: return "Nursing"
    if "mbbs" in s or "mb bs" in s: return "MBBS"
    if "physio" in s: return "Physiotherapy"
    if "pharm" in s: return "Pharmacology"
    if "audio" in s: return "Audiology"
    if "biochem" in s: return "Biochemistry"
    return str(s).strip().title()

df["age_num"] = pd.to_numeric(df.iloc[:, 2].str.extract(r"(\d+)")[0], errors="coerce")
df["sex_c"] = df.iloc[:, 3].str.strip()
df["dept_c"] = df.iloc[:, 4].apply(clean_dept)
df["level_c"] = df.iloc[:, 5].str.strip()
df["level_num"] = df["level_c"].str.extract(r"(\d+)").astype(float)

# ---- Internet Access ----
df["device_c"] = df.iloc[:, 6].str.strip()
df["freq_c"] = df.iloc[:, 7].str.strip()
df["means_c"] = df.iloc[:, 8].str.strip()
df["reliability_c"] = df.iloc[:, 9].str.strip()
df["hours_c"] = df.iloc[:, 10].str.strip()

# Multi-select parsing
def split_multi(s):
    return [p.strip() for p in str(s).split(",") if p.strip()]

df["uses_list"] = df.iloc[:, 11].apply(split_multi)
df["barriers_list"] = df.iloc[:, 12].apply(split_multi)

df["satisfaction_c"] = df.iloc[:, 13].str.strip()

# ---- SDL Scoring (5-point Likert) ----
LIK = {"Strongly Agree": 5, "Agree": 4, "Undecided": 3, "Disagree": 2, "Strongly Disagree": 1}

def norm_lik(v):
    t = str(v).strip()
    # Handle combined entries like "Strongly Agree, Agree"
    parts = [p.strip() for p in t.split(",")]
    vals = [LIK.get(p, np.nan) for p in parts if p in LIK]
    return np.nanmean(vals) if vals else np.nan

for i, col_idx in enumerate(SDL):
    col_name = df.columns[col_idx]
    df[f"SDL{i+1}_raw"] = df.iloc[:, col_idx]
    df[f"SDL{i+1}"] = df.iloc[:, col_idx].apply(norm_lik)

sdl_cols = [f"SDL{i+1}" for i in range(24)]
df[sdl_cols] = df[sdl_cols].apply(pd.to_numeric, errors="coerce")

df["sdl_total"] = df[sdl_cols].sum(axis=1)
df.loc[df[sdl_cols].isna().sum(axis=1) > 12, "sdl_total"] = np.nan
for name, idxs in SDL_SUB.items():
    sub_cols = [f"SDL{i}" for i in idxs]
    sub = df[sub_cols]
    df[f"sdl_{name}"] = sub.mean(axis=1)
    df.loc[sub.isna().sum(axis=1) > len(idxs)//2, f"sdl_{name}"] = np.nan

# SDL Categories (proportional to 40-item scale: 40-109 low, 110-149 moderate, 150-200 high)
# 24-item scale: 24-120. Proportional cutoffs: low ≤65, moderate 66-89, high ≥90
df["sdl_cat"] = pd.cut(df["sdl_total"], bins=[23, 65, 89, 120],
                       labels=["Low", "Moderate", "High"])

# Internet Access Composite Score (items 6-10: device, freq, means, reliability, hours)
# All coded 1-5 except device (binary) and hours (4 levels)
def score_device(v): return 5 if str(v).strip().lower() == "yes" else 1
def score_freq(v):
    m = {"Daily": 5, "Several times a week": 4, "Once a week": 3, "Rarely": 2, "Never": 1}
    return m.get(str(v).strip(), np.nan)
def score_means(v):
    m = {"Personal mobile data": 5, "Campus Wi-Fi or internet facility": 4,
         "Shared data from another person": 2, "Cybercafe": 1}
    return m.get(str(v).strip(), np.nan)
def score_reliability(v):
    m = {"Very reliable (connects consistently without interruption)": 5,
         "Fairly reliable (occasional interruptions)": 4,
         "Unreliable (frequent disconnections)": 2,
         "Very unreliable (rarely connects when needed)": 1}
    return m.get(str(v).strip(), np.nan)
def score_hours(v):
    m = {"More than 4 hours": 5, "3 to 4 hours": 4, "1 to 2 hours": 3, "Less than 1 hour": 2}
    return m.get(str(v).strip(), np.nan)

df["ia_device"] = df.iloc[:, 6].apply(score_device)
df["ia_freq"] = df.iloc[:, 7].apply(score_freq)
df["ia_means"] = df.iloc[:, 8].apply(score_means)
df["ia_reliability"] = df.iloc[:, 9].apply(score_reliability)
df["ia_hours"] = df.iloc[:, 10].apply(score_hours)

ia_cols = ["ia_device", "ia_freq", "ia_means", "ia_reliability", "ia_hours"]
df["ia_score"] = df[ia_cols].mean(axis=1)
# Mask if too many missing
df.loc[df[ia_cols].isna().sum(axis=1) > len(ia_cols)//2, "ia_score"] = np.nan

# Internet Access Level (tertile-based)
df["ia_cat"] = pd.qcut(df["ia_score"], q=3, labels=["Low", "Medium", "High"])

# Satisfaction numeric
sat_map = {"Very satisfied": 5, "Satisfied": 4, "Neutral": 3, "Dissatisfied": 2, "Very dissatisfied": 1}
df["sat_num"] = df["satisfaction_c"].map(sat_map)

# ---- Save cleaned ----
CLEAN = PROC_DIR / "internet_sdl_cleaned.csv"
df.to_csv(CLEAN, index=False)
print(f"Saved: {CLEAN} ({df.shape})")

# ---- Verification ----
print("\n--- VERIFICATION ---")
print(f"N = {N}")
print("Level:", df["level_c"].value_counts().to_dict())
print("Sex:", df["sex_c"].value_counts().to_dict())
print("Dept:", df["dept_c"].value_counts().to_dict())
print(f"IA Score: mean={df['ia_score'].mean():.2f}, median={df['ia_score'].median():.2f}")
print(f"SDL Total: mean={df['sdl_total'].mean():.2f}, median={df['sdl_total'].median():.2f}")
print("SDL Cat:", df["sdl_cat"].value_counts().to_dict())
print("IA Cat:", df["ia_cat"].value_counts().to_dict())
print(f"SDL Subscales: mgmt={df['sdl_self_mgmt'].mean():.2f}, desire={df['sdl_desire'].mean():.2f}, ctrl={df['sdl_self_ctrl'].mean():.2f}")