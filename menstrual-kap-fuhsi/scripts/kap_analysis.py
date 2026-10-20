"""FUHSI KAP study — Phase 1: clean, score and categorise per thesis Ch.1 & §3.11.
Run:  .venv/bin/python kap_analysis.py
Outputs: data/processed/kap_cleaned_full.csv, data/processed/kap_item_labels.json
"""
from pathlib import Path
import json
import re
from datetime import date
import warnings
import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")
TODAY = date(2026, 10, 18)

BASE = Path(__file__).resolve().parent
STUDY_DIR = BASE / "data" / "raw" / "Knowledge, Attitude and Health-Seeking Behavior Regarding Menstrual Irregularities Among Undergraduate Female Students of Federal University of Health Sciences Ila-Orangun."
RAW_CSV = next(STUDY_DIR.glob("*.csv"))
PROC_DIR = BASE / "data" / "processed"
PROC_DIR.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------- load
df_raw = pd.read_csv(RAW_CSV, dtype=str, keep_default_na=False)
cols = list(df_raw.columns)
print("RAW shape:", df_raw.shape)

C = {"timestamp": cols[0], "consent": cols[1], "age": cols[2], "level": cols[3],
     "dept": cols[4], "marital": cols[5], "ethnicity": cols[6], "menarche": cols[7]}
K = cols[8:20]
A = cols[20:30]
H = cols[30:39]
B = cols[39:53]
QH = {"exp": H[0], "type": H[1], "action": H[2], "time": H[3], "info": H[4],
      "campus": H[5], "facility": H[6], "barrier": H[7], "future": H[8]}
Q2_DUP = cols[53]
print("Consent values:", df_raw[C["consent"]].value_counts().to_dict())

df = df_raw[df_raw[C["consent"]].str.strip().str.lower().str.startswith("yes")].copy().reset_index(drop=True)
N = len(df)
print("Valid consenting sample:", N)

# ---------------------------------------------------------------- demographics
def band_of(a):
    if 16 <= a <= 20: return "16-20 years"
    if 21 <= a <= 24: return "21-24 years"
    if 25 <= a <= 30: return "25-30 years"
    return "Above 30 years"

WORDS = {"thirteen": 13, "fourteen": 14, "fifteen": 15, "sixteen": 16, "seventeen": 17,
         "eighteen": 18, "nineteen": 19, "twenty": 20, "twenty one": 21, "twenty two": 22,
         "twenty three": 23, "twenty four": 24, "twenty five": 25}

def parse_age(v):
    t = str(v).strip().lower()
    if not t:
        return np.nan, "Not stated"
    m = re.fullmatch(r"(\d{1,2})/(\d{1,2})/(\d{4})", t)
    if m:
        dob = date(int(m.group(3)), int(m.group(2)), int(m.group(1)))
        a = TODAY.year - dob.year - ((TODAY.month, TODAY.day) < (dob.month, dob.day))
        return a, band_of(a)
    if re.fullmatch(r"(above|over)\s*30.*", t):
        return np.nan, "Above 30 years"
    m = re.search(r"(twenty[- ]one|twenty[- ]two|twenty[- ]three|twenty[- ]four|twenty[- ]five|twenty|nineteen|eighteen|seventeen|sixteen|fifteen|fourteen|thirteen)", t)
    if m:
        a = WORDS[m.group(1).replace(" ", " ").replace("-", " ")]
        return a, band_of(a)
    m = re.match(r"^(16-20|21-24|25-30)\s*years", t)
    if m:
        return np.nan, m.group(1) + " years"
    m = re.match(r"^(\d{1,2})(?:\s*(?:years?|yrs?|old)|\+|\b|$)", t)
    if m:
        a = int(m.group(1))
        if 10 <= a <= 40:
            return a, band_of(a)
    return np.nan, "Not stated"

age_parsed = df[C["age"]].apply(parse_age)
df["age_num"] = [x[0] for x in age_parsed]
df["age_band"] = [x[1] for x in age_parsed]

LEVELS = ["100 level", "200 level", "300 level", "400 level"]
df["level_c"] = df[C["level"]].str.strip()
df["level_num"] = df["level_c"].str.extract(r"(\d+)").astype(float)

DEPT_FIX = {"prosthetics and orthotics": "Prosthetics and Orthotics",
            "human nutrition and dietetics": "Human Nutrition and Dietetics"}
df["dept_c"] = df[C["dept"]].str.strip()
df["dept_c"] = df["dept_c"].apply(lambda v: DEPT_FIX.get(str(v).lower(), str(v).strip()))

df["marital_c"] = df[C["marital"]].str.strip()
ETH_FIX = {"idoma": "Idoma", "ebira": "Ebira"}
df["ethnicity_c"] = df[C["ethnicity"]].str.strip().apply(lambda v: ETH_FIX.get(v.lower(), v))
df["menarche_c"] = df[C["menarche"]].str.replace(r"\s*-\s*", "-", regex=True).str.strip()

# ---------------------------------------------------------------- knowledge scoring
def text_of(hdr):
    m = re.search(r"\d+\.\s*(.+?)\s*\]", hdr, re.S)
    return re.sub(r"\s+", " ", m.group(1)).strip() if m else hdr.strip()

k_labels = [text_of(cols[8 + i]) for i in range(12)]
K_KEY = {i: "True" for i in range(12)}
K_KEY[9] = "False"                                   # item 10: "...never need medical attention"

def norm_bool(v):
    t = str(v).strip().lower()
    if t.startswith("true"): return "True"
    if t.startswith("false"): return "False"
    if "don" in t or "not sure" in t: return "Don't know"
    return "Other:" + str(v).strip()

for i, c in enumerate(K):
    df[f"K{i+1}_raw"] = df[c]
    df[f"K{i+1}"] = df[c].apply(norm_bool)
    df[f"K{i+1}__n"] = (df[f"K{i+1}"] == K_KEY[i]).astype(int)
    odd = set(df[f"K{i+1}"]) - {"True", "False", "Don't know"}
    if odd: print(f"WARN K{i+1} unexpected values:", odd)
know_items = [f"K{i+1}__n" for i in range(12)]
df["know_score"] = df[know_items].sum(axis=1).astype(int)
df["know_pct"] = df["know_score"] / 12 * 100

# ---------------------------------------------------------------- attitude scoring
a_labels = [text_of(cols[20 + i]) for i in range(10)]
LIK = {"SA": 5, "A": 4, "U": 3, "D": 2, "SD": 1}
ATT_REV = {0, 1, 3, 9}                               # items 1,2,4,10 negatively worded

def norm_lik(v):
    t = str(v).strip().upper().replace("STRONGLY AGREE", "SA").replace("STRONGLY DISAGREE", "SD")
    t = {"AGREE": "A", "DISAGREE": "D", "NOT SURE": "U", "UNDECIDED": "U", "NEUTRAL": "U"}.get(t, t)
    return t if t in LIK else None

for i, c in enumerate(A):
    df[f"A{i+1}_raw"] = df[c]
    lv = df[c].apply(norm_lik)
    odd = set(lv.dropna().unique()) - set(LIK)
    if odd: print(f"WARN A{i+1} unexpected values:", odd)
    num = lv.map(LIK).astype(float)
    df[f"A{i+1}__n"] = np.where(i in ATT_REV, 6 - num, num)
att_items = [f"A{i+1}__n" for i in range(10)]
df["att_score"] = df[att_items].sum(axis=1, min_count=10)

# ---------------------------------------------------------------- HBM scoring
b_labels = [text_of(cols[39 + i]) for i in range(14)]
for i, c in enumerate(B):
    df[f"E{i+1}_raw"] = df[c]
    num = df[c].apply(norm_lik).map(LIK).astype(float)
    df[f"E{i+1}__n"] = num
hbm_items = [f"E{i+1}__n" for i in range(14)]
HBM_GROUPS = {"susceptibility": [0, 1], "severity": [2, 3], "benefit": [4, 5],
              "barrier": [6, 7, 8, 9], "cues": [10, 11], "self_efficacy": [12, 13]}
for g, idxs in HBM_GROUPS.items():
    sub = df[[f"E{i+1}__n" for i in idxs]]
    df[f"hbm_{g}"] = sub.mean(axis=1).where(sub.notna().all(axis=1))

# ---------------------------------------------------------------- categorisation (mean + median splits)
kn_mean, kn_med = df["know_score"].mean(), df["know_score"].median()
at_mean, at_med = df["att_score"].mean(), df["att_score"].median()
df["know_cat_mean"] = np.where(df["know_score"] >= kn_mean, "Good", "Poor")
df["know_cat_median"] = np.where(df["know_score"] >= kn_med, "Good", "Poor")
df["att_cat_mean"] = np.where(df["att_score"] >= at_mean, "Positive", "Negative")
df["att_cat_median"] = np.where(df["att_score"] >= at_med, "Positive", "Negative")

# ---------------------------------------------------------------- behaviour variables
def split_multi(s):
    return [p.strip() for p in str(s).split(";") if p.strip()]

df["exp_c"] = df[QH["exp"]].apply(lambda v: "Yes" if str(v).strip().lower().startswith("yes") else "No")

TYPE_CANON = ["Irregular cycle length", "Severe menstrual pain (dysmenorrhea)",
              "Heavy/prolonged bleeding (menorrhagia)", "Absence of menstruation (amenorrhea)"]
NONE_SET = {"none", "nil", "no", ".", "0", "not applicable", "haven't experienced any",
            "i haven't experienced any", "i have not experienced any of it."}

def norm_type_part(p):
    t = str(p).strip().lower()
    if t in NONE_SET:
        return []
    if t.startswith("irregular cycle"):
        return [TYPE_CANON[0]]
    if t.startswith("severe menstrual pain"):
        return [TYPE_CANON[1]]
    if t.startswith("heavy"):
        return [TYPE_CANON[2]]
    if t.startswith("absence"):
        return [TYPE_CANON[3]]
    if "cramp" in t or "pain" in t:
        return [TYPE_CANON[1]]
    if "extended days" in t:
        return [TYPE_CANON[2]]
    if "all of the above" in t:
        return list(TYPE_CANON)
    return ["Other"]

others_seen = {}
def norm_type_cell(*raw_vals):
    found, other = [], []
    for rv in raw_vals:
        for p in split_multi(rv):
            res = norm_type_part(p)
            if res == ["Other"] and p not in others_seen:
                others_seen[p] = True
            for r in res:
                if r not in found:
                    found.append(r)
    return found

type_rows = [norm_type_cell(a, b) for a, b in zip(df[QH["type"]], df[Q2_DUP])]
df["type_list"] = [";".join(t) for t in type_rows]
df["type_n"] = [len(t) for t in type_rows]
if others_seen:
    print("WARN type free-text mapped to Other:", list(others_seen))

def norm_action(v):
    t = str(v).strip().lower()
    if not t or t in NONE_SET or "none of the above" in t or "didn't" in t or "haven't" in t:
        return "No action reported"
    if "doctor" in t or "gyn" in t:
        return "Consulted a doctor/gynaecologist"
    if "mum" in t or "mother" in t or "friend" in t or "family" in t:
        return "Consulted a friend or family member"
    if "campus" in t or "school health" in t:
        return "Visited the campus/school health center"
    if "hospital or clinic outside" in t:
        return "Visited a hospital or clinic outside campus"
    if "ignored" in t or "did nothing" in t or "hoping and praying" in t:
        return "Ignored it / did nothing"
    if "self-medic" in t:
        return "Self-medicated"
    if "home remedy" in t:
        return "Used a home remedy"
    if "pharmacist" in t:
        return "Consulted a pharmacist"
    return "Other"

others_seen.clear()
df["action_c"] = df[QH["action"]].apply(lambda v: norm_action(v) if norm_action(v) != "Other" else "Other")
for v in df[QH["action"]]:
    if norm_action(v) == "Other":
        others_seen[str(v).strip()] = True
if others_seen:
    print("WARN action free-text mapped to Other:", list(others_seen))

def norm_time(v):
    t = str(v).strip().lower()
    if t.startswith("immediately"): return "Immediately"
    if t.startswith("within a week"): return "Within a week"
    if t.startswith("within a month"): return "Within a month"
    if t.startswith("after more than a month"): return "More than a month"
    if t.startswith("i did not seek"): return "Did not seek"
    return "Not stated"

df["time_c"] = df[QH["time"]].apply(norm_time)
df["sought_ever"] = np.where(df["time_c"].isin(["Immediately", "Within a week",
        "Within a month", "More than a month"]), "Sought professional help",
        np.where(df["time_c"] == "Did not seek", "Never sought help",
                 np.where(df["exp_c"] == "No", "N/A (never experienced)", "Not stated")))

INFO_CANON = ["Social media", "Internet/websites", "Healthcare provider (nurse, doctor, pharmacist)",
              "School/health talks or campaigns", "Friends or peers",
              "Family members (mother, sister, relative)", "Textbooks/course materials"]

def norm_info_part(p):
    t = str(p).strip().lower()
    if t in {"nil", "no where", "nowhere"} or "not sat down" in t:
        return "None"
    if "app" in t:
        return "Other"
    for c in INFO_CANON:
        if t.startswith(c.lower().split("(")[0].strip()[:14]):
            return c
    return {"social media": INFO_CANON[0], "internet": INFO_CANON[1],
            "healthcare": INFO_CANON[2], "school": INFO_CANON[3],
            "friends": INFO_CANON[4], "family": INFO_CANON[5],
            "textbook": INFO_CANON[6]}.get(t.split("(")[0].strip()[:9], None)

others_seen.clear()
info_rows = []
for v in df[QH["info"]]:
    parts = []
    for p in split_multi(v):
        r = norm_info_part(p)
        if r is None and p not in others_seen:
            others_seen[str(p).strip()] = True
            r = "Other"
        if r and r not in parts:
            parts.append(r)
    if any(x != "None" for x in parts) and "None" in parts:
        parts.remove("None")
    info_rows.append(parts)
if others_seen:
    print("WARN info free-text:", list(others_seen))
df["info_list"] = [";".join(p) for p in info_rows]

df["campus_c"] = df[QH["campus"]].str.strip()

FAC_CANON = ["Private clinic", "General/teaching hospital", "Campus/school health center",
             "Pharmacy/patent medicine store", "Traditional healer"]

def norm_facility(v):
    t = str(v).strip().lower()
    if not t or t in {"nil", "none", "0", "."}:
        return "Not stated"
    for f in FAC_CANON:
        if t.startswith(f.lower()[:14]):
            return f
    if "pharmacy" in t or "medicine store" in t:
        return FAC_CANON[3]
    if "female doctors at a hospital" in t:
        return FAC_CANON[1]
    return "Other"

others_seen.clear()
for v in df[QH["facility"]]:
    if norm_facility(v) == "Other" and str(v).strip().lower() not in {"nil", "none"}:
        others_seen[str(v).strip()] = True
if others_seen:
    print("WARN facility free-text mapped to Other:", list(others_seen))
df["facility_c"] = df[QH["facility"]].apply(norm_facility)

BAR_CANON = ["Belief that it would resolve on its own", "Cost of healthcare", "Lack of time",
             "Embarrassment", "Not knowing where to go", "Cultural or religious reasons"]
NOTHING_SET = {"nothing", "no reason", "none", "0", "nothing can prevent me", "i don't have any issues",
               "i barely experience it", "because it's a minor issue"}

def norm_barrier_part(p):
    t = str(p).strip().lower()
    if not t or t in NOTHING_SET or "don't have any reason" in t or "nothing will prevent" in t:
        return "Nothing prevents me" if ("nothing" in t or "reason" in t or "issues" in t
                                          or "minor" in t or "barely" in t or t == "0") else None
    for b in BAR_CANON:
        if t.startswith(b.lower()[:16]):
            return b
    if "minor" in t or "resolve" in t or "on its own" in t:
        return BAR_CANON[0]
    if "cost" in t:
        return BAR_CANON[1]
    if "time" in t:
        return BAR_CANON[2]
    if "embarrass" in t:
        return BAR_CANON[3]
    if "where" in t:
        return BAR_CANON[4]
    if "cultural" in t:
        return BAR_CANON[5]
    return "Other"

others_seen.clear()
bar_rows = []
for v in df[QH["barrier"]]:
    parts = []
    for p in split_multi(v):
        r = norm_barrier_part(p)
        if r is None:
            continue
        if r == "Other" and p not in others_seen:
            others_seen[str(p).strip()] = True
        if r not in parts:
            parts.append(r)
    bar_rows.append(parts)
if others_seen:
    print("WARN barrier free-text mapped to Other:", list(others_seen))
df["barrier_list"] = [";".join(p) for p in bar_rows]

def norm_future(v):
    t = str(v).strip().lower()
    if t == "yes": return "Yes"
    if "sure" in t: return "Not sure"
    return "No"

df["future_c"] = df[QH["future"]].apply(norm_future)

# ---------------------------------------------------------------- reliability
def cronbach(item_df):
    d = item_df.dropna()
    k = d.shape[1]
    if k < 2 or len(d) < 3: return np.nan
    iv = d.var(axis=0, ddof=1).sum()
    tv = d.sum(axis=1).var(ddof=1)
    return k / (k - 1) * (1 - iv / tv) if tv > 0 else np.nan

def kr20(item_df):
    d = item_df.dropna()
    p = d.mean(axis=0)
    tv = d.sum(axis=1).var(ddof=1)
    k = d.shape[1]
    return k / (k - 1) * (1 - (p * (1 - p)).sum() / tv) if tv > 0 else np.nan

hits = df[know_items]
ALPHAS = {"knowledge_kr20": kr20(hits), "attitude": cronbach(df[att_items]),
          "hbm_total": cronbach(df[hbm_items])}
for g, idxs in HBM_GROUPS.items():
    ALPHAS[f"hbm_{g}"] = cronbach(df[[f"E{i+1}__n" for i in idxs]])

# ---------------------------------------------------------------- save
drop_raw = []
out = df.copy()
keep_cols = ([c for c in out.columns if not c.endswith("_raw") and c not in list(K) + list(A) + list(B) + [Q2_DUP]]
             + [f"K{i+1}_raw" for i in range(12)] + [f"A{i+1}_raw" for i in range(10)]
             + [f"E{i+1}_raw" for i in range(14)] + [f"hbm_{g}" for g in HBM_GROUPS])
out = out[keep_cols]
CLEAN = PROC_DIR / "kap_cleaned_full.csv"
out.to_csv(CLEAN, index=False)

labels = {"k": k_labels, "k_key": K_KEY, "a": a_labels, "a_rev": sorted(ATT_REV),
          "hbm": b_labels, "hbm_groups": {g: [i + 1 for i in v] for g, v in HBM_GROUPS.items()},
          "type_canon": TYPE_CANON, "info_canon": INFO_CANON, "facility_canon": FAC_CANON,
          "bar_canon": BAR_CANON, "alphas": ALPHAS}
(PROC_DIR / "kap_item_labels.json").write_text(json.dumps(labels, indent=2))

# ---------------------------------------------------------------- verification summary
print("\n--- VERIFICATION ---")
print("N =", N, "| experienced:", df["exp_c"].value_counts().to_dict())
print("level:", df["level_c"].value_counts().reindex(LEVELS).to_dict())
print("age valid:", df["age_num"].notna().sum(), f"mean={df['age_num'].mean():.2f}",
      "bands:", df["age_band"].value_counts().to_dict())
print("know_score mean/median:", round(kn_mean, 2), kn_med, "| cats(mean):",
      df["know_cat_mean"].value_counts().to_dict(), "cats(median):",
      df["know_cat_median"].value_counts().to_dict())
print("att_score mean/median:", round(at_mean, 2), at_med, "| cats(mean):",
      df["att_cat_mean"].value_counts().to_dict(), "cats(median):",
      df["att_cat_median"].value_counts().to_dict())
print("HBM means:", {g: round(df[f"hbm_{g}"].mean(), 2) for g in HBM_GROUPS})
from collections import Counter
tc = Counter(t for row in type_rows for t in row)
pc = Counter()
for rv, rv2 in zip(df[QH["type"]], df[Q2_DUP]):
    for p in split_multi(rv) + split_multi(rv2):
        for r in norm_type_part(p):
            pc[r] += 1
print("Type part census:", dict(pc), "| union (deduped):", dict(tc))
print("type mentioned at all:", sum(1 for r in type_rows if r), "| other/free:", tc.get("Other", 0))
exp_yes = df["exp_c"] == "Yes"
print("types reported by experienced:", sum(1 for r, e in zip(type_rows, exp_yes) if r and e),
      "| by non-experienced:", sum(1 for r, e in zip(type_rows, exp_yes) if r and not e))
print("future:", df["future_c"].value_counts().to_dict())
print("sought_ever:", df["sought_ever"].value_counts().to_dict())
print("campus:", df["campus_c"].value_counts().to_dict())
print("facility:", df["facility_c"].value_counts().to_dict())
print("alphas:", {k: round(v, 3) for k, v in ALPHAS.items()})
print("Saved:", CLEAN, out.shape)
