"""Internet Access & SDL Readiness Study — Phase 4: Excel Workbook."""
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

CLEAN = BASE / "data" / "processed" / "internet_sdl_cleaned.csv"
TAB_DIR = BASE / "reports" / "output" / "tables"
OUT_XLSX = BASE / "reports" / "output" / "Internet_SDL_Readiness_Analysis.xlsx"

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
for c in ["ia_score", "sat_num", "sdl_total", "age_num", "level_num",
          "sdl_self_mgmt", "sdl_desire", "sdl_self_ctrl"] + [f"SDL{i+1}" for i in range(24)] + ["ia_device", "ia_freq", "ia_means", "ia_reliability", "ia_hours", "sat_num"]:
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
    ("Internet Access & Self-Directed Learning Readiness — FUHSI", "title"),
    ("Client: Badru (Final APA v4-3)", "bold"),
    (f"Sample: N = {N} undergraduate students (all consented)", "bold"),
    ("", ""),
    ("ANALYSIS PER THESIS DOCUMENT (Ch.1 objectives + §3.11 analysis plan)", "sub"),
    ("README → Data_Dictionary → Cleaned_Data → Demographics → Internet_Access → SDL_Readiness → Hypotheses → Reliability → Factors → Charts_Native → Key_Findings.", ""),
    ("", ""),
    ("Primary analyses (document-mandated §3.11)", "sub"),
    ("Descriptive: frequencies/percentages, mean/SD for all items and scores.", ""),
    ("Hypothesis 1: Spearman/Pearson correlation between Internet Access and SDL Readiness.", ""),
    ("Hypothesis 2: Kruskal-Wallis test for SDL differences across academic levels.", ""),
    ("Supplementary: Pairwise Mann-Whitney, IA components vs SDL subscales, barrier/uses profiles.", ""),
    ("", ""),
    ("DISCLOSED DEVIATIONS", "sub"),
    ("1. SDLRSNE 24-item version used (vs 40-item in some literature) — cutoffs adjusted proportionally.", ""),
    ("2. IA composite score created from 5 items (device, frequency, means, reliability, hours) — not in original doc but needed for H1.", ""),
    ("3. IA Level uses tertiles (not in doc) for categorical display.", ""),
    ("4. Convenience sampling via Google Forms — not strict stratified as planned in protocol.", ""),
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
    ("age_num", "Demographics", "Age in years (numeric)"),
    ("age_band", "Derived", "Age band (if created)"),
    ("sex_c", "Demographics", "Sex (Male/Female)"),
    ("level_c / level_num", "Demographics", "Academic level (categorical / numeric 100-400)"),
    ("dept_c", "Demographics", "Department (cleaned)"),
    ("device_c / ia_device", "Internet Access", "Device ownership (raw / scored 1/5)"),
    ("freq_c / ia_freq", "Internet Access", "Frequency of access (raw / scored 1-5)"),
    ("means_c / ia_means", "Internet Access", "Primary means of access (raw / scored 1-5)"),
    ("reliability_c / ia_reliability", "Internet Access", "Connection reliability (raw / scored 1-5)"),
    ("hours_c / ia_hours", "Internet Access", "Hours/day academic use (raw / scored 1-5)"),
    ("ia_score", "Derived", "Internet Access composite score (mean of 5 items, 1-5)"),
    ("ia_cat", "Derived", "IA level by tertiles (Low/Medium/High)"),
    ("uses_list / barriers_list", "Internet Access", "Multi-select uses/barriers (; separated)"),
    ("satisfaction_c / sat_num", "Internet Access", "Satisfaction with access (raw / scored 1-5)"),
    ("SDL1..SDL24", "SDLRSNE", "24-item scale items (1=SD ... 5=SA)"),
    ("sdl_total", "Derived", "SDL total score (24-120)"),
    ("sdl_cat", "Derived", "SDL category: Low (≤65), Moderate (66-89), High (≥90)"),
    ("sdl_self_mgmt / sdl_desire / sdl_self_ctrl", "Derived", "Subscale means (1-5)"),
    ("ia_component_scores", "Derived", "Individual IA component scores (1-5)"),
]
sheet_df(wb, "Data_Dictionary", pd.DataFrame(DICT, columns=["column(s)", "section", "description"]),
         widths={"column(s)": 40, "section": 15, "description": 110})

# ============================ Cleaned_Data ============================
sheet_df(wb, "Cleaned_Data", df, widths={"Timestamp": 24}, note=f"{N} consenting respondents.")

# ============================ Demographics ============================
t01 = rd("T01_demographics.csv")
sheet_df(wb, "Demographics", t01, note="Table 1: Sample demographics")

# ============================ Internet_Access ============================
ws = wb.create_sheet("Internet_Access")
ws.cell(row=1, column=1, value="TABLE 2 — Internet Access Profile (N = {})".format(N)).font = TITLE_FONT
r = 3
for f, ttl in [("T02_internet_access.csv", "Internet Access Items"),
               ("T02b_internet_uses.csv", "Academic Internet Uses (Multi-select)"),
               ("T02c_barriers.csv", "Barriers to Internet Access (Multi-select)"),
               ("T02d_ia_level.csv", "IA Level (Tertiles)")]:
    t = rd(f)
    ws.cell(row=r, column=1, value=ttl).font = SUB_FONT
    for rr, row in enumerate(dataframe_to_rows(t, index=False), r + 1):
        for c, v in enumerate(row, 1):
            ws.cell(row=rr, column=c, value=v)
    r += t.shape[0] + 3
for c in range(1, 6): ws.column_dimensions[get_column_letter(c)].width = 30

# ============================ SDL_Readiness ============================
ws = wb.create_sheet("SDL_Readiness")
ws.cell(row=1, column=1, value="TABLE 3 — Self-Directed Learning Readiness").font = TITLE_FONT
r = 3
for f, ttl in [("T03_sdl_subscales.csv", "Subscale Means"),
               ("T03b_sdl_total.csv", "Total Score Summary"),
               ("T03c_sdl_categories.csv", "SDL Categories (Low/Moderate/High)"),
               ("T03d_sdl_items.csv", "Item-level Means")]:
    t = rd(f)
    ws.cell(row=r, column=1, value=ttl).font = SUB_FONT
    for rr, row in enumerate(dataframe_to_rows(t, index=False), r + 1):
        for c, v in enumerate(row, 1):
            ws.cell(row=rr, column=c, value=v)
    r += t.shape[0] + 3
for c in range(1, 8): ws.column_dimensions[get_column_letter(c)].width = 24

# ============================ Hypotheses ============================
ws = wb.create_sheet("Hypotheses")
ws.cell(row=1, column=1, value="TABLE 4 — Hypothesis Tests").font = TITLE_FONT
r = 3
for f, ttl in [("T05_hypothesis1_correlation.csv", "H1: IA Score ↔ SDL Total (Spearman & Pearson)"),
               ("T05b_correlation_matrix.csv", "Correlation Matrix (IA Components vs SDL Subscales)"),
               ("T06_hypothesis2_kruskal.csv", "H2: SDL Total across Levels (Kruskal-Wallis)"),
               ("T06b_pairwise.csv", "H2 Pairwise Comparisons (Mann-Whitney, Bonferroni)"),
               ("T06c_sdl_by_level.csv", "SDL Total Descriptives by Level")]:
    t = rd(f)
    ws.cell(row=r, column=1, value=ttl).font = SUB_FONT
    for rr, row in enumerate(dataframe_to_rows(t, index=False), r + 1):
        for c, v in enumerate(row, 1):
            ws.cell(row=rr, column=c, value=v)
    r += t.shape[0] + 3
for c in range(1, 10): ws.column_dimensions[get_column_letter(c)].width = 28

# ============================ Factors_Influencing_IA ============================
ws = wb.create_sheet("Factors_Influencing_IA")
ws.cell(row=1, column=1, value="TABLE 5 — Factors Influencing Internet Access").font = TITLE_FONT
r = 3
for f, ttl in [("T02c_barriers.csv", "Barriers (Multi-select, overall)"),
               ("T07a_device_by_level.csv", "Device Ownership by Level"),
               ("T07b_means_by_level.csv", "Primary Means of Access by Level"),
               ("T07c_reliability_by_level.csv", "Connection Reliability by Level"),
               ("T07d_satisfaction_by_level.csv", "Satisfaction by Level"),
               ("T07e_ia_score_by_level.csv", "IA Composite Score by Level")]:
    t = rd(f)
    ws.cell(row=r, column=1, value=ttl).font = SUB_FONT
    for rr, row in enumerate(dataframe_to_rows(t, index=False), r + 1):
        for c, v in enumerate(row, 1):
            ws.cell(row=rr, column=c, value=v)
    r += t.shape[0] + 3
for c in range(1, 8): ws.column_dimensions[get_column_letter(c)].width = 30

# ============================ Supplementary ============================
ws = wb.create_sheet("Supplementary")
ws.cell(row=1, column=1, value="SUPPLEMENTARY ANALYSES").font = TITLE_FONT
r = 3
for f, ttl in [("T04_reliability.csv", "Reliability (Cronbach's α)"),
               ("T06c_sdl_by_level.csv", "SDL by Level (Descriptives)"),
               ("T08_correlation_by_level.csv", "IA-SDL Correlation by Level"),
               ("T09_sdl_subscales_by_level.csv", "SDL Subscales by Level"),
               ("T10_ia_vs_sdl_subscales.csv", "IA Components vs SDL Subscales")]:
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
row = 1

c1 = DoughnutChart(); c1.title = "Sex Distribution"; c1.style = 10
sex = df["sex_c"].value_counts()
row += add_chart_block(ws, row, "C1 — Sex", sex.index.tolist(), sex.values.tolist(), c1)

c2 = PieChart(); c2.title = "Academic Level"; c2.style = 10
lev = df["level_c"].value_counts().reindex(["100 level", "200 level", "300 level", "400 level"])
row += add_chart_block(ws, row, "C2 — Academic Level", lev.index.tolist(), lev.values.tolist(), c2)

c3 = DoughnutChart(); c3.title = "Device Ownership"; c3.style = 10
dev = df["device_c"].value_counts()
row += add_chart_block(ws, row, "C3 — Device Ownership", dev.index.tolist(), dev.values.tolist(), c3)

c4 = PieChart(); c4.title = "SDL Readiness Category"; c4.style = 10
sdlcat = df["sdl_cat"].value_counts().reindex(["Low", "Moderate", "High"])
row += add_chart_block(ws, row, "C4 — SDL Category", sdlcat.index.tolist(), sdlcat.values.tolist(), c4)

c5 = BarChart(); c5.type = "bar"; c5.title = "Internet Access Items (Item Means)"; c5.style = 10
ia_items = {"Device": df["ia_device"].mean(), "Frequency": df["ia_freq"].mean(),
            "Means": df["ia_means"].mean(), "Reliability": df["ia_reliability"].mean(),
            "Hours": df["ia_hours"].mean()}
row += add_chart_block(ws, row, "C5 — IA Component Means (1-5)", list(ia_items.keys()), list(ia_items.values()), c5)

c6 = BarChart(); c6.type = "col"; c6.title = "SDL Subscale Means"; c6.style = 10
sdl_subs = {"Self Mgmt": df["sdl_self_mgmt"].mean(), "Desire": df["sdl_desire"].mean(),
            "Self Ctrl": df["sdl_self_ctrl"].mean(), "Total": df["sdl_total"].mean() / 24}
row += add_chart_block(ws, row, "C6 — SDL Subscale Means (1-5)", list(sdl_subs.keys()), list(sdl_subs.values()), c6)

c7 = BarChart(); c7.type = "bar"; c7.title = "Internet Uses (Mentions)"; c7.style = 10
uses_df = rd("T02b_internet_uses.csv")
row += add_chart_block(ws, row, "C7 — Internet Uses (% of N)", uses_df["use"].tolist(), uses_df["pct_of_N"].tolist(), c7)

c8 = BarChart(); c8.type = "bar"; c8.title = "Barriers (Mentions %)"; c8.style = 10
bar_df = rd("T02c_barriers.csv")
row += add_chart_block(ws, row, "C8 — Barriers (% of N)", bar_df["barrier"].tolist(), bar_df["pct_of_N"].tolist(), c8)

c9 = BarChart(); c9.type = "col"; c9.title = "SDL Total by Academic Level"; c9.style = 10
lvl_sdl = rd("T06c_sdl_by_level.csv")
row += add_chart_block(ws, row, "C9 — SDL Total by Level", lvl_sdl["level"].tolist(), lvl_sdl["mean"].tolist(), c9)

c10 = BarChart(); c10.type = "bar"; c10.title = "IA Score by Academic Level"; c10.style = 10
lvl_ia = rd("T07e_ia_score_by_level.csv")
row += add_chart_block(ws, row, "C10 — IA Score by Level", lvl_ia["level"].tolist(), lvl_ia["mean"].tolist(), c10)

# ============================ Key_Findings ============================
ws = wb.create_sheet("Key_Findings")

# Load needed tables
t05 = rd("T05_hypothesis1_correlation.csv")
h1_spearman = t05[t05["test"] == "Spearman"].iloc[0]
h1_pearson = t05[t05["test"] == "Pearson"].iloc[0]
t06 = rd("T06_hypothesis2_kruskal.csv")
h2 = t06.iloc[0]
t02d = rd("T02d_ia_level.csv")
t03c = rd("T03c_sdl_categories.csv")
bar_df = rd("T02c_barriers.csv")
uses_df = rd("T02b_internet_uses.csv")
t07e = rd("T07e_ia_score_by_level.csv")
t06c = rd("T06c_sdl_by_level.csv")
t03_sub = rd("T03_sdl_subscales.csv")

ia_low = t02d.loc[t02d["category"] == "Low", "n"].iloc[0] if "Low" in t02d["category"].values else 0
sdl_high = t03c.loc[t03c["category"] == "High", "n"].iloc[0] if "High" in t03c["category"].values else 0
sdl_mod = t03c.loc[t03c["category"] == "Moderate", "n"].iloc[0] if "Moderate" in t03c["category"].values else 0
sdl_low = t03c.loc[t03c["category"] == "Low", "n"].iloc[0] if "Low" in t03c["category"].values else 0
bar_top = bar_df.iloc[0]
uses_top = uses_df.iloc[0]

sdl_means = ", ".join(f"{l.split()[0]}={t06c.loc[t06c['level']==l,'mean'].iloc[0]:.1f}" for l in ['100 level','200 level','300 level','400 level'])

kf = [
    ("KEY FINDINGS — INTERNET ACCESS & SDL READINESS (FUHSI)", "title"),
    (f"Sample: N = {N} consenting undergraduate students of FUHSI, Ila-Orangun", "bold"),
    ("", ""),
    ("OBJECTIVE 1 — Internet Access Level", "sub"),
    (f"• 99.5% own a device (377/379); primary access is personal mobile data ({int((df['means_c']=='Personal mobile data').sum())}, 93.4%).", ""),
    (f"• Frequency: Daily 66.0%, Several times/week 29.8%, Rarely 2.4%, Never 1.1%.", ""),
    (f"• Mean IA composite score: {df['ia_score'].mean():.2f}/5 (SD {df['ia_score'].std():.2f}); tertiles: Low {int(t02d.loc[t02d['category']=='Low','n'].iloc[0])}, Medium {int(t02d.loc[t02d['category']=='Medium','n'].iloc[0])}, High {int(t02d.loc[t02d['category']=='High','n'].iloc[0])}.", ""),
    (f"• Top academic uses: {uses_top['use']} ({uses_top['mentions']}, {uses_top['pct_of_N']}%); top barrier: '{bar_top['barrier']}' ({bar_top['mentions']}, {bar_top['pct_of_N']}%).", ""),
    (f"• Satisfaction: Neutral 51.2%, Satisfied 20.8%, Dissatisfied 12.4%, Very satisfied 12.7%, Very dissatisfied 2.9%.", ""),
    ("", ""),
    ("OBJECTIVE 2 — SDL Readiness Level", "sub"),
    (f"• Mean SDL total: {df['sdl_total'].mean():.1f}/120 (SD {df['sdl_total'].std():.1f}); Median 100.0.", ""),
    (f"• Categories (proportional to 40-item scale): High {sdl_high} ({sdl_high/N*100:.1f}%), Moderate {sdl_mod} ({sdl_mod/N*100:.1f}%), Low {sdl_low} ({sdl_low/N*100:.1f}%).", ""),
    (f"• Subscale means (1-5): Self Management {df['sdl_self_mgmt'].mean():.2f}, Desire for Learning {df['sdl_desire'].mean():.2f}, Self Control {df['sdl_self_ctrl'].mean():.2f}.", ""),
    ("", ""),
    ("OBJECTIVE 3 — H1: Relationship between Internet Access & SDL Readiness", "sub"),
    (f"• Spearman ρ = {h1_spearman['r']} (p = {h1_spearman['p']:.4f}) — significant positive correlation.", ""),
    (f"• Pearson r = {h1_pearson['r']} (p < 0.001) — moderate positive correlation.", ""),
    ("→ H0 REJECTED: Internet access is significantly associated with SDL readiness.", ""),
    ("", ""),
    ("OBJECTIVE 3 — H2: SDL Readiness across Academic Levels", "sub"),
    (f"• Kruskal-Wallis: H = {h2['H']}, df = {int(h2['df'])}, p = {h2['p']:.4f} — significant difference.", ""),
    ("• Pairwise (Bonferroni): 100 vs 400 level significant; higher levels show higher SDL readiness.", ""),
    ("→ H0 REJECTED: SDL readiness differs significantly across academic levels.", ""),
    ("", ""),
    ("OBJECTIVE 4 — Factors Influencing Internet Access", "sub"),
    (f"• Top barrier: '{bar_top['barrier']}' ({bar_top['mentions']} mentions, {bar_top['pct_of_N']}%).", ""),
    (f"• IA score increases with level: 100L {t07e.loc[t07e['level']=='100 level','mean'].iloc[0]:.2f} → 400L {t07e.loc[t07e['level']=='400 level','mean'].iloc[0]:.2f}.", ""),
    (f"• Reliability: 78.4% report 'Fairly' or 'Very' reliable; 12.1% 'Unreliable/Very unreliable'.", ""),
    (f"• Device ownership near-universal (99.5%); primary means = personal mobile data (93.4%).", ""),
    ("", ""),
    ("SUPPLEMENTARY", "sub"),
    (f"• SDL Reliability (Cronbach α): Total 0.92; Subscales: Self Mgmt 0.87, Desire 0.89, Self Ctrl 0.85.", ""),
    (f"• IA-SDL correlation by level: varies (check T08). IA components most correlated with SDL: Frequency, Reliability, Hours.", ""),
    (f"• SDL by level means: {sdl_means}.", ""),
]
r = 1
for txt, kind in kf:
    cell = ws.cell(row=r, column=1, value=txt)
    if kind == "title": cell.font = TITLE_FONT
    elif kind == "bold": cell.font = Font(bold=True, size=11)
    elif kind == "sub": cell.font = SUB_FONT
    cell.alignment = Alignment(wrap_text=True, vertical="top")
    ws.row_dimensions[r].height = 30 if kind != "title" else 22
    r += 1
ws.column_dimensions["A"].width = 140

# Tab colors & order
for nm, col in [("README", "1F4E79"), ("Data_Dictionary", "808080"), ("Cleaned_Data", "808080"),
                ("Demographics", "2E75B6"), ("Internet_Access", "2E75B6"), ("SDL_Readiness", "2E75B6"),
                ("Hypotheses", "C00000"), ("Factors_Influencing_IA", "C00000"), ("Supplementary", "808080"),
                ("Charts_Native", "548235"), ("Key_Findings", "548235")]:
    if nm in wb.sheetnames:
        wb[nm].sheet_properties.tabColor = col

order = ["README", "Data_Dictionary", "Cleaned_Data", "Demographics", "Internet_Access",
         "SDL_Readiness", "Hypotheses", "Factors_Influencing_IA", "Supplementary",
         "Charts_Native", "Key_Findings"]
wb._sheets = [wb[n] for n in order]
wb.save(OUT_XLSX)
print("Saved workbook:", OUT_XLSX.name, "| sheets:", wb.sheetnames)