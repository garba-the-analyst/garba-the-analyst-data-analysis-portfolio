"""Malaria Prevention KAP Study — Phase 4: Excel Workbook."""
import warnings
import os
from pathlib import Path
import numpy as np
import pandas as pd
import openpyxl as xl
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter
from openpyxl.utils.dataframe import dataframe_to_rows
from openpyxl.chart import BarChart, PieChart, DoughnutChart, Reference

warnings.filterwarnings("ignore")

BASE = Path("/home/garba-the-analyst/Desktop/Projects/Data analysis ")
os.chdir(BASE)

CLEAN = BASE / "data" / "processed" / "malaria_kap_cleaned.csv"
TAB_DIR = BASE / "reports" / "output" / "tables"
OUT_XLSX = BASE / "reports" / "output" / "Malaria_KAP_Analysis.xlsx"

TITLE_FONT = Font(bold=True, size=14, color="1F4E79")
HDR_FONT = Font(bold=True, color="FFFFFF")
SUB_FONT = Font(bold=True, size=11, color="1F4E79")
NOTE_FONT = Font(italic=True, size=9, color="555555")
HDR_FILL = PatternFill("solid", fgColor="1F4E79")
ALT_FILL = PatternFill("solid", fgColor="DDEBF7")

def rd(name):
    d = pd.read_csv(TAB_DIR / name, keep_default_na=False)
    for c in d.columns:
        if d[c].dtype == object and len(d) and d[c].str.fullmatch(r"-?\d+(\.\d+)?").all():
            d[c] = pd.to_numeric(d[c])
    return d

df = pd.read_csv(CLEAN, dtype=str, keep_default_na=False)
for c in ["know_score", "know_pct", "prac_score", "mis_score", "gap_score",
          "level_num", "age_ord"] + [f"K{i+1}" for i in range(10)] + \
           [f"P{i+1}" for i in range(8)] + [f"M{i+1}" for i in range(8)]:
    if c in df.columns:
        df[c] = pd.to_numeric(df[c], errors="coerce")
N = len(df)

def sheet_df(wb, name, d, widths=None, note=None, freeze="A2"):
    ws = wb.create_sheet(name)
    for r, row in enumerate(dataframe_to_rows(d, index=False), 1):
        for c, v in enumerate(row, 1):
            ws.cell(row=r, column=c, value=v)
    for c in range(1, d.shape[1] + 1):
        cell = ws.cell(row=1, column=c)
        cell.font = HDR_FONT
        cell.fill = HDR_FILL
        cell.alignment = Alignment(wrap_text=True, vertical="center")
    for w, col in enumerate(d.columns, 1):
        letter = get_column_letter(w)
        if widths and col in widths:
            ws.column_dimensions[letter].width = widths[col]
        else:
            ws.column_dimensions[letter].width = min(max(12, int(d[col].astype(str).str.len().max() if len(d) else 12) + 2), 60)
    ws.freeze_panes = freeze
    if note:
        ws.cell(row=d.shape[0] + 3, column=1, value=note).font = NOTE_FONT
    return ws

def add_chart_block(ws, row, title, cats, vals, chart):
    ws.cell(row=row, column=1, value=title).font = SUB_FONT
    ws.cell(row=row + 1, column=1, value="Category").font = HDR_FONT
    ws.cell(row=row + 1, column=2, value="Value").font = HDR_FONT
    ws.cell(row=row + 1, column=1).fill = HDR_FILL
    ws.cell(row=row + 1, column=2).fill = HDR_FILL
    for i, (c, v) in enumerate(zip(cats, vals)):
        ws.cell(row=row + 2 + i, column=1, value=str(c))
        ws.cell(row=row + 2 + i, column=2, value=round(float(v), 1))
    n = len(cats)
    data = Reference(ws, min_col=2, min_row=row + 1, max_row=row + 1 + n)
    labs = Reference(ws, min_col=1, min_row=row + 2, max_row=row + 1 + n)
    chart.add_data(data, titles_from_data=True)
    chart.set_categories(labs)
    chart.height = 7.5
    chart.width = 14
    ws.add_chart(chart, f"D{row}")
    return max(n + 4, 22)

wb = Workbook()
wb.remove(wb.active)

# ============================ README ============================
ws = wb.create_sheet("README")
readme = [
    ("Malaria Prevention KAP Study — FUHSI", "title"),
    ("Client: Yusuf Khadijat Opeyemi, Department of Nursing Science", "bold"),
    (f"Sample: {N} consenting undergraduate students", "bold"),
    ("", ""),
    ("ANALYSIS PER THESIS DOCUMENT (§3.10 + Orem's Self-Care Theory)", "sub"),
    ("README → Data_Dictionary → Cleaned_Data → Demographics → Knowledge → Practice → Misconceptions → Hypotheses → Training_Barriers → Supplementary → Charts_Native (10) → Key_Findings.", ""),
    ("", ""),
    ("Primary analyses (document-mandated §3.10)", "sub"),
    ("Descriptive: frequencies/percentages, mean/SD for all items and scores.", ""),
    ("H1: Chi-square (knowledge vs practice categories) + Pearson/Spearman (continuous).", ""),
    ("H2: Kruskal-Wallis (knowledge/practice across levels) + pairwise Mann-Whitney.", ""),
    ("Supplementary (labelled): Misconceptions, Gap analysis, Logistic regressions.", ""),
    ("", ""),
    ("DISCLOSED DEVIATIONS", "sub"),
    ("1. Fixed + median categorisations for both knowledge and practice (doc doesn't specify).", ""),
    ("2. Misconceptions scored separately (reverse-coded) — not merged with knowledge.", ""),
    ("3. Department grouped into faculties via col 43 mapping + department cleaning.", ""),
    ("4. ITN ownership treated as both practice item and separate outcome.", ""),
]
r = 1
for txt, kind in readme:
    cell = ws.cell(row=r, column=1, value=txt)
    if kind == "title": cell.font = TITLE_FONT
    elif kind in ("bold", "sub"): cell.font = SUB_FONT
    cell.alignment = Alignment(wrap_text=True, vertical="top")
    r += 1
ws.column_dimensions["A"].width = 150

# ============================ Data_Dictionary ============================
DICT = [
    ("age_band / age_ord", "Demographics", "Age band + ordinal (1=16-20, 2=21-25, 3=26-30)"),
    ("gender_c", "Demographics", "Gender (Male/Female)"),
    ("dept_c / faculty_grp", "Demographics", "Department cleaned + faculty group (Allied Health/Basic Medical/Clinical/Other)"),
    ("level_c / level_num", "Demographics", "Academic level (categorical / numeric 1-4)"),
    ("residence_c", "Demographics", "Residence type (3 categories)"),
    ("K1..K10 (+_raw)", "Knowledge", "10 MCQ items (0=incorrect, 1=correct); keys in labels JSON"),
    ("know_score / know_pct", "Derived", "Knowledge total 0-10 and percentage"),
    ("know_cat_fixed / know_cat_median", "Derived", "Good/Moderate/Poor (fixed ≥8/5-7/<5) and Good/Poor (median split)"),
    ("P1..P8 (+_raw)", "Practice", "8 frequency items (Always=5..Never=1); raw text preserved"),
    ("prac_score", "Derived", "Practice total 8-40"),
    ("prac_cat_fixed / prac_cat_median", "Derived", "Good/Moderate/Poor (fixed ≥30/18-29/<18) and median split"),
    ("M1..M8 (+_raw)", "Misconceptions", "8 agreement items reverse-coded (SD=5..SA=1); higher=fewer misconceptions"),
    ("mis_score", "Derived", "Misconception total 8-40"),
    ("training_c / source_c / diagnosed_c / itn_own_c / access_c", "Training/Experience", "Training yes/no, source, malaria diagnosis, ITN ownership, access rating"),
    ("comfort_c / treat24_c / sanit_c / talk_c", "Barriers/Intent", "Comfort, 24h treatment, sanitation willingness, health talk attendance"),
    ("know_z / prac_z / gap_score", "Derived", "Z-scores and Practice-Knowledge gap (positive = practice > knowledge)"),
]
sheet_df(wb, "Data_Dictionary", pd.DataFrame(DICT, columns=["column(s)", "section", "description"]),
         widths={"column(s)": 40, "section": 15, "description": 110})

# ============================ Cleaned_Data ============================
sheet_df(wb, "Cleaned_Data", df, widths={"Timestamp": 24}, note=f"{N} consenting respondents.")

# ============================ Demographics ============================
t01 = rd("T01_demographics.csv")
sheet_df(wb, "Demographics", t01, note="Table 1: Sample demographics")

# ============================ Knowledge ============================
ws = wb.create_sheet("Knowledge")
ws.cell(row=1, column=1, value="TABLE 2 — Knowledge of Malaria Prevention").font = TITLE_FONT
r = 3
for f, ttl in [("T02_knowledge_items.csv", "Item-level Results"),
               ("T02b_knowledge_summary.csv", "Score Summary & Categorisation (Fixed + Median)")]:
    t = rd(f)
    ws.cell(row=r, column=1, value=ttl).font = SUB_FONT
    for rr, row in enumerate(dataframe_to_rows(t, index=False), r + 1):
        for c, v in enumerate(row, 1):
            ws.cell(row=rr, column=c, value=v)
    r += t.shape[0] + 3
for c in range(1, 10): ws.column_dimensions[get_column_letter(c)].width = 28

# ============================ Practice ============================
ws = wb.create_sheet("Practice")
ws.cell(row=1, column=1, value="TABLE 3 — Practice of Malaria Prevention").font = TITLE_FONT
r = 3
for f, ttl in [("T03_practice_items.csv", "Item-level Frequency"),
               ("T03b_practice_summary.csv", "Score Summary & Categorisation (Fixed + Median)")]:
    t = rd(f)
    ws.cell(row=r, column=1, value=ttl).font = SUB_FONT
    for rr, row in enumerate(dataframe_to_rows(t, index=False), r + 1):
        for c, v in enumerate(row, 1):
            ws.cell(row=rr, column=c, value=v)
    r += t.shape[0] + 3
for c in range(1, 14): ws.column_dimensions[get_column_letter(c)].width = 30

# ============================ Misconceptions ============================
ws = wb.create_sheet("Misconceptions")
ws.cell(row=1, column=1, value="TABLE 4 — Misconceptions about Malaria (Reverse-scored)").font = TITLE_FONT
r = 3
for f, ttl in [("T04_misconceptions.csv", "Item-level Agreement"),
               ("T04b_misconceptions_summary.csv", "Score Summary")]:
    t = rd(f)
    ws.cell(row=r, column=1, value=ttl).font = SUB_FONT
    for rr, row in enumerate(dataframe_to_rows(t, index=False), r + 1):
        for c, v in enumerate(row, 1):
            ws.cell(row=rr, column=c, value=v)
    r += t.shape[0] + 3
for c in range(1, 14): ws.column_dimensions[get_column_letter(c)].width = 30

# ============================ Hypotheses ============================
ws = wb.create_sheet("Hypotheses")
ws.cell(row=1, column=1, value="TABLE 5 — Hypothesis Tests").font = TITLE_FONT
r = 3
for f, ttl in [("T07_hypothesis1_chi2.csv", "H1: Knowledge vs Practice (Chi-square)"),
               ("T07b_correlation_continuous.csv", "H1: Continuous Correlation (Spearman + Pearson)"),
               ("T08_kruskal_level.csv", "H2: Knowledge/Practice by Level (Kruskal-Wallis + MW)"),
               ("T08b_kruskal_faculty.csv", "H2: Knowledge/Practice by Faculty (Kruskal-Wallis)"),
               ("T08c_category_demographics.csv", "Categories x Demographics (Chi-square)"),
               ("T07b_correlation_continuous.csv", "Correlation: Knowledge vs Practice (Continuous)")]:
    t = rd(f)
    ws.cell(row=r, column=1, value=ttl).font = SUB_FONT
    for rr, row in enumerate(dataframe_to_rows(t, index=False), r + 1):
        for c, v in enumerate(row, 1):
            ws.cell(row=rr, column=c, value=v)
    r += t.shape[0] + 3
for c in range(1, 12): ws.column_dimensions[get_column_letter(c)].width = 30

# ============================ Training_Barriers ============================
ws = wb.create_sheet("Training_Barriers")
ws.cell(row=1, column=1, value="TABLE 6 — Training, ITN, Access, Barriers & Intent").font = TITLE_FONT
r = 3
for f, ttl in [("T05_training_experience.csv", "Training, Source, Diagnosis, ITN, Access"),
               ("T05b_itn_ownership_by_level.csv", "ITN Ownership by Level"),
               ("T05b_access_rating_by_level.csv", "Access Rating by Level"),
               ("T06_barriers_intent.csv", "Barriers & Future Intent")]:
    t = rd(f)
    ws.cell(row=r, column=1, value=ttl).font = SUB_FONT
    for rr, row in enumerate(dataframe_to_rows(t, index=False), r + 1):
        for c, v in enumerate(row, 1):
            ws.cell(row=rr, column=c, value=v)
    r += t.shape[0] + 3
for c in range(1, 8): ws.column_dimensions[get_column_letter(c)].width = 40

# ============================ Supplementary ============================
ws = wb.create_sheet("Supplementary")
ws.cell(row=1, column=1, value="SUPPLEMENTARY ANALYSES (Labelled — Beyond §3.10)").font = TITLE_FONT
r = 3
for f, ttl in [("T08_kruskal_level.csv", "S01: Kruskal-Wallis + MW (Level)"),
               ("T08b_kruskal_faculty.csv", "S02: Kruskal-Wallis (Faculty)"),
               ("T08c_category_demographics.csv", "S03: Categories x Demographics"),
               ("T11_gap_by_level.csv", "S04: Gap Score by Level"),
               ("T12_mis_by_level.csv", "S05: Misconceptions by Level"),
               ("T10_logistic_itn.csv", "S06: Logistic Regr. - ITN Ownership"),
               ("T13_logistic_practice.csv", "S07: Logistic Regr. - Practice Good")]:
    p = TAB_DIR / f
    if p.exists():
        t = rd(f)
        ws.cell(row=r, column=1, value=ttl).font = SUB_FONT
        for rr, row in enumerate(dataframe_to_rows(t, index=False), r + 1):
            for c, v in enumerate(row, 1):
                ws.cell(row=rr, column=c, value=v)
        r += t.shape[0] + 3
for c in range(1, 10): ws.column_dimensions[get_column_letter(c)].width = 30

# ============================ Charts_Native (10 charts) ============================
ws = wb.create_sheet("Charts_Native")
ws.column_dimensions["A"].width = 34; ws.column_dimensions["B"].width = 16; ws.column_dimensions["C"].width = 4

def add_chart_block(row, title, cats, vals, chart):
    ws.cell(row=row, column=1, value=title).font = SUB_FONT
    ws.cell(row=row + 1, column=1, value="Category").font = HDR_FONT
    ws.cell(row=row + 1, column=2, value="Value").font = HDR_FONT
    ws.cell(row=row + 1, column=1).fill = HDR_FILL
    ws.cell(row=row + 1, column=2).fill = HDR_FILL
    for i, (c, v) in enumerate(zip(cats, vals)):
        ws.cell(row=row + 2 + i, column=1, value=str(c))
        ws.cell(row=row + 2 + i, column=2, value=round(float(v), 1))
    n = len(cats)
    data = Reference(ws, min_col=2, min_row=row + 1, max_row=row + 1 + n)
    labs = Reference(ws, min_col=1, min_row=row + 2, max_row=row + 1 + n)
    chart.add_data(data, titles_from_data=True)
    chart.set_categories(labs)
    chart.height = 7.5
    chart.width = 14
    ws.add_chart(chart, f"D{row}")
    return max(n + 4, 22)

row = 1
c1 = DoughnutChart(); c1.title = "Gender Distribution"; c1.style = 10
sex = df["gender_c"].value_counts()
row += add_chart_block(row, "C1 — Gender", sex.index.tolist(), sex.values.tolist(), c1)

c2 = PieChart(); c2.title = "Academic Level"; c2.style = 10
lev = df["level_c"].value_counts().reindex(["100 Level", "200 Level", "300 Level", "400 Level"])
row += add_chart_block(row, "C2 — Academic Level", lev.index.tolist(), lev.values.tolist(), c2)

c3 = DoughnutChart(); c3.title = "ITN Ownership"; c3.style = 10
itn = df["itn_own_c"].value_counts()
row += add_chart_block(row, "C3 — ITN Ownership", itn.index.tolist(), itn.values.tolist(), c3)

c4 = PieChart(); c4.title = "Knowledge Category (Fixed)"; c4.style = 10
kc = df["know_cat_fixed"].value_counts()
row += add_chart_block(row, "C4 — Knowledge Category", kc.index.tolist(), kc.values.tolist(), c4)

c5 = BarChart(); c5.type = "bar"; c5.title = "Knowledge Items % Correct"; c5.style = 10
t02 = rd("T02_knowledge_items.csv")
row += add_chart_block(row, "C5 — Knowledge Items (% Correct)", t02["item"].tolist(),
                       t02["correct_pct"].tolist(), c5)

c6 = BarChart(); c6.type = "bar"; c6.title = "Practice Item Means (1-5)"; c6.style = 10
t03 = rd("T03_practice_items.csv")
row += add_chart_block(row, "C6 — Practice Item Means", t03["item"].tolist(),
                       t03["mean_1to5"].tolist(), c6)

c7 = BarChart(); c7.type = "col"; c7.title = "Misconception Item Means (1-5, rev)"; c7.style = 10
t04 = rd("T04_misconceptions.csv")
row += add_chart_block(row, "C7 — Misconception Item Means", t04["item"].tolist(),
                       t04["mean_1to5"].tolist(), c7)

c8 = BarChart(); c8.type = "bar"; c8.title = "Knowledge by Academic Level (Mean)"; c8.style = 10
lvl_know = rd("T08_kruskal_level.csv")
# Get descriptive means by level
lvl_means = df.groupby("level_c")["know_score"].mean().reindex(["100 Level", "200 Level", "300 Level", "400 Level"])
row += add_chart_block(row, "C8 — Knowledge Mean by Level", lvl_means.index.tolist(),
                       lvl_means.values.tolist(), c8)

c9 = BarChart(); c9.type = "bar"; c9.title = "Practice by Academic Level (Mean)"; c9.style = 10
lvl_means = df.groupby("level_c")["prac_score"].mean().reindex(["100 Level", "200 Level", "300 Level", "400 Level"])
row += add_chart_block(row, "C9 — Practice Mean by Level", lvl_means.index.tolist(),
                       lvl_means.values.tolist(), c9)

c10 = BarChart(); c10.type = "bar"; c10.title = "ITN Ownership by Level"; c10.style = 10
itn_lev = df.groupby("level_c")["itn_own_c"].apply(lambda x: (x=="Yes").mean()*100).reindex(["100 Level", "200 Level", "300 Level", "400 Level"])
row += add_chart_block(row, "C10 — ITN Ownership % by Level", itn_lev.index.tolist(),
                       itn_lev.values.tolist(), c10)

# ============================ Key_Findings ============================
ws = wb.create_sheet("Key_Findings")
t07 = rd("T07_hypothesis1_chi2.csv")
h1_fixed = t07[t07["test"] == "H1 Primary"].iloc[0]
t07c = rd("T07b_correlation_continuous.csv")
h1_spearman = t07c[t07c["test"] == "Spearman"].iloc[0]
h1_pearson = t07c[t07c["test"] == "Pearson"].iloc[0]
t08 = rd("T08_kruskal_level.csv")
k_level = t08[t08["variable"] == "Knowledge"].iloc[0]
p_level = t08[t08["variable"] == "Practice"].iloc[0]

# Convert to float
h1_chi2 = float(h1_fixed['chi2'])
h1_dof = int(h1_fixed['dof'])
h1_pval = float(h1_fixed['p'])
h1_v = float(h1_fixed['cramers_v'])
h1_spearman_r = float(h1_spearman['r'])
h1_spearman_p = float(h1_spearman['p'])
h1_pearson_r = float(h1_pearson['r'])
h1_pearson_p = float(h1_pearson['p'])
k_H = float(k_level['H'])
k_p = float(k_level['p'])
p_H = float(p_level['H'])
p_p = float(p_level['p'])

t01 = rd("T01_demographics.csv")
t02 = rd("T02_knowledge_items.csv")
t03 = rd("T03_practice_items.csv")
t04 = rd("T04_misconceptions.csv")
t05 = rd("T05_training_experience.csv")
bar_df = pd.read_csv(TAB_DIR / "T04_misconceptions.csv").nsmallest(1, "mean_1to5")

good_fixed = int((df['know_cat_fixed']=='Good (≥8)').sum())
mod_fixed = int((df['know_cat_fixed']=='Moderate (5-7)').sum())
poor_fixed = int((df['know_cat_fixed']=='Poor (<5)').sum())
prac_good_fixed = int((df['prac_cat_fixed']=='Good (≥30)').sum())
prac_mod_fixed = int((df['prac_cat_fixed']=='Moderate (18-29)').sum())
prac_poor_fixed = int((df['prac_cat_fixed']=='Poor (<18)').sum())

kf = [
    ("KEY FINDINGS — MALARIA PREVENTION KAP (FUHSI)", "title"),
    (f"Sample: N = {N} consenting undergraduates (100% consent rate)", "bold"),
    ("", ""),
    ("OBJECTIVE 1 — Knowledge Level", "sub"),
    (f"• Mean knowledge: {df['know_score'].mean():.2f}/10 (SD {df['know_score'].std():.2f}); Median 9.0.", ""),
    (f"• Categorisation (Fixed ≥8): Good {good_fixed} ({good_fixed/N*100:.1f}%), Moderate {mod_fixed}, Poor {poor_fixed}.", ""),
    (f"• Weakest items: {t02.nsmallest(3, 'correct_pct').iloc[0]['item']} ({t02.nsmallest(3, 'correct_pct').iloc[0]['correct_pct']}%), {t02.nsmallest(3, 'correct_pct').iloc[1]['item']} ({t02.nsmallest(3, 'correct_pct').iloc[1]['correct_pct']}%), {t02.nsmallest(3, 'correct_pct').iloc[2]['item']} ({t02.nsmallest(3, 'correct_pct').iloc[2]['correct_pct']}%).", ""),
    ("", ""),
    ("OBJECTIVE 2 — Practice Level", "sub"),
    (f"• Mean practice: {df['prac_score'].mean():.2f}/40 (SD {df['prac_score'].std():.2f}); Median 29.0.", ""),
    (f"• Categorisation (Fixed ≥30): Good {prac_good_fixed} ({prac_good_fixed/N*100:.1f}%), Moderate {prac_mod_fixed}, Poor {prac_poor_fixed}.", ""),
    (f"• Most consistent: 'Screen/close windows' (Always 63.2%); Least: 'ITN every night' (Always 5.3%).", ""),
    ("", ""),
    ("OBJECTIVE 3 — Knowledge ↔ Practice (H1)", "sub"),
    (f"• Chi-square (Fixed): χ²={h1_chi2}, df={h1_dof}, p={h1_pval:.4f}, V={h1_v} — significant.", ""),
    (f"• Spearman ρ = {h1_spearman_r} (p={h1_spearman_p:.4f}); Pearson r = {h1_pearson_r} (p={h1_pearson_p:.4f}) — moderate positive.", ""),
    ("→ H0 REJECTED: Knowledge significantly associated with practice.", ""),
    ("", ""),
    ("OBJECTIVE 3 — Practice by Level/Dept (H2)", "sub"),
    (f"• Knowledge by level: Kruskal-Wallis H={k_H}, p={k_p:.4f} — significant.", ""),
    (f"• Practice by level: Kruskal-Wallis H={p_H}, p={p_p:.4f} — {'significant' if p_p<0.05 else 'not significant'}.", ""),
    ("• Pairwise MW (Bonferroni): 100L vs 300L/400L significant for knowledge; 100L vs 400L significant for practice.", ""),
    ("→ H0 REJECTED for knowledge; " + ("REJECTED" if p_p<0.05 else "RETAINED") + " for practice.", ""),
    ("", ""),
    ("OBJECTIVE 4 — Information Sources", "sub"),
    ("• Primary sources: School/Course (55.4%), Health worker (28.7%), Media (11.2%), Family/Friends (3.7%).", ""),
    ("", ""),
    ("OBJECTIVE 5 — Misconceptions & ITN", "sub"),
    (f"• Misconception score: mean {df['mis_score'].mean():.2f}/40 (SD {df['mis_score'].std():.2f}); higher = fewer misconceptions.", ""),
    ("• ITN ownership: 161/321 (50.2%); Access: Easy/Very Easy 59.2%, Difficult/Very Difficult 17.1%.", ""),
    (f"• Top misconception (highest agreement): {t04.nsmallest(1, 'mean_1to5').iloc[0]['item']} (mean {t04.nsmallest(1, 'mean_1to5').iloc[0]['mean_1to5']:.2f}/5).", ""),
    ("", ""),
    ("SUPPLEMENTARY", "sub"),
    (f"• Logistic (Practice Good ~ Knowledge + Level + Gender + Misconceptions): see Hypotheses sheet for fitted ORs.", ""),
    ("• Gap score (Practice_z - Knowledge_z) is positive at 100L (0.32) and lowest at 200L (-0.63); see Supplementary S04.", ""),
    ("• Misconception differences by level are significant but non-monotonic: 100L highest (35.4), 200L lowest (33.7).", ""),
]
r = 1
for txt, kind in kf:
    cell = ws.cell(row=r, column=1, value=txt)
    if kind == "title": cell.font = TITLE_FONT
    elif kind in ("bold", "sub"): cell.font = SUB_FONT
    cell.alignment = Alignment(wrap_text=True, vertical="top")
    ws.row_dimensions[r].height = 30 if kind != "title" else 22
    r += 1
ws.column_dimensions["A"].width = 140

# Tab colors & order
for nm, col in [("README", "1F4E79"), ("Data_Dictionary", "808080"), ("Cleaned_Data", "808080"),
                ("Demographics", "2E75B6"), ("Knowledge", "2E75B6"), ("Practice", "2E75B6"),
                ("Misconceptions", "2E75B6"), ("Hypotheses", "C00000"), ("Training_Barriers", "C00000"),
                ("Supplementary", "808080"), ("Charts_Native", "548235"), ("Key_Findings", "548235")]:
    if nm in wb.sheetnames:
        wb[nm].sheet_properties.tabColor = col

order = ["README", "Data_Dictionary", "Cleaned_Data", "Demographics", "Knowledge",
         "Practice", "Misconceptions", "Hypotheses", "Training_Barriers", "Supplementary",
         "Charts_Native", "Key_Findings"]
wb._sheets = [wb[n] for n in order]
wb.save(OUT_XLSX)
print("Saved workbook:", OUT_XLSX.name, "| sheets:", wb.sheetnames)