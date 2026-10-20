"""Malaria Prevention KAP Study — Phase 1: Clean, Score & Save."""
import warnings
import os
from pathlib import Path
import numpy as np
import pandas as pd
import json

warnings.filterwarnings("ignore")

BASE = Path("/home/garba-the-analyst/Desktop/Projects/Data analysis ")
os.chdir(BASE)

RAW_DIR = BASE / "data" / "raw" / "Assessment of Knowledge and Practice of Malaria Prevention among Undergraduate Students of FUHSI (Q-MPKP)"
RAW_FILE = RAW_DIR / "FUHSI_Malaria_Prevention_Survey_321_Responses.csv"
PROC_DIR = BASE / "data" / "processed"
PROC_DIR.mkdir(parents=True, exist_ok=True)

df_raw = pd.read_csv(RAW_FILE, dtype=str, keep_default_na=False)
print("RAW shape:", df_raw.shape)

# ---- Column mapping ----
C = {
    "timestamp": 0, "consent": 1, "age": 2, "gender": 3, "dept": 4,
    "level": 5, "residence": 6,
}
K = list(range(7, 17))          # 10 knowledge MCQ
P = list(range(17, 25))         # 8 practice frequency
M = list(range(25, 33))         # 8 misconceptions
E = list(range(33, 39))         # 6 training/experience
F = list(range(39, 43))         # 4 barriers/intent
FACULTY = 43

# ---- Consent ----
print("Consent:", df_raw.iloc[:, 1].value_counts().to_dict())
df = df_raw.copy().reset_index(drop=True)
N = len(df)
print("Valid N:", N)

# ---- Demographics ----
def clean_dept(s):
    s = str(s).strip().lower()
    if "nursing" in s: return "Nursing"
    if "mbbs" in s or "mb bs" in s: return "MBBS"
    if "mls" in s or "medical lab" in s: return "MLS"
    if "pharm" in s: return "Pharmacology"
    if "audio" in s: return "Audiology"
    if "microbiol" in s: return "Microbiology"
    if "biochem" in s: return "Biochemistry"
    if "nutrition" in s or "dietet" in s: return "Human Nutrition & Dietetics"
    if "ith" in s: return "Information Technology & Health"
    return str(s).strip().title()

def clean_level(s):
    s = str(s).strip()
    if "100" in s: return "100 Level"
    if "200" in s: return "200 Level"
    if "300" in s: return "300 Level"
    if "400" in s: return "400 Level"
    return "Other"

df["age_band"] = df.iloc[:, 2].str.strip()
df["gender_c"] = df.iloc[:, 3].str.strip()
df["dept_c"] = df.iloc[:, 4].apply(clean_dept)
df["level_c"] = df.iloc[:, 5].apply(clean_level)
df["level_num"] = df["level_c"].str.extract(r"(\d+)").astype(float)
df["residence_c"] = df.iloc[:, 6].str.strip()

# Faculty from col 43
fac_raw = df.iloc[:, 43].astype(str).str.strip()
fac_map = {
    "Faculty of Allied Health Sciences": "Allied Health",
    "Faculty of Basic Medical Sciences": "Basic Medical",
    "Faculty of Basic Clinical Sciences": "Clinical",
}
df["faculty_c"] = fac_raw.map(fac_map).fillna("Other")

# Age ordinal
age_map = {"16 – 20 years": 1, "21 – 25 years": 2, "26 – 30 years": 3}
df["age_ord"] = df["age_band"].map(age_map)

# ---- Knowledge Scoring ----
K_KEY = {
    7: "A protozoan parasite (Plasmodium) transmitted by mosquitoes",
    8: "Anopheles mosquito",
    9: "The bite of an infected female Anopheles mosquito",
    10: "Fever, chills, and headache",
    11: "Sleeping under an insecticide-treated net (ITN)",
    12: "Indoor residual spraying (IRS)",
    13: "It eliminates stagnant water and bushes where mosquitoes breed",
    14: "Seek prompt testing and treatment at a health facility",
    15: "A person can be repeatedly infected with malaria; a single episode does not confer lasting immunity",
    16: "Re-treated or replaced periodically as recommended, and washed gently only when necessary",
}

for i, col_idx in enumerate(K):
    col = df.columns[col_idx]
    correct = K_KEY[col_idx]
    df[f"K{i+1}_raw"] = df.iloc[:, col_idx]
    df[f"K{i+1}"] = (df.iloc[:, col_idx].str.strip() == correct).astype(int)

k_cols = [f"K{i+1}" for i in range(10)]
df["know_score"] = df[k_cols].sum(axis=1).astype(int)
df["know_pct"] = df["know_score"] / 10 * 100

# Fixed cutoffs
df["know_cat_fixed"] = pd.cut(df["know_score"], bins=[-1, 4, 7, 10],
                               labels=["Poor (<5)", "Moderate (5-7)", "Good (≥8)"])
# Median split
know_med = df["know_score"].median()
df["know_cat_median"] = np.where(df["know_score"] >= know_med, "Good (≥median)", "Poor (<median)")

# ---- Practice Scoring ----
PRACTICE_MAP = {"Always": 5, "Often": 4, "Sometimes": 3, "Rarely": 2, "Never": 1}

for i, col_idx in enumerate(P):
    col = df.columns[col_idx]
    df[f"P{i+1}_raw"] = df.iloc[:, col_idx]
    df[f"P{i+1}"] = df.iloc[:, col_idx].map(PRACTICE_MAP)

p_cols = [f"P{i+1}" for i in range(8)]
df["prac_score"] = df[p_cols].sum(axis=1, min_count=8)

# Fixed cutoffs
df["prac_cat_fixed"] = pd.cut(df["prac_score"], bins=[7, 17, 29, 40],
                               labels=["Poor (<18)", "Moderate (18-29)", "Good (≥30)"])
# Median split
prac_med = df["prac_score"].median()
df["prac_cat_median"] = np.where(df["prac_score"] >= prac_med, "Good (≥median)", "Poor (<median)")

# ---- Misconceptions (reverse-coded) ----
MIS_MAP = {"Strongly Agree": 1, "Agree": 2, "Neutral": 3, "Disagree": 4, "Strongly Disagree": 5}

for i, col_idx in enumerate(M):
    col = df.columns[col_idx]
    df[f"M{i+1}_raw"] = df.iloc[:, col_idx]
    df[f"M{i+1}"] = df.iloc[:, col_idx].map(MIS_MAP)

m_cols = [f"M{i+1}" for i in range(8)]
df["mis_score"] = df[m_cols].sum(axis=1, min_count=8)

# ---- Training / Experience ----
df["training_raw"] = df.iloc[:, 33]
df["training_c"] = df.iloc[:, 33].str.strip()
df["source_raw"] = df.iloc[:, 34]
df["source_c"] = df.iloc[:, 34].str.strip()
df["diagnosed_raw"] = df.iloc[:, 35]
df["diagnosed_c"] = df.iloc[:, 35].str.strip()
df["itn_own_raw"] = df.iloc[:, 36]
df["itn_own_c"] = df.iloc[:, 36].str.strip()
df["access_raw"] = df.iloc[:, 37]
df["access_c"] = df.iloc[:, 37].str.strip()

# Barriers / Intent
df["net_purchase_raw"] = df.iloc[:, 38]
df["net_purchase_c"] = df.iloc[:, 38].str.strip()
df["comfort_raw"] = df.iloc[:, 39]
df["comfort_c"] = df.iloc[:, 39].str.strip()
df["treat24_raw"] = df.iloc[:, 40]
df["treat24_c"] = df.iloc[:, 40].str.strip()
df["sanit_raw"] = df.iloc[:, 41]
df["sanit_c"] = df.iloc[:, 41].str.strip()
df["talk_raw"] = df.iloc[:, 42]
df["talk_c"] = df.iloc[:, 42].str.strip()

# ---- Gap Score ----
df["know_z"] = (df["know_score"] - df["know_score"].mean()) / df["know_score"].std()
df["prac_z"] = (df["prac_score"] - df["prac_score"].mean()) / df["prac_score"].std()
df["gap_score"] = df["prac_z"] - df["know_z"]

# ---- Save cleaned ----
CLEAN = PROC_DIR / "malaria_kap_cleaned.csv"
df.to_csv(CLEAN, index=False)

# Item labels for later use
labels = {
    "knowledge": [str(df.columns[i]) for i in K],
    "knowledge_key": {str(i+1): K_KEY[K[i]] for i in range(10)},
    "practice": [str(df.columns[i]) for i in P],
    "misconceptions": [str(df.columns[i]) for i in M],
    "practice_map": PRACTICE_MAP,
    "mis_map": MIS_MAP,
}
(PROC_DIR / "malaria_item_labels.json").write_text(json.dumps(labels, indent=2))

# ---- Verification ----
print("\n--- VERIFICATION ---")
print(f"N = {N}")
print("Level:", df["level_c"].value_counts().to_dict())
print("Gender:", df["gender_c"].value_counts().to_dict())
print("Residence:", df["residence_c"].value_counts().to_dict())
print("Faculty:", df["faculty_c"].value_counts().to_dict())
print(f"\nKnowledge: mean={df['know_score'].mean():.2f}, median={know_med}, SD={df['know_score'].std():.2f}")
print("Fixed cats:", df["know_cat_fixed"].value_counts().to_dict())
print("Median cats:", df["know_cat_median"].value_counts().to_dict())
print(f"\nPractice: mean={df['prac_score'].mean():.2f}, median={prac_med}, SD={df['prac_score'].std():.2f}")
print("Fixed cats:", df["prac_cat_fixed"].value_counts().to_dict())
print("Median cats:", df["prac_cat_median"].value_counts().to_dict())
print(f"\nMisconceptions: mean={df['mis_score'].mean():.2f}, SD={df['mis_score'].std():.2f}")
print(f"\nTraining Yes: {(df['training_c']=='Yes').sum()}, No: {(df['training_c']=='No').sum()}")
print("ITN Own:", df["itn_own_c"].value_counts().to_dict())
print("Access:", df["access_c"].value_counts().to_dict())
print("Gap score: mean=0, SD=", round(df["gap_score"].std(), 3))
print(f"\nSaved: {CLEAN} ({df.shape})")