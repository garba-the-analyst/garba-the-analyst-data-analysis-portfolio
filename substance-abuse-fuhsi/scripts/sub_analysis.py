"""Substance Abuse Study — Step 1: load, clean, score."""
import warnings
import ast
import os
import sys
from pathlib import Path
import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")

# Force working directory to the one with trailing space
PROJECT_ROOT = "/home/garba-the-analyst/Desktop/Projects/Data analysis "
os.chdir(PROJECT_ROOT)

RAW_CSV = os.path.join(PROJECT_ROOT, "data/raw/Assessment of Substance Abuse and Perceived Health Implications Among Undergraduate Students of FUHSI 5/FUHSI_Substance_Abuse_Survey_395_Responses.csv")
PROC_DIR = Path(os.path.join(PROJECT_ROOT, "data/processed"))
PROC_DIR.mkdir(parents=True, exist_ok=True)

df_raw = pd.read_csv(RAW_CSV, dtype=str, keep_default_na=False)
cols = list(df_raw.columns)
print("RAW shape:", df_raw.shape)
print("Columns:", len(cols))

C = {"timestamp": cols[0], "consent": cols[1], "age": cols[2], "sex": cols[3],
     "level": cols[4], "faculty": cols[5], "religion": cols[6], "marital": cols[7],
     "living": cols[8], "allowance": cols[9]}
SU = {"ever_use": cols[10], "past_3mo": cols[11], "substances": cols[12],
      "frequency": cols[13], "poly_use": cols[14], "should_reduce": cols[15],
      "withdrawal": cols[16]}
FACTORS = cols[17:30]
HEALTH = cols[30:42]
PREVENTION = cols[42:50]

print("Consent:", df_raw[C["consent"]].value_counts().to_dict())
df = df_raw[df_raw[C["consent"]].str.strip().str.lower().str.contains("agree")].copy().reset_index(drop=True)
print("After consent:", df.shape)

def clean_level(s):
    s = str(s).strip()
    if "100" in s: return "100 Level"
    if "200" in s: return "200 Level"
    if "300" in s: return "300 Level"
    if "400" in s: return "400 Level"
    if "500" in s: return "500 Level"
    return "Other"

def clean_faculty(s):
    s = str(s).strip().lower()
    if "allied" in s: return "Allied Health Sciences"
    if "basic medical" in s: return "Basic Medical Sciences"
    if "clinical" in s: return "Clinical Sciences"
    if "science" in s and "basic" not in s and "clinical" not in s and "allied" not in s: return "Faculty of Sciences"
    return str(s).strip()

def clean_religion(s):
    s = str(s).strip()
    if s.lower() in ["islam", "muslim"]: return "Islam"
    if s.lower() in ["christianity", "christian"]: return "Christianity"
    return s

df["age_c"] = df[cols[2]].str.strip()
df["sex_c"] = df[cols[3]].str.strip()
df["level_c"] = df[cols[4]].apply(clean_level)
df["faculty_c"] = df[cols[5]].apply(clean_faculty)
df["religion_c"] = df[cols[6]].apply(clean_religion)
df["marital_c"] = df[cols[7]].str.strip()
df["living_c"] = df[cols[8]].str.strip()
df["allowance_c"] = df[cols[9]].str.strip()

print("\nDemographics:")
for c in ["age_c", "sex_c", "level_c", "faculty_c", "religion_c", "marital_c", "living_c", "allowance_c"]:
    print(f"\n{c}:")
    print(df[c].value_counts().to_string())

# Substance Use
def norm_yn(s):
    s = str(s).strip().lower()
    if s.startswith("yes"): return "Yes"
    if s.startswith("no"): return "No"
    return s

df["ever_use_c"] = df.iloc[:, 10].apply(norm_yn)
df["past_3mo_c"] = df.iloc[:, 11].apply(norm_yn)

def split_subs(s):
    if not isinstance(s, str): return []
    s = s.strip()
    if s in ["", "None", "Not applicable", "Not at all", "N/A", "n/a", "Na", "NA", "none", "not applicable"]:
        return []
    return [p.strip() for p in s.split(";") if p.strip()]

df["substances_list"] = df.iloc[:, 12].apply(split_subs)
# CSV-safe string form (semicolon-joined, no Python list repr)
df["substances_str"] = df["substances_list"].apply(lambda L: ";".join(L))

freq_map = {"Not applicable": 0, "Not at all": 0, "": 0,
            "Less than once a week": 1,
            "1–2 times per week": 2,
            "3–6 times per week": 3}
df["freq_c"] = df.iloc[:, 13].str.strip().map(freq_map).fillna(0).astype(int)

df["poly_use_c"] = df.iloc[:, 14].apply(norm_yn)
df["should_reduce_c"] = df.iloc[:, 15].apply(norm_yn)
df["withdrawal_c"] = df.iloc[:, 16].apply(norm_yn)
df["problem_use"] = ((df["should_reduce_c"] == "Yes") | (df["withdrawal_c"] == "Yes")).astype(int)
df["any_substance_3mo"] = (df["past_3mo_c"] == "Yes").astype(int)
df["primary_substance"] = df["substances_list"].apply(lambda x: x[0] if x else "None")

print("\nSubstance Use:")
print("Ever use:", df["ever_use_c"].value_counts().to_dict())
print("Past 3mo:", df["past_3mo_c"].value_counts().to_dict())
print("Any 3mo:", df["any_substance_3mo"].value_counts().to_dict())
print("Freq:", df["freq_c"].value_counts().sort_index().to_dict())
print("Poly:", df["poly_use_c"].value_counts().to_dict())
print("Should reduce:", df["should_reduce_c"].value_counts().to_dict())
print("Withdrawal:", df["withdrawal_c"].value_counts().to_dict())
print("Problem use:", df["problem_use"].value_counts().to_dict())
print("Primary:", df["primary_substance"].value_counts().to_dict())

from collections import Counter
all_subs = []
for lst in df["substances_list"]:
    all_subs.extend(lst)
sub_counts = Counter(all_subs)
print("\nSubstance mentions:")
for sub, cnt in sub_counts.most_common():
    print(f"  {sub}: {cnt} ({cnt/len(df)*100:.1f}%)")

# Likert scales
LIKERT_MAP = {"SA": 5, "A": 4, "U": 3, "D": 2, "SD": 1}
def norm_likert(s):
    s = str(s).strip().upper()
    return LIKERT_MAP.get(s, np.nan)

# Factors Q17-Q29 (13 items)
FACTOR_LABELS = ["Peer pressure", "Academic stress", "Curiosity/experimentation",
    "Easy availability", "Family member use", "Social media exposure",
    "Emotional distress", "Coping with pain/stress/sleep",
    "Social gatherings/parties", "Low self-esteem",
    "Limited parental monitoring", "Boredom/unstructured time",
    "Inadequate policy enforcement"]

factor_cols = []
for i, col in enumerate(df.columns[17:30]):
    label = FACTOR_LABELS[i] if i < len(FACTOR_LABELS) else f"Factor {i+1}"
    df[f"factor_{i+1:02d}"] = df[col].apply(norm_likert)
    factor_cols.append(f"factor_{i+1:02d}")
    print(f"Factor {i+1} ({label}): mean={df[f'factor_{i+1:02d}'].mean():.2f}")

df["factor_score"] = df[factor_cols].mean(axis=1)
df["factor_peer_social"] = df[["factor_01", "factor_09", "factor_10"]].mean(axis=1)
df["factor_academic"] = df[["factor_02"]].mean(axis=1)
df["factor_emotional"] = df[["factor_07", "factor_08"]].mean(axis=1)
df["factor_availability"] = df[["factor_04"]].mean(axis=1)
df["factor_family"] = df[["factor_05", "factor_11"]].mean(axis=1)
df["factor_social_media"] = df[["factor_06"]].mean(axis=1)
df["factor_boredom"] = df[["factor_12"]].mean(axis=1)
df["factor_policy"] = df[["factor_13"]].mean(axis=1)

# Health Q30-Q41 (12 items)
HEALTH_LABELS = ["Dependence/addiction", "Cardiovascular problems", "Respiratory problems",
    "Anxiety/depression/mental health", "Sleep disturbances",
    "Impaired concentration/memory", "Impaired judgement/decision-making",
    "Risky sexual behaviour", "Accidents/injuries",
    "Long-term organ damage", "Relationship problems", "Academic performance"]

HEALTH_DOMAINS = {
    "physical": [0, 1, 2, 8, 9],      # Q30,31,32,38,39
    "psychological": [3, 4, 6],        # Q33,34,36
    "social": [7, 10],                 # Q37,40
    "academic": [5, 11],               # Q35,41
}
health_cols = []
for i, col in enumerate(df.columns[30:42]):
    label = HEALTH_LABELS[i] if i < len(HEALTH_LABELS) else f"Health {i+1}"
    df[f"health_{i+1:02d}"] = df[col].apply(norm_likert)
    health_cols.append(f"health_{i+1:02d}")
    print(f"Health {i+1} ({label}): mean={df[f'health_{i+1:02d}'].mean():.2f}")

df["health_score"] = df[health_cols].mean(axis=1)
for domain, idxs in HEALTH_DOMAINS.items():
    df[f"health_{domain}"] = df[[f"health_{i+1:02d}" for i in idxs]].mean(axis=1)

# Prevention Q42-Q49 (8 items)
PREV_LABELS = ["Counselling/mental health", "Education/awareness campaigns",
    "Peer-led education/support", "University policies/disciplinary measures",
    "Early identification/screening/referral", "Parental/family involvement",
    "Religious/spiritual support", "Recreational/extracurricular activities"]

prev_cols = []
for i, col in enumerate(df.columns[42:50]):
    label = PREV_LABELS[i] if i < len(PREV_LABELS) else f"Prevention {i+1}"
    df[f"prev_{i+1:02d}"] = df[col].apply(norm_likert)
    prev_cols.append(f"prev_{i+1:02d}")
    print(f"Prevention {i+1} ({label}): mean={df[f'prev_{i+1:02d}'].mean():.2f}")

df["prev_score"] = df[prev_cols].mean(axis=1)

# Reliability
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

alpha_f, n_f = cronbach(df[factor_cols])
alpha_h, n_h = cronbach(df[health_cols])
alpha_p, n_p = cronbach(df[prev_cols])
print(f"\nReliability: Factors α={alpha_f:.3f} (n={n_f}), Health α={alpha_h:.3f} (n={n_h}), Prevention α={alpha_p:.3f} (n={n_p})")

# Save (drop list column; keep stringified-free substances_str)
out = df.drop(columns=["substances_list"]).rename(columns={"substances_str": "substances_list"})
PROC_DIR = Path("data/processed")
PROC_DIR.mkdir(parents=True, exist_ok=True)
out.to_csv(PROC_DIR / "substance_abuse_cleaned_full.csv", index=False)
print(f"\nSaved: {PROC_DIR / 'substance_abuse_cleaned_full.csv'} ({out.shape})")
print("DONE STEP 1")