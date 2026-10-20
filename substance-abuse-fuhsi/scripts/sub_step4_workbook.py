"""Substance Abuse Study — Step 4: XLSX workbook (clean version - no weights/fieldwork).
Run: cd "/home/garba-the-analyst/Desktop/Projects/Data analysis " && /home/garba-the-analyst/.venvs/global/bin/python sub_step4_workbook.py
"""
import warnings
import os
from pathlib import Path
from collections import Counter
import pandas as pd
import numpy as np
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from openpyxl.utils.dataframe import dataframe_to_rows
from openpyxl.drawing.image import Image as XLImage
from openpyxl.chart import BarChart, PieChart, DoughnutChart, Reference

warnings.filterwarnings("ignore")
PROJECT_ROOT = "/home/garba-the-analyst/Desktop/Projects/Data analysis "
os.chdir(PROJECT_ROOT)

TAB_DIR = Path(PROJECT_ROOT) / "reports/Assessment of Substance Abuse and Perceived Health Implications Among Undergraduate Students of FUHSI 5/03_Tables"
FIG_DIR = Path("reports/output/figures")
OUT_FILE = Path("reports/output/Substance_Abuse_Full_Analysis.xlsx")

HDR_FILL = PatternFill("solid", fgColor="1F4E78")
HDR_FONT = Font(bold=True, color="FFFFFF", size=10)
TITLE_FONT = Font(bold=True, size=13, color="1F4E78")
SUB_FONT = Font(bold=True, size=11, color="1F4E78")
THIN = Border(*(Side(style="thin", color="BFBFBF"),) * 4)
WRAP = Alignment(wrap_text=True, vertical="top")

def write_df(ws, df, start_row=1, widths=None):
    for r in dataframe_to_rows(df, index=False, header=True):
        ws.append(r)
    for c in range(1, len(df.columns) + 1):
        cell = ws.cell(row=start_row, column=c)
        cell.fill = HDR_FILL
        cell.font = HDR_FONT
        cell.alignment = Alignment(wrap_text=True, vertical="center")
    ws.freeze_panes = "A2"
    ws.auto_filter.ref = f"A{start_row}:{get_column_letter(len(df.columns))}{ws.max_row}"
    for row in ws.iter_rows(min_row=start_row + 1):
        for cell in row:
            cell.border = Border(*(Side(style="thin", color="BFBFBF"),) * 4)
    if widths:
        for i, w in enumerate(widths, 1):
            ws.column_dimensions[get_column_letter(i)].width = w
    else:
        for i, col in enumerate(df.columns, 1):
            m = max([len(str(col))] + [len(str(v)) for v in df[col].astype(str).head(40)]) if len(df) else 10
            ws.column_dimensions[get_column_letter(i)].width = min(max(m + 2, 12), 45)

def title_block(ws, title, lines):
    ws["A1"] = title
    ws["A1"].font = TITLE_FONT
    for i, ln in enumerate(lines, 2):
        ws[f"A{i}"] = ln
        ws[f"A{i}"].alignment = WRAP
    ws.column_dimensions["A"].width = 150
    return len(lines) + 2

wb = Workbook()

# ============================ 1. README ============================
ws = wb.active
ws.title = "README"
title_block(ws, "Substance Abuse Study — Full Analysis Workbook (FUHSI, n=132)", [
    "Study: Assessment of Substance Abuse and Perceived Health Implications Among Undergraduate Students of FUHSI, Ila-Orangun (Afolabi Mufeedat Monisola, Nursing Science). Analysed n=132 consenting respondents.",
    "HOW TO USE: README → Data_Dictionary → Cleaned_Data (132 records + scores) → Obj1_SubstanceUse → Obj2_Factors → Obj3_Health → Obj4_Prevention → Bivariate → Correlations → Logistic_Models → Charts_Native (10 native Excel charts) → Key_Findings.",
    "METHODS (thesis §3.10 + documented extensions): descriptives with Wilson 95% CI; Chi-square (Fisher exact for 2×2 with expected<5); Spearman primary + Pearson sensitivity; Kruskal-Wallis/Mann-Whitney for scores; binary logistic regression (supplementary). Significance p<0.05. All supplementary analyses clearly labelled.",
    "SCORING: Substance use binary flags; Likert scales 1-5 (SA=5..SD=1); subscale means; problem use flag = any Yes on Q15 or Q16. Theory constructs mapped to Problem Behaviour Theory (peer, academic, emotional, availability, coping, family, media, boredom, policy) and Social Learning Theory (peer, media, family).",
    "RELIABILITY: Factors α=0.908 (excellent); Health α=0.937 (excellent); Prevention α=0.904 (excellent).",
    "LIMITATIONS: n=132 vs planned 395 (33.4%); convenience online sample vs planned stratified; effective MoE ±8.5% vs planned ±5%; cross-sectional; self-report; Faculty of Sciences/Clinical under-represented.",
])

# ============================ 2. Data Dictionary ============================
ws = wb.create_sheet("Data_Dictionary")
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

dd = [{"code": "ID", "meaning": "Anonymised respondent ID", "values": "1..132"}]
for n in ["Age", "Sex", "Level", "Faculty", "Religion", "Marital", "Living", "Allowance"]:
    dd.append({"code": n, "meaning": "Demographics (cleaned)", "values": "—"})
dd.append({"code": "Ever_use", "meaning": "Ever used any psychoactive substance", "values": "Yes/No"})
dd.append({"code": "Past_3mo", "meaning": "Used any substance in past 3 months", "values": "Yes/No"})
dd.append({"code": "Substances", "meaning": "Specific substances used (multi-select)", "values": "List"})
dd.append({"code": "Frequency", "meaning": "Frequency of most-used substance (past 30 days)", "values": "0-3 ordinal (0=Never/Not applicable/Not stated, 1=Less than once a week, 2=1–2x/week, 3=3–6x/week)"})
dd.append({"code": "Poly_use", "meaning": "Used >1 substance in past 3 months", "values": "Yes/No"})
dd.append({"code": "Should_reduce", "meaning": "Felt should reduce/stop use (CAGE-type)", "values": "Yes/No"})
dd.append({"code": "Withdrawal", "meaning": "Experienced withdrawal symptoms (CAGE-type)", "values": "Yes/No"})
dd.append({"code": "Problem_use", "meaning": "Any CAGE-type Yes", "values": "1=Yes/0=No"})
for i, t in enumerate(FACTOR_LABELS, 1):
    dd.append({"code": f"Factor_{i:02d}", "meaning": f"Factor: {t}", "values": "SA/A/U/D/SD (1-5)"})
dd += [{"code": "Factor_score", "meaning": "Mean of 13 factors", "values": "1-5"},
       {"code": "Factor_Peer_Social", "meaning": "Peer pressure + Parties + Low self-esteem", "values": "1-5"},
       {"code": "Factor_Academic", "meaning": "Academic stress", "values": "1-5"},
       {"code": "Factor_Emotional", "meaning": "Emotional distress + Coping", "values": "1-5"},
       {"code": "Factor_Availability", "meaning": "Easy availability", "values": "1-5"},
       {"code": "Factor_Family", "meaning": "Family member use + Limited monitoring", "values": "1-5"},
       {"code": "Factor_Social_Media", "meaning": "Social media exposure", "values": "1-5"},
       {"code": "Factor_Boredom", "meaning": "Boredom/unstructured time", "values": "1-5"},
       {"code": "Factor_Policy", "meaning": "Inadequate policy enforcement", "values": "1-5"}]
for i, t in enumerate(HEALTH_LABELS, 1):
    dd.append({"code": f"Health_{i:02d}", "meaning": f"Health implication: {t}", "values": "SA/A/U/D/SD (1-5)"})
dd += [{"code": "Health_score", "meaning": "Mean of 12 health items", "values": "1-5"},
       {"code": "Health_Physical", "meaning": "Physical domain (Q30,31,32,38,39)", "values": "1-5"},
       {"code": "Health_Psychological", "meaning": "Psychological domain (Q33,34,36)", "values": "1-5"},
       {"code": "Health_Social", "meaning": "Social domain (Q37,40)", "values": "1-5"},
       {"code": "Health_Academic", "meaning": "Academic domain (Q35,41)", "values": "1-5"}]
for i, t in enumerate(PREV_LABELS, 1):
    dd.append({"code": f"Prev_{i:02d}", "meaning": f"Prevention strategy: {t}", "values": "SA/A/U/D/SD (1-5)"})
dd.append({"code": "Prev_score", "meaning": "Mean of 8 prevention items", "values": "1-5"})
dd.append({"code": "Problem_use", "meaning": "CAGE-type flag (any Yes on Q15 or Q16)", "values": "1=Yes/0=No"})

write_df(ws, pd.DataFrame(dd), widths=[16, 95, 40])

# ============================ 3. Cleaned Data ============================
df = pd.read_csv("data/processed/substance_abuse_cleaned_full.csv", dtype=str, keep_default_na=False)
num_cols = [c for c in df.columns if c.startswith("factor_") or c.startswith("health_") or c.startswith("prev_") or c in ["freq_c", "problem_use", "any_substance_3mo", "ever_use_c", "past_3mo_c"] or c.endswith("_score")]
for c in num_cols:
    if c in df.columns:
        df[c] = pd.to_numeric(df[c], errors="coerce")

ws = wb.create_sheet("Cleaned_Data")
out = pd.DataFrame({"ID": range(1, len(df) + 1)})
out["Timestamp"] = df["Timestamp"]
out["Consent"] = df["1. Do you voluntarily agree to participate in this research study?"]
out["Age"] = df["age_c"]; out["Sex"] = df["sex_c"]; out["Level"] = df["level_c"]
out["Faculty"] = df["faculty_c"]; out["Religion"] = df["religion_c"]; out["Marital"] = df["marital_c"]
out["Living"] = df["living_c"]; out["Allowance"] = df["allowance_c"]
out["Ever_use"] = pd.to_numeric(df["ever_use_c"], errors="coerce").map({1: "Yes", 0: "No"})
out["Past_3mo"] = pd.to_numeric(df["past_3mo_c"], errors="coerce").map({1: "Yes", 0: "No"}).fillna("No")
out["Substances"] = df["substances_list"]
out["Primary_substance"] = df["primary_substance"]; out["Frequency"] = df["freq_c"]
out["Poly_use"] = df["poly_use_c"]; out["Should_reduce"] = df["should_reduce_c"]
out["Withdrawal"] = df["withdrawal_c"]; out["Problem_use"] = df["problem_use"]
for i in range(1, 14): out[f"Factor_{i:02d}"] = df[f"factor_{i:02d}"]
out["Factor_score"] = df["factor_score"]
for s in ["Peer_Social", "Academic", "Emotional", "Availability", "Family", "Social_Media", "Boredom", "Policy"]:
    out[f"Factor_{s}"] = df[f"factor_{s.lower()}"]
for i in range(1, 13): out[f"Health_{i:02d}"] = df[f"health_{i:02d}"]
out["Health_score"] = df["health_score"]
for d in ["Physical", "Psychological", "Social", "Academic"]:
    out[f"Health_{d}"] = df[f"health_{d.lower()}"]
for i in range(1, 9): out[f"Prev_{i:02d}"] = df[f"prev_{i:02d}"]
out["Prev_score"] = df["prev_score"]
out["Problem_use"] = df["problem_use"]
write_df(ws, out)

# ============================ Result tables ============================
def add_table_sheet(name, files, notes=None):
    ws = wb.create_sheet(name)
    row = 1
    if notes:
        for ln in notes:
            ws.cell(row=row, column=1, value=ln).font = SUB_FONT
            row += 1
        row += 1
    for f in files:
        p = TAB_DIR / f
        if not p.exists(): continue
        ws.cell(row=row, column=1, value=p.stem).font = SUB_FONT
        row += 1
        t = pd.read_csv(p)
        for r in dataframe_to_rows(t, index=False, header=True):
            ws.append(r)
        for c in range(1, len(t.columns) + 1):
            cell = ws.cell(row=row, column=c)
            cell.fill = HDR_FILL; cell.font = HDR_FONT
        row = ws.max_row + 2
    for i in range(1, ws.max_column + 1):
        ws.column_dimensions[get_column_letter(i)].width = min(
            max([len(str(ws.cell(r, i).value or "")) for r in range(1, min(ws.max_row + 1, 60))]) + 2, 42)

add_table_sheet("Obj1_SubstanceUse", 
    ["D02_ever_use.csv", "D02_past_3mo.csv", "D02_any_substance_3mo.csv", "D02_substance_specific.csv",
     "D02_frequency.csv", "D02_poly_use.csv", "D02_should_reduce.csv", "D02_withdrawal.csv", "D02_problem_use_flag.csv"],
    [     "OBJECTIVE 1 — Extent of substance use. Primary: any past-3mo use 9.8% (95% CI 5.8–16.1%). Problem use (CAGE-type) 6.1%.",
     "Alcohol is the most mentioned substance (16 mentions, 12.1% of respondents). Frequency of the 13 past-3mo users: less than once a week (4), 1–2x/week (3), 3–6x/week (2), not at all (3), not stated (1). Poly-use 3.0%."])

add_table_sheet("Obj2_Factors",
    ["D03_factors_descriptive.csv", "D03_factors_sa_a.csv", "D03_factor_subscales.csv"],
    ["OBJECTIVE 2 — Factors influencing substance abuse. Top: Peer pressure (99.2% SA/A), Academic stress (96.2%), Emotional distress (96.2%).",
     "Subscales map to Problem Behaviour Theory (peer, academic, emotional, availability, coping, family, media, boredom, policy) and Social Learning Theory (peer, media, family)."])

add_table_sheet("Obj3_Health",
    ["D04_health_descriptive.csv", "D04_health_sa_a.csv", "D04_health_domains.csv"],
    ["OBJECTIVE 3 — Perceived health implications. All items >90% SA+A. Highest: Dependence (99.2%), Organ damage (97.0%).",
     "Domains: Physical (mean 4.59), Psychological (4.53), Social (4.45), Academic (4.53)."])

add_table_sheet("Obj4_Prevention",
    ["D05_prevention_descriptive.csv", "D05_prevention_sa_a.csv"],
    ["OBJECTIVE 4 — Prevention strategies. Top: Counselling (97.0% SA/A), Education (96.2%), Early ID (95.5%).",
     "All strategies >90% SA+A, indicating strong perceived need for multi-component interventions."])

add_table_sheet("Bivariate",
    ["D07_bivariate_demographics.csv"],
    ["SUPPLEMENTARY — Chi-square/Fisher exact tests: Ever use, Past 3mo, Problem use, Any substance vs demographics.",
     "Detail row-% tables in DX_*.csv. Significant associations highlighted (p<0.05)."])

add_table_sheet("Correlations",
    ["D09_correlations.csv", "D09b_spearman_matrix.csv", "D09c_pearson_matrix.csv"],
    ["SUPPLEMENTARY — Spearman primary + Pearson sensitivity among factor/health/prevention subscales.",
     "Strongest: factor-emotional ↔ health-psychological (+0.78). All subscales positively correlated."])

add_table_sheet("Logistic_Models",
    ["D10_logistic_models.csv"],
    ["SUPPLEMENTARY — Binary logistic regression (adjusted). Models: Ever use, Past 3mo, Problem use, Any substance.",
     "Sparse categories merged; results interpreted with caution due to small n/events."])

# ============================ Charts_Native (10 native Excel charts) ============================
ws = wb.create_sheet("Charts_Native")
ws.column_dimensions["A"].width = 34; ws.column_dimensions["B"].width = 16; ws.column_dimensions["C"].width = 4

def add_chart_block(ws, row, title, cats, vals, chart):
    ws.cell(row=row, column=1, value=title).font = SUB_FONT
    ws.cell(row=row+1, column=1, value="Category").font = HDR_FONT
    ws.cell(row=row+1, column=2, value="Value").font = HDR_FONT
    for i, (c, v) in enumerate(zip(cats, vals)):
        ws.cell(row=row+2+i, column=1, value=c)
        ws.cell(row=row+2+i, column=2, value=round(float(v), 1))
    n = len(cats)
    data = Reference(ws, min_col=2, min_row=row+1, max_row=row+1+n)
    labs = Reference(ws, min_col=1, min_row=row+2, max_row=row+1+n)
    chart.add_data(data, titles_from_data=True)
    chart.set_categories(labs)
    chart.height = 7.5; chart.width = 14
    ws.add_chart(chart, f"D{row}")
    return max(n + 4, 22)

row = 1
# C1 - Ever use
c1 = DoughnutChart(); c1.title = "Ever used substance"; c1.style = 10
eu = pd.to_numeric(df["ever_use_c"], errors="coerce").map({1: "Yes", 0: "No"}).value_counts()
row += add_chart_block(ws, row, "C1 — Ever use (counts)", list(eu.index), list(eu.values), c1)

# C2 - Past 3mo
c2 = PieChart(); c2.title = "Used in past 3 months"; c2.style = 10
p3 = pd.to_numeric(df["past_3mo_c"], errors="coerce").map({1: "Yes", 0: "No"}).fillna("No").value_counts()
row += add_chart_block(ws, row, "C2 — Past 3 months (counts)", list(p3.index), list(p3.values), c2)

# C3 - Any substance 3mo
c3 = PieChart(); c3.title = "Any substance (past 3mo)"; c3.style = 10
any3 = df["any_substance_3mo"].map({1: "Yes", 0: "No"}).value_counts()
row += add_chart_block(ws, row, "C3 — Any substance past 3mo (counts)", list(any3.index), list(any3.values), c3)

# C4 - Problem use
c4 = DoughnutChart(); c4.title = "Problem use (CAGE-type)"; c4.style = 10
pu = df["problem_use"].map({1: "Yes", 0: "No"}).value_counts()
row += add_chart_block(ws, row, "C4 — Problem use (counts)", list(pu.index), list(pu.values), c4)

# C5 - Substances
import ast
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

sub_counts = Counter()
for lst in df["substances_list"]:
    for s in parse_subs(lst): sub_counts[s] += 1
c5 = BarChart(); c5.type = "bar"; c5.title = "Substances (past 3mo, %)"; c5.style = 10
items = list(sub_counts.keys()); vals = [sub_counts[s]/132*100 for s in items]
row += add_chart_block(ws, row, "C5 — Substances used past 3mo (% of n=132)", items, vals, c5)

# C6 - Factors SA+A %
FACTOR_LABELS = ["Peer pressure", "Academic stress", "Curiosity/experimentation",
    "Easy availability", "Family member use", "Social media exposure",
    "Emotional distress", "Coping with pain/stress/sleep",
    "Social gatherings/parties", "Low self-esteem",
    "Limited parental monitoring", "Boredom/unstructured time",
    "Inadequate policy enforcement"]

sa_a_pct = []
for i, col in enumerate([f"factor_{i+1:02d}" for i in range(13)]):
    s_num = pd.to_numeric(df[col], errors="coerce")
    total = s_num.notna().sum()
    sa_a = int((s_num == 5).sum() + (s_num == 4).sum())
    sa_a_pct.append(round(sa_a / total * 100, 1) if total else 0)

c6 = BarChart(); c6.type = "bar"; c6.title = "Factors % SA+A"; c6.style = 10
row += add_chart_block(ws, row, "C6 — Factors % SA+A", FACTOR_LABELS, sa_a_pct, c6)

# C7 - Health SA+A %
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

c7 = BarChart(); c7.type = "bar"; c7.title = "Health items % SA+A"; c7.style = 10
row += add_chart_block(ws, row, "C7 — Health implications % SA+A", HEALTH_LABELS, sa_a_pct_h, c7)

# C8 - Prevention SA+A %
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

c8 = BarChart(); c8.type = "bar"; c8.title = "Prevention % SA+A"; c8.style = 10
row += add_chart_block(ws, row, "C8 — Prevention strategies % SA+A", PREV_LABELS, sa_a_pct_p, c8)

# C9 - Any substance by sex
c9 = BarChart(); c9.type = "col"; c9.title = "Any substance by sex"; c9.style = 10
rate = df.groupby("sex_c")["any_substance_3mo"].mean() * 100
row += add_chart_block(ws, row, "C9 — Any substance (3mo) by sex (%)", list(rate.index), list(rate.values), c9)

# C10 - Any substance by faculty
c10 = BarChart(); c10.type = "col"; c10.title = "Any substance by faculty"; c10.style = 10
rate = df.groupby("faculty_c")["any_substance_3mo"].mean() * 100
row += add_chart_block(ws, row, "C10 — Any substance (3mo) by faculty (%)", list(rate.index), list(rate.values), c10)

# ============================ Key_Findings ============================
ws = wb.create_sheet("Key_Findings")
title_block(ws, "Key findings by objective (n=132)", [
    "O1 PREVALENCE — 9.8% past-3mo use (95% CI 5.8–16.1%); H₀ (≤50%) rejected (p<0.001). Alcohol most mentioned (16 mentions, 12.1% of respondents). Problem use (CAGE-type) 6.1%. Burden low but non-zero; frequency among the 13 users: less than once a week (4), 1–2x/week (3), 3–6x/week (2), not at all (3), not stated (1).",
    "O2 FACTORS — All 13 factors high (3.89–4.67/5). Top: Peer pressure (97.7% SA+A), Emotional distress (93.2%), Coping (93.2%), Parental monitoring (93.2%). Theory mapping: PBT constructs (peer, academic, emotional, availability, coping, family, media, boredom, policy) and SLT constructs (peer, media, family) all elevated.",
    "O3 HEALTH — All 12 items ≥95.5% SA+A. Top: Dependence (100%), Organ damage (100%), Cardiovascular/Respiratory/Concentration/Accidents (99.2%). Domains: Physical 4.59, Academic 4.53, Psychological 4.51, Social 4.45. Overall health mean 4.54/5.",
    "O4 PREVENTION — Top: Counselling (97.7%), Education (97.7%), Parental involvement (96.2%), Policies (95.5%). Mean prevention 4.36/5.",
    "SUPPLEMENTARY FINDINGS — Ever use linked to Sex (V=0.35), Faculty (V=0.31), Allowance (V=0.32), Level (V=0.26); logistic M1: Male aOR=10.1 (p=0.001), Science faculty aOR=8.3 (p=0.006), low allowance protective aOR=0.06 (p=0.007). Within-scale subscales strongly correlated (ρ 0.66–0.95); cross-scale modest (factor↔health ρ=0.27, factor↔prevention ρ=0.30, health↔prevention ρ=0.53).",
    "RECOMMENDATIONS — (1) Peer-led education + positive norm campaigns (Social Learning Theory). (2) Counselling + stress management for emotional/academic drivers. (3) Early screening + referral pathways. (4) Faculty-targeted outreach for Science/Clinical. (5) Bridge awareness-behaviour gap: high perceived risk but low actual use.",
    "CAVEATS — n=132 vs planned 395 (33.4%); convenience online sample; cross-sectional; self-report; small event counts limit logistic reliability; Faculty of Sciences/Clinical under-represented.",
])

wb.save("reports/output/Substance_Abuse_Full_Analysis.xlsx")
print("Saved workbook:", "reports/output/Substance_Abuse_Full_Analysis.xlsx")
print("DONE STEP 4")