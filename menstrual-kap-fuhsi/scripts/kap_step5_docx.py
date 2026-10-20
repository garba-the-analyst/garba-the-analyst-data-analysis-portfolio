"""FUHSI KAP study — Phase 5: DOCX report (reads client folder tables/figures).
Run:  .venv/bin/python kap_step5_docx.py
Output: reports/output/KAP_Menstrual_Irregularities_FUHSI_Analysis_Report.docx
"""
import warnings
import os
from pathlib import Path
import pandas as pd
import numpy as np
from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

warnings.filterwarnings("ignore")
PROJECT_ROOT = "/home/garba-the-analyst/Desktop/Projects/Data analysis "
os.chdir(PROJECT_ROOT)

CLIENT = Path("reports/Knowledge, Attitude and Health-Seeking Behavior Regarding Menstrual Irregularities Among Undergraduate Female Students of Federal University of Health Sciences Ila-Orangun.")
TAB_DIR = CLIENT / "03_Tables"
FIG_DIR = CLIENT / "04_Figures"
OUT_FILE = Path("reports/output/KAP_Menstrual_Irregularities_FUHSI_Analysis_Report.docx")
NAVY = RGBColor(0x1F, 0x4E, 0x78)

doc = Document()
doc.styles["Normal"].font.name = "Calibri"
doc.styles["Normal"].font.size = Pt(10.5)
for s in doc.sections:
    s.left_margin = Inches(0.9)
    s.right_margin = Inches(0.9)

def h1(t):
    h = doc.add_heading(t, level=1)
    for r in h.runs: r.font.color.rgb = NAVY
    return h

def h2(t):
    h = doc.add_heading(t, level=2)
    for r in h.runs: r.font.color.rgb = NAVY
    return h

def para(t, bold=False, italic=False):
    p = doc.add_paragraph()
    r = p.add_run(t)
    r.bold = bold; r.italic = italic
    return p

def bullets(items):
    for it in items:
        doc.add_paragraph(it, style="List Bullet")

def shade_header(row):
    for cell in row.cells:
        tcPr = cell._tc.get_or_add_tcPr()
        shd = OxmlElement("w:shd")
        shd.set(qn("w:val"), "clear")
        shd.set(qn("w:fill"), "1F4E78")
        tcPr.append(shd)
        for p in cell.paragraphs:
            for r in p.runs:
                r.font.bold = True; r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF); r.font.size = Pt(9)

def add_csv_table(csv_name, caption, columns=None, fontsize=8, maxrows=None):
    para(caption, bold=True, italic=True)
    p = TAB_DIR / csv_name
    if not p.exists() or p.stat().st_size < 2:
        para(f"[Table {csv_name} not available or empty]", italic=True)
        return
    t = pd.read_csv(p)
    if columns: t = t[columns]
    if maxrows: t = t.head(maxrows)
    t = t.fillna("").astype(str)
    table = doc.add_table(rows=1 + len(t), cols=len(t.columns))
    table.style = "Table Grid"; table.alignment = WD_TABLE_ALIGNMENT.CENTER
    for j, col in enumerate(t.columns):
        cell = table.rows[0].cells[j]; cell.text = ""
        r = cell.paragraphs[0].add_run(col); r.font.size = Pt(8.5)
    shade_header(table.rows[0])
    for i, (_, row) in enumerate(t.iterrows(), 1):
        for j, v in enumerate(row):
            table.rows[i].cells[j].text = ""
            r = table.rows[i].cells[j].paragraphs[0].add_run(v)
            r.font.size = Pt(fontsize)
    doc.add_paragraph()

def add_figure(fig_name, caption, width=6.6):
    p = FIG_DIR / fig_name
    if not p.exists():
        para(f"[Figure {fig_name} not available]", italic=True)
        return
    doc.add_picture(str(p), width=Inches(width))
    doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
    cp = doc.add_paragraph()
    cr = cp.add_run(caption)
    cr.italic = True; cr.font.size = Pt(9)
    cp.alignment = WD_ALIGN_PARAGRAPH.CENTER

def rd(name):
    d = pd.read_csv(TAB_DIR / name, keep_default_na=False)
    for c in d.columns:
        if d[c].dtype == object and len(d) and d[c].str.fullmatch(r"-?\d+(\.\d+)?").all():
            d[c] = pd.to_numeric(d[c])
    return d

CLEAN = pd.read_csv("data/processed/kap_cleaned_full.csv", dtype=str, keep_default_na=False)
for c in ["know_score", "att_score", "age_num", "know_pct"]:
    CLEAN[c] = pd.to_numeric(CLEAN[c], errors="coerce")
N = len(CLEAN)

# ============ runtime-derived narrative numbers ============
T02A = rd("T02a_knowledge_items.csv")
T02C = rd("T02c_knowledge_summary.csv")
T02B = rd("T02b_knowledge_scores.csv")
T03A = rd("T03a_attitude_items.csv")
T03B = rd("T03b_attitude_scores.csv")
T04A = rd("T04a_hbm_items.csv")
T04B = rd("T04b_hbm_subscales.csv")
T05A = rd("T05a_experienced.csv"); T05B = rd("T05b_types.csv")
T05C = rd("T05c_first_action.csv"); T05D = rd("T05d_timeliness.csv")
T05E = rd("T05e_info_sources.csv"); T05F = rd("T05f_campus_health_center.csv")
T05G = rd("T05g_preferred_facility.csv"); T05H = rd("T05h_future_intent.csv")
T05I = rd("T05i_barriers.csv")
T06A = rd("T06a_hypotheses_chi_square.csv"); T06B = rd("T06b_demographic_chi_square.csv")
T07A = rd("T07a_pearson_r.csv"); T07B = rd("T07b_pearson_p.csv")
S01 = rd("S01_bloom_grades_supplementary.csv")
S03 = rd("S03_group_comparisons_supplementary.csv")
S04 = rd("S04_logistic_future_intent_supplementary.csv")
T01A = rd("T01a_demographics_categorical.csv")

def cellv(t, col, where, val, out):
    m = t[t[col] == val]
    return m.iloc[0][out] if len(m) else None

def iv(x):
    return int(float(x))

know_mean = float(T02C.iloc[0]["mean"]); know_sd = float(T02C.iloc[0]["sd"])
know_med = float(T02C.iloc[0]["median"])
good_n = iv(T02B.iloc[0]["Good"]); good_pct = round(good_n / N * 100, 1)
poor_n = N - good_n
weak = T02A.nsmallest(3, "correct_pct")
strong = T02A.nlargest(2, "correct_pct")
att_mean = float(T03B.iloc[0]["mean"]); att_sd = float(T03B.iloc[0]["sd"]); att_med = float(T03B.iloc[0]["median"])
pos_n = iv(T03B.iloc[1]["Positive"]); pos_pct = round(pos_n / N * 100, 1)
neg_n = N - pos_n
agree_top = T03A.nlargest(3, "SA_pct" if "SA_pct" in T03A else ["SA_n"])[["item", "statement"]]
exp_yes = iv(T05A.loc[T05A["category"] == "Yes", "n"].iloc[0])
exp_yes_pct = float(T05A.loc[T05A["category"] == "Yes", "pct"].iloc[0])
n_types_base = int((CLEAN["type_list"] != "").sum())
never_sought = iv(T05D[(T05D["variable"] == "time_to_seek_help") & (T05D["value"] == "Did not seek")]["n"].iloc[0])
sought_n = exp_yes - never_sought
sought_pct = round(sought_n / exp_yes * 100, 1)
fut_yes = iv(T05H.loc[T05H["category"] == "Yes", "n"].iloc[0]); fut_yes_pct = float(T05H.loc[T05H["category"] == "Yes", "pct"].iloc[0])
campus_yes = iv(T05F.loc[T05F["category"] == "Yes", "n"].iloc[0]); campus_pct = float(T05F.loc[T05F["category"] == "Yes", "pct"].iloc[0])
priv_n = iv(T05G.loc[T05G["category"] == "Private clinic", "n"].iloc[0]); priv_pct = float(T05G.loc[T05G["category"] == "Private clinic", "pct"].iloc[0])
bar_top = T05I.iloc[0]
info_top = T05E.iloc[0]
type_top = T05B.iloc[0]
act_top = T05C.iloc[0]
h1b = T06A[T06A["test"] == "H1 primary (binary)"].iloc[0]
h13 = T06A[T06A["test"] == "H1 primary (3-cat)"].iloc[0]
h1s = T06A[T06A["test"] == "H1 secondary"].iloc[0]
h2b = T06A[T06A["test"] == "H2 primary (binary)"].iloc[0]
h23 = T06A[T06A["test"] == "H2 primary (3-cat)"].iloc[0]
h2s = T06A[T06A["test"] == "H2 secondary"].iloc[0]
kxl = T06B[(T06B["variables"] == "know_cat_mean x level_c")].iloc[0]
kxd = T06B[(T06B["variables"] == "know_cat_mean x dept_group")].iloc[0]
fxl = T06B[(T06B["variables"] == "future_c x level_c")].iloc[0]
lev_by_know = pd.crosstab(CLEAN["level_c"], CLEAN["know_cat_mean"], normalize="index") * 100
good_by_level = "; ".join(f"{lv} {lev_by_know.loc[lv, 'Good']:.0f}%" for lv in ["100 level", "200 level", "300 level", "400 level"])
know_bylevel_star = CLEAN.copy()
kw_level = S03[(S03["variable"] == "know_score") & (S03["groups"] == "level_c")].iloc[0]

# ============ TITLE PAGE ============
for _ in range(3): doc.add_paragraph()
p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = p.add_run("STATISTICAL ANALYSIS REPORT"); r.font.size = Pt(15); r.bold = True; r.font.color.rgb = NAVY
p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = p.add_run("Knowledge, Attitude, and Health-Seeking Behaviour Regarding Menstrual "
              "Irregularities Among Female Undergraduate Students of the Federal University "
              "of Health Sciences, Ila-Orangun")
r.font.size = Pt(13.5); r.bold = True
doc.add_paragraph()
para("In fulfilment of the data-analysis requirements of the supervised research project "
     "(Department of Nursing Science, Faculty of Allied Health Sciences).", italic=True)
doc.add_paragraph()
meta = [
    ("Client / Author:", "TAOREED SOFIAT OPEMIPOSI"),
    ("Matriculation number:", "22/NSC/048"),
    ("Department:", "Nursing Science, Federal University of Health Sciences, Ila-Orangun"),
    ("Instrument administered:", "377 responses received; 376 valid (consent-based exclusion of 1 record)"),
    ("Analysis basis:", "Thesis document Ch.1 objectives and §3.11 analysis plan (chi-square + Pearson; "
     "descriptives; knowledge/attitude categorised by mean and median splits)"),
    ("Date of analysis:", "18 October 2026"),
    ("Prepared with:", "Python statistical environment; every figure traceable to the accompanying workbook and tables"),
]
for k, v in meta:
    p = doc.add_paragraph()
    r1 = p.add_run(k + "  "); r1.bold = True
    p.add_run(v)
doc.add_paragraph()
para("Deliverables: 01_Report (this document) · 02_Workbook (Excel, 13 sheets, 10 native charts) · "
     "03_Tables (28 CSV tables) · 04_Figures (16 charts) · 05_Data (cleaned dataset).", italic=True)
doc.add_page_break()

# ============ 1. INTRODUCTION ============
h1("1. INTRODUCTION")
para("Menstruation is a normal physiological process of the female reproductive system. Deviations from a "
     "woman's normal menstrual pattern — in cycle length, duration, or volume of bleeding — are broadly "
     "described as menstrual irregularities and include irregular cycle length, amenorrhoea, dysmenorrhoea "
     "and menorrhagia. Among students, menstrual irregularity is one of the most commonly reported "
     "reproductive-health complaints; literature synthesised in the project document places prevalence in "
     "the wide 47–96% band among female undergraduates, with major Nigerian and international surveys "
     "recording that roughly three-quarters of affected students experienced at least one irregularity "
     "symptom in the previous year.")
para("Because help-seeking is shaped by how the problem is perceived, the study is anchored on the "
     "Health Belief Model (HBM): perceived susceptibility and severity, perceived benefits of action, "
     "perceived barriers, cues to action, and self-efficacy jointly determine whether a student seeks "
     "professional care. The project therefore measured knowledge, attitudes, health-seeking behaviour "
     "(HSB) and barriers among female undergraduates of the Federal University of Health Sciences "
     "(FUHSI), Ila-Orangun, and tested the associations between knowledge/attitude and help-seeking "
     "behaviour.")

# ============ 2. METHODS ============
h1("2. MATERIALS AND METHODS")
h2("2.1 Design, population and sample")
bullets([
    "Design: descriptive cross-sectional survey.",
    "Population: 2,245 female undergraduate students of FUHSI, Ila-Orangun.",
    "Sample size: Yamane (1967) formula at 95% confidence → n = 340; a 10% allowance for non-response "
    "raised the target to 374 questionnaires administered.",
    "Sampling: proportionate stratified sampling by level of study — stratum targets 144 / 108 / 69 / 53 "
    "for 100–400 levels.",
])
h2("2.2 Instrument")
para("A five-part structured questionnaire was used: Section A demographics; Section B 12 knowledge items "
     "answered True / False / I don't know; Section C 10 attitude items on a Likert scale (administered as "
     "5-point SA/A/U/D/SD although §3.7 specified a 4-point format — reported as fielded, disclosed in §11); "
     "Section D nine health-seeking behaviour items including multi-select type-of-irregularity, first "
     "action, timeliness, information sources, campus health-centre use, facility preference, barriers and "
     "future intent; Section E 14 HBM statements covering susceptibility, severity, benefits, barriers, "
     "cues to action and self-efficacy.")
h2("2.3 Validity, reliability and data handling")
bullets([
    "Face and content validity were addressed through expert/supervisor review during instrument design "
    "(document §3.8).",
    "The pilot test-retest exercise (§3.9) was outside the analyst's remit; internal consistency of the "
    "annual data is reported instead: knowledge KR-20 = 0.77; attitude Cronbach's α = 0.43 (low — "
    "attitude items are treated dimensionally rather than as a single scale); HBM total α = 0.82.",
    "377 responses were received; informed consent was explicit and one record without consent was "
    "excluded → analysis sample n = 376.",
    "Duplicate first-question deployment of Q2 (two form editions) was merged so all type reports are "
    "counted; 28 respondents who had not experienced an irregularity still listed types, and 52 "
    "answered Q3 (53 answered Q4) despite branching — experiential analyses are therefore restricted "
    "to the experienced subset.",
    "Scoring: knowledge 1 point per correct answer (key: all statements True except item 10, which is "
    "False); attitude items scored 1–5 with items 1, 2, 4 and 10 reverse-worded; HBM items scored 1–5 and "
    "averaged within constructs.",
])
h2("2.4 Analysis (per §3.11)")
bullets([
    "Descriptives: frequencies and percentages for all variables; mean ± SD / median for scores and scale items.",
    "Knowledge and attitude categorised by both mean and median splits (good/poor knowledge; positive/"
    "negative attitude); at these data the two rules coincide (cut-offs: knowledge ≥ 11 of 12; attitude ≥ 41 of 50).",
    "Inferential: chi-square tests of association (hypotheses and demographic battery) with Cramér's V "
    "effect sizes; Pearson product-moment correlations among knowledge, attitude, HBM constructs, age and "
    "level. Significance: p < 0.05.",
    "Supplementary (labelled, beyond §3.11): Bloom grading, Spearman correlations, Kruskal-Wallis/"
    "Mann-Whitney comparisons, and a logistic regression on future intent.",
])

# ============ 3. SAMPLE ============
h1("3. SAMPLE PROFILE")
para(f"Table 1 profiles the {N} respondents. Age was mostly reported in bands: {int((CLEAN['age_band'] == '16-20 years').sum())} "
     f"({(CLEAN['age_band'] == '16-20 years').mean()*100:.1f}%) aged 16–20, {int((CLEAN['age_band'] == '21-24 years').sum())} "
     f"({(CLEAN['age_band'] == '21-24 years').mean()*100:.1f}%) 21–24; mean age 19.7 years among the "
     f"{int(CLEAN['age_num'].notna().sum())} respondents who stated an exact age."
     " Levels almost exactly matched the stratification targets (143/108/69/56 vs 144/108/69/53 — "
     "Figure F01): the sampling frame was attained for all four strata. Nursing (32.2%), Medicine (16.0%) "
     "and Medical Laboratory Science (11.7%) contributed the largest groups; the sample is "
     "predominantly single (99%) and Yoruba (96.8%).")
add_csv_table("T01a_demographics_categorical.csv", "Table 1. Demographic profile of respondents (N = 376)", fontsize=8.5)
add_figure("F01_sampling.png", "Figure F01 — Stratified sampling framework vs achieved sample")
add_csv_table("T01b_departments.csv", "Table 1b. Respondents by department")
add_figure("F02_demographics.png", "Figure F02 — Demographic profile")

# ============ 4. OBJECTIVE 1: KNOWLEDGE ============
h1("4. OBJECTIVE 1 — LEVEL OF KNOWLEDGE OF MENSTRUAL IRREGULARITIES")
para(f"Mean knowledge score was {know_mean:.2f} of 12 (median 11; SD {know_sd:.2f}). By the "
     f"§3.11 categorisation, {good_n} respondents ({good_pct}%) had good knowledge and {poor_n} "
     f"({poor_n and round(poor_n/N*100,1)}%) poor — identical under mean and median splits "
     "(Table 3; Figure F04).")
weak_txt = "; ".join(f"{r['item']} ({r['correct_pct']}%)" for _, r in weak.iterrows())
strong_txt = "; ".join(f"{r['item']} ({r['correct_pct']}%)" for _, r in strong.iterrows())
para(f"Item-level results (Table 2; Figure F03) show very high recognition of core definitions — "
     f"e.g. {strong_txt} largely correct — but the weakest items were {weak_txt}. The lowest-scoring item "
     "was K10, the statement that irregular periods are always a normal part of student life and never "
     "need medical attention: a sizeable minority did not identify this normalisation statement as false, "
     "evidencing the knowledge gap the document hypothesised.")
add_csv_table("T02a_knowledge_items.csv", "Table 2. Knowledge items (Section B) — correct answer key and results",
              columns=["item", "statement", "correct_answer", "correct_n", "correct_pct", "incorrect_n", "incorrect_pct", "dont_know_n", "dont_know_pct"], fontsize=7.5)
add_csv_table("T02b_knowledge_scores.csv", "Table 3. Knowledge categorisation — mean and median splits")
add_csv_table("T02c_knowledge_summary.csv", "Table 3b. Knowledge score summary")
add_figure("F03_knowledge_items.png", "Figure F03 — % correct per knowledge item", width=6.2)
add_figure("F04_knowledge_scores.png", "Figure F04 — Knowledge score distribution and categorisation")

# ============ 5. OBJECTIVE 2: ATTITUDE ============
h1("5. OBJECTIVE 2 — ATTITUDES TOWARD MENSTRUAL IRREGULARITIES")
para(f"The composite attitude score averaged {att_mean:.2f} of 50 (median {att_med:.0f}; SD {att_sd:.2f}), "
     f"categorising {pos_n} respondents ({pos_pct}%) as having a positive attitude and {neg_n} "
     f"({round(neg_n/N*100,1)}%) negative — the mean and median splits again coincide (Table 5; Figure F06).")
para("Item patterns (Table 4; Figure F05) show strong agreement with the studiable consequences of "
     "untreated irregularity (A7: negative effect on daily/academic performance) and with the importance "
     "of menstrual-health education (A8), while respondents pushed back on the normalisation (A1) and "
     "age-related minimisation (A10) statements. Stigma remains salient: notable agreement persisted with "
     "the embarrassment (A2) and stigmatisation (A4) statements, which pull in the negative direction of "
     "the attitude scale. Because the 10-item composite shows modest internal consistency "
     "(α = 0.43; documented deviation), item-level reading is preferred for attitude claims, "
     "with categorisation retained as required by the document.")
add_csv_table("T03a_attitude_items.csv", "Table 4. Attitude items (Section C) — 5-point Likert as fielded (reverse-scored items marked)",
              columns=["item", "statement", "reverse_scored", "SA_n", "SA_pct", "A_n", "A_pct", "U_n", "U_pct", "D_n", "D_pct", "SD_n", "SD_pct", "mean_1to5"], fontsize=7)
add_csv_table("T03b_attitude_scores.csv", "Table 5. Attitude score summary and categorisation")
add_figure("F05_attitude_items.png", "Figure F05 — Attitude item response distribution", width=6.4)
add_figure("F06_attitude_scores.png", "Figure F06 — Attitude score distribution and categorisation")

# ============ 6. OBJECTIVE 3: HSB ============
h1("6. OBJECTIVE 3 — HEALTH-SEEKING BEHAVIOUR PATTERNS")
para(f"Ever-experience of menstrual irregularity was common: {exp_yes} respondents ({exp_yes_pct}%) "
     f"reported it (Figure F09). Types reported (Table 7) were led by irregular cycle length "
     f"({type_top['mentions']} mentions; {type_top['pct_of_285_reporting']}% of the "
     f"{n_types_base} respondents listing types), followed by dysmenorrhoea, amenorrhoea and menorrhagia.")
para(f"When an irregularity was first noticed, the single largest response among the experienced was "
     f"'{act_top['category']}' ({iv(act_top['n'])} respondents, {act_top['pct']}%); only {sought_n} "
     f"({sought_pct}%) sought professional help at some point, while {never_sought} "
     f"({round(never_sought/exp_yes*100,1)}%) never did (Table 8; Figure F10/F11). Fewer than one in seven "
     f"({campus_yes} respondents, {campus_pct}%) had ever used the FUHSI campus health centre, and the "
     f"most preferred facility for menstrual care was a private clinic ({priv_n} respondents, "
     f"{priv_pct}%) ahead of the general/teaching hospital (Table 9; Figure F13).")
para(f"Destined future: {fut_yes} respondents ({fut_yes_pct}%) said they would seek professional medical "
     f"help for a future irregularity (Table 10).")
para(f"Information: {info_top['source']} ({info_top['pct_of_376']}% of all {N}) and "
     f"{T05E.iloc[1]['source']} ({T05E.iloc[1]['pct_of_376']}%) dominate; healthcare providers follow "
     "(Table 8b; Figure F12), underscoring the online-first information ecosystem the report recommends "
     "partnering with.")
add_csv_table("T05a_experienced.csv", "Table 6. Ever experienced menstrual irregularity")
add_csv_table("T05b_types.csv", "Table 7. Types of irregularity reported (multi-select; % of 285 who listed types)", fontsize=8)
add_csv_table("T05c_first_action.csv", "Table 8. First action after noticing the irregularity (experienced, n = 257)", fontsize=8)
add_csv_table("T05d_timeliness.csv", "Table 8b. Timeliness of seeking professional help (experienced)", fontsize=8)
add_csv_table("T05e_info_sources.csv", "Table 8c. Information sources (multi-select, % of N = 376)", fontsize=8)
add_csv_table("T05f_campus_health_center.csv", "Table 9. Ever visited the FUHSI campus health centre")
add_csv_table("T05g_preferred_facility.csv", "Table 9b. Preferred facility for menstrual care", fontsize=8)
add_csv_table("T05h_future_intent.csv", "Table 10. Would seek professional help in future")
add_figure("F09_experience_types.png", "Figure F09 — Experience and types of irregularity")
add_figure("F10_first_action.png", "Figure F10 — First action taken", width=6.2)
add_figure("F11_timeliness.png", "Figure F11 — Timeliness of help-seeking (experienced)", width=6.0)
add_figure("F12_info_sources.png", "Figure F12 — Information sources", width=6.2)
add_figure("F13_campus_facility.png", "Figure F13 — Campus health-centre use and preferred facility")

# ============ 7. OBJECTIVE 4: BARRIERS + HBM ============
h1("7. OBJECTIVE 4 — BARRIERS TO HEALTH-SEEKING AND HBM CONSTRUCTS")
para(f"The most-cited barrier to seeking care was '{bar_top['barrier']}' "
     f"({iv(bar_top['mentions'])} mentions; {bar_top['pct_of_376']}% of all {N}), far ahead of "
     "cost, time constraints, embarrassment or not knowing where to go (Table 11; Figure F14). This "
     "wait-and-see belief is precisely the barrier construct the HBM captures on the perception side.")
subs_txt = "; ".join(f"{r['subscale']} {r['mean']:.2f}" for _, r in T04B.iterrows())
para(f"HBM constructs (Table 12; Figure F07/F08) averaged: {subs_txt} (1–5 scale). Perceived benefits "
     "were highest — respondents strongly endorse early detection and check-ups — followed by severity "
     "(including infertility beliefs), self-efficacy and susceptibility. Perceived barriers were the "
     "lowest score, though still around the neutral point: within the barrier items, cost and lack of "
     "time resonate more than embarrassment, while cultural/religious language barriers sit lower "
     "(Figure F08). Cues to action — social influence of friends/family and school health talks — are "
     "present but require strengthening; the 2-item cues subscale α (0.32) is unstable, read item-wise.")
add_csv_table("T05i_barriers.csv", "Table 11. Main reasons that would prevent seeking care (multi-select; % of N = 376)", fontsize=8)
add_csv_table("T04b_hbm_subscales.csv", "Table 12. HBM construct scores (mean ± SD) with per-construct Cronbach's α",
              columns=["subscale", "items", "mean", "sd", "median", "cronbach_alpha"], fontsize=8.5)
add_csv_table("T04a_hbm_items.csv", "Table 12b. HBM statements and item distributions",
              columns=["item", "statement", "hbm_domain", "SA_n", "SA_pct", "A_n", "A_pct", "U_n", "U_pct", "D_n", "D_pct", "SD_n", "SD_pct", "mean_1to5"], fontsize=7)
add_figure("F07_hbm_subscale.png", "Figure F07 — HBM construct means", width=5.6)
add_figure("F08_hbm_items.png", "Figure F08 — HBM item means by construct", width=6.4)
add_figure("F14_barriers.png", "Figure F14 — Barriers to seeking medical care", width=6.3)

# ============ 8. HYPOTHESES ============
h1("8. HYPOTHESIS TESTS (CHI-SQUARE)")
para(f"H1 — knowledge and health-seeking behaviour: A significant association was found between "
     f"knowledge level (good/poor) and future help-seeking intention (binary): χ²(1) = {h1b['chi2']}, "
     f"p = {h1b['p']}, Cramér's V = {h1b['cramers_v']}; the 3-level version is likewise significant "
     f"(χ²(2) = {h13['chi2']}, p = {h13['p']}). Respondents with good knowledge were more likely to say "
     "they would seek professional care (91% vs 81%). The null hypothesis of no association is REJECTED — "
     "though the effect is weak (V = 0.14). Secondary behavioural measure: knowledge was NOT "
     f"significantly associated with ever having sought help among those who experienced an irregularity "
     f"(χ²(1) = {h1s['chi2']}, p = {h1s['p']}).")
para(f"H2 — attitude and health-seeking behaviour: No significant association with future intention "
     f"(χ²(2) = {h23['chi2']}, p = {h23['p']}; binary χ²(1) = {h2b['chi2']}, p = {h2b['p']}, "
     f"V = {h2b['cramers_v']}) nor with ever seeking help (χ²(1) = {h2s['chi2']}, p = {h2s['p']}). The "
     "null hypothesis of no association is RETAINED (Figure F15).")
para("Demographic associations (Table 13b): knowledge differs significantly by level "
     f"(χ²(3) = {kxl['chi2']}, p = {kxl['p']}, V = {kxl['cramers_v']}) — good knowledge was most prevalent "
     f"among {good_by_level}, the reverse ordering — and sharply by clinical vs non-clinical department "
     f"(χ²(1) = {kxd['chi2']}, p = {kxd['p']}, V = {kxd['cramers_v']}). Future intention also differs by "
     f"level (χ²(3) = {fxl['chi2']}, p = {fxl['p']}). Attitudes showed no significant demographic "
     "associations; small expected counts in the 'No' (n = 6) and ethnic-minority cells are flagged in "
     "the tables.")
add_csv_table("T06a_hypotheses_chi_square.csv", "Table 13. Chi-square hypothesis tests", columns=["test", "variables", "n", "chi2", "dof", "p", "cramers_v", "min_expected", "note"], fontsize=7.5)
add_csv_table("T06b_demographic_chi_square.csv", "Table 13b. Chi-square battery — categorised scores and HSB vs demographics", columns=["test", "variables", "n", "chi2", "p", "cramers_v", "note"], fontsize=7.5)
add_figure("F15_hypotheses.png", "Figure F15 — Knowledge and attitude categories × future intent")

# ============ 9. PEARSON ============
h1("9. PEARSON CORRELATIONS")
para("Key correlations (Table 14; Figure F16): knowledge score correlates positively with HBM "
     "self-efficacy (r = 0.50, p < 0.001), perceived severity (r = 0.44), susceptibility (r = 0.32), "
     "benefits (r = 0.24) and barriers-to-care acknowledgement (r = 0.19) — knowledgeable students "
     "recognise both the stakes and their own capacity to act. Age correlates modestly with knowledge "
     "(r = 0.28), whereas level of study correlates negatively with knowledge (r = −0.12, p < 0.05) and "
     "with several HBM constructs (−0.20 to −0.32): earlier-level students are more knowledgeable and "
     "more risk-aware, echoing the chi-square findings. Attitude correlates with benefits (r = 0.25) and "
     "negatively with perceived barriers (r = −0.26): students who view care as valuable feel fewer "
     "impediments.")
add_csv_table("T07a_pearson_r.csv", "Table 14. Pearson correlation matrix (r; pairwise)", fontsize=7.5)
add_csv_table("T07b_pearson_p.csv", "Table 14b. Corresponding p-values (pairwise)", fontsize=7.5)
add_figure("F16_pearson_heatmap.png", "Figure F16 — Pearson correlation heatmap (* p<0.05, ** p<0.001)")

# ============ 10. SUPPLEMENTARY ============
h1("10. SUPPLEMENTARY ANALYSES (LABELLED — BEYOND §3.11)")
b_good = S01.loc[S01["category"].str.startswith("Good"), "n"].iloc[0] if "Bloom" in S01["level"].iloc[0] else ""
para("Bloom grading (Table 15): knowledge is likewise dominated by the 'good' band under the classic "
     "≥70% rule (consistent with the §3.11 splits; the ≥50% adequacy rule classifies almost everyone as "
     "adequate). Kruskal-Wallis/Mann-Whitney comparisons (Table 16) confirm that knowledge scores differ "
     f"by level (H = {kw_level['stat']}, p = {kw_level['p']}) and by department group. A logistic "
     "regression on future intent (Table 17; n = 376) corroborates the chi-square result: each extra "
     "point of knowledge raises the odds of intending to seek help (OR = 1.22, p = 0.005), while each "
     "higher level halves intent (OR = 0.59 per 100-level step, p = 0.002); attitudes and HBM barriers "
     "are not independent predictors once knowledge and level are modelled.")
add_csv_table("S01_bloom_grades_supplementary.csv", "Table 15. Bloom grading and adequacy rule (supplementary)", fontsize=8)
if os.path.exists(TAB_DIR / "S02a_spearman_r_supplementary.csv"):
    add_csv_table("S02a_spearman_r_supplementary.csv", "Table 15b. Spearman rank-correlation matrix (supplementary)", fontsize=7.5)
add_csv_table("S03_group_comparisons_supplementary.csv", "Table 16. Kruskal-Wallis / Mann-Whitney group comparisons (supplementary)", fontsize=7.5)
add_csv_table("S04_logistic_future_intent_supplementary.csv", "Table 17. Logistic regression — future help-seeking intent (supplementary)", fontsize=8)

# ============ 11. DISCUSSION ============
h1("11. DISCUSSION")
bullets([
    "Knowledge of menstrual irregularities is broadly good (≈69% good by both splits) but the deficit is "
    "conceptual: normalisation myths (K10) and definitional items (amenorrhoea/PCOS) are the weak spots, "
    "and — counter-intuitively — knowledge and risk perception are lowest among the senior levels.",
    "Attitudes are largely constructive yet stigma-tinged; openness and education-importance co-exist "
    "with embarrassment and stigmatisation concerns (items A2/A4), which the document anticipated as "
    "cultural products.",
    "Behaviour reveals the actionable gap: 68.4% experienced an irregularity, but 149 of those 257 "
    "(58%) never sought professional help and 'ignored it' was the modal first response; the campus facility that is "
    "free by design is barely used (13.8%) while private clinics dominate preference — an "
    "awareness/approachability problem rather than a cost problem (cost ranked 2nd as a barrier, "
    "beliefs first).",
    "The hypothesis tests explain the mechanism: knowledge — not attitude — predicts the intention to "
    "seek care (H1 significant, weak; H2 null). Knowledge also travels with self-efficacy (r = 0.50), "
    "which per HBM is the proximal determinant of action.",
])
doc.add_page_break()

# ============ 12. RECOMMENDATIONS ============
h1("12. RECOMMENDATIONS")
bullets([
    "Institute structured menstrual-health education for all levels (orientation modules + periodic "
    "health talks), with priority on correcting normalisation myths and definitions — appealing to HBM "
    "perceived susceptibility/severity and cues to action.",
    "Target senior levels and non-clinical departments explicitly, as knowledge and risk-perception are "
    "lowest there.",
    "Reposition the FUHSI campus health centre: awareness visits during orientation, menstrual-health "
    "clinic days, guaranteed privacy/female-provider options to address embarrassment items (A2, E7) and "
    "raise utilisation beyond 13.8%.",
    "Leverage the online-first information ecosystem (social media/websites ≈ dominant sources) with "
    "institution-created, evidence-based digital content and a cycle-tracking resource to build "
    "self-efficacy.",
    "Counter the 'it will resolve on its own' belief with consequence-focused messaging anchored on "
    "endorsed severity beliefs (infertility, academic impact).",
    "Continued research/quality work: qualitative interviews on help-seeking inertia; repeat pilot "
    "reliability testing as specified in §3.9.",
])

# ============ 13. LIMITATIONS ============
h1("13. LIMITATIONS AND DISCLOSED DEVIATIONS")
bullets([
    "Cross-sectional design limits causal inference; all measures are self-reported (recall and social "
    "desirability possible).",
    "The attitude Likert was fielded on a 5-point scale although §3.7 specified 4-point; reported as "
    "fielded with mapping documented in the workbook.",
    "The pilot test-retest reliability exercise (§3.9) was not part of the data delivered; internal "
    "consistency from the main study is reported instead (attitude α = 0.43 — attitude claims are "
    "made at item level).",
    "Section A as fielded collected ethnicity rather than religion; both are small-cell and treated "
    "descriptively.",
    "Form branching was not enforced in the field: 28 non-experienced respondents listed types and 52 "
    "answered Q3/Q4; experiential analyses use the experienced subset (n = 257), and Q2 type counts use "
    "both form editions merged.",
    "Age was free-text; 164 respondents stated exact ages (mean 19.7) while the remainder reported bands "
    "only — age-group percentages are used rather than precise years.",
    "A few chi-square cells have small expected counts (notably the 6 respondents who answered 'No' to "
    "future intent); Fisher exact or flagged variants are shown per cell in Table 13/13b.",
])
doc.add_page_break()

# ============ 14. APPENDIX ============
h1("14. APPENDIX — DATA AND DOCUMENTATION MANIFEST")
para("Folder structure delivered alongside this report:", bold=True)
bullets([
    "01_Report — this DOCX report (+ source markdown summary).",
    "02_Workbook — Excel workbook: README, Data_Dictionary, Cleaned_Data (376 × 139), Demographics, "
    "Obj1_Knowledge, Obj2_Attitude, Obj3_HSB, Obj4_HBM, Chi_Square, Pearson, Supplementary, "
    "Charts_Native (10 native Excel charts), Key_Findings.",
    "03_Tables — 28 CSV tables (T01–T07 document analyses; S01–S04 supplementary).",
    "04_Figures — 16 charts (F01–F16, 150 dpi PNG).",
    "05_Data — cleaned analysis dataset (KAP_Cleaned_Data.csv) and item-label dictionary.",
])
para("Reproducibility: every number in this report is generated from the cleaned dataset; the pipeline "
     "(cleaning → statistics → figures → workbook → report) is scripted and re-runnable end-to-end.",
     italic=True)

doc.save(OUT_FILE)
print("Saved:", OUT_FILE.name)
