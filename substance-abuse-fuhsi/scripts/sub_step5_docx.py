"""Substance Abuse Study — Step 5: DOCX report (reads client folder tables/figures).
Run:  .venv/bin/python sub_step5_docx.py
Output: reports/output/Substance_Abuse_FUHSI_Afolabi_Analysis_Report.docx
"""
import warnings
import os
from pathlib import Path
import pandas as pd
from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

warnings.filterwarnings("ignore")
PROJECT_ROOT = "/home/garba-the-analyst/Desktop/Projects/Data analysis "
os.chdir(PROJECT_ROOT)

CLIENT = Path("reports/Assessment of Substance Abuse and Perceived Health Implications Among Undergraduate Students of FUHSI 5")
TAB_DIR = CLIENT / "03_Tables"
FIG_DIR = CLIENT / "04_Figures"
OUT_FILE = Path("reports/output/Substance_Abuse_FUHSI_Afolabi_Analysis_Report.docx")
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
                r.font.bold = True; r.font.color.rgb = RGBColor(0xFF,0xFF,0xFF); r.font.size = Pt(9)

def add_csv_table(csv_name, caption, columns=None):
    para(caption, bold=True, italic=True)
    p = TAB_DIR / csv_name
    if not p.exists() or p.stat().st_size < 2:
        para(f"[Table {csv_name} not available or empty]", italic=True)
        return
    t = pd.read_csv(p)
    if columns: t = t[columns]
    t = t.fillna("").astype(str)
    table = doc.add_table(rows=1 + len(t), cols=len(t.columns))
    table.style = "Table Grid"; table.alignment = WD_TABLE_ALIGNMENT.CENTER
    for j, col in enumerate(t.columns):
        cell = table.rows[0].cells[j]; cell.text = ""
        r = cell.paragraphs[0].add_run(col); r.font.size = Pt(9)
    shade_header(table.rows[0])
    for i, (_, row) in enumerate(t.iterrows(), 1):
        for j, v in enumerate(row):
            table.rows[i].cells[j].text = ""
            r = table.rows[i].cells[j].paragraphs[0].add_run(v)
            r.font.size = Pt(8.5)
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

# ---- runtime numbers from cleaned data ----
CLEAN = pd.read_csv("data/processed/substance_abuse_cleaned_full.csv", dtype=str, keep_default_na=False)
for c in ["freq_c", "problem_use", "any_substance_3mo"]:
    CLEAN[c] = pd.to_numeric(CLEAN[c], errors="coerce")
N = len(CLEAN)
ever_yes = int((CLEAN["ever_use_c"] == "Yes").sum())
past3_yes = int((CLEAN["past_3mo_c"] == "Yes").sum())
prob_yes = int((CLEAN["problem_use"] == 1).sum())
freq_dist = CLEAN["freq_c"].value_counts().to_dict()
prim = CLEAN["primary_substance"].value_counts()
alc_n = int(prim.get("Alcohol", 0))
cod_n = int(prim.get("Codeine-containing cough syrup without a medical prescription", 0))
tob_n = int(prim.get("Tobacco/cigarettes", 0))
sed_n = int(prim.get("Sedatives/sleeping pills without a medical prescription", 0))
tra_n = int(prim.get("Tramadol or other prescription opioids without a medical prescription", 0))
can_n = int(prim.get("Cannabis/marijuana", 0))

# ---- TITLE PAGE ----
for _ in range(4): doc.add_paragraph()
p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = p.add_run("ASSESSMENT OF SUBSTANCE ABUSE AND PERCEIVED HEALTH IMPLICATIONS\nAMONG UNDERGRADUATE STUDENTS OF FUHSI"); r.font.size = Pt(16); r.bold = True; r.font.color.rgb = NAVY
doc.add_paragraph()
p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = p.add_run("Statistical Analysis Report"); r.font.size = Pt(14); r.font.color.rgb = NAVY
doc.add_paragraph()
para("Prepared for: Faculty of Allied Health Sciences, Federal University of Health Sciences, Ila-Orangun (FUHSI)", italic=True)
para("Client: Afolabi Maryam Adedeji (Matric: 22/NAH/019), Department of Nursing Science", italic=True)
para(f"Date: {pd.Timestamp.now().strftime('%B %d, %Y')}", italic=True)
doc.add_page_break()

# ---- 1. INTRODUCTION ----
h1("1. INTRODUCTION")
para("Substance abuse among undergraduate students is a growing public health concern in Nigeria and globally. "
     "This study assessed the prevalence of substance abuse, perceived factors influencing use, perceived health "
     "implications, and prevention strategies among undergraduate students of the Federal University of Health "
     "Sciences, Ila-Orangun (FUHSI). The study was guided by Problem Behaviour Theory (Jessor & Jessor) and "
     "Social Learning Theory (Bandura), which posit that substance use is influenced by a complex interplay of "
     "personal, environmental, and behavioural factors.")

# ---- 2. METHODS ----
h1("2. MATERIALS AND METHODS")
h2("2.1 Study Design, Population and Sampling")
para(f"Design: cross-sectional descriptive survey. Population: ~3,500 undergraduate students across four faculties "
     f"(Allied Health Sciences, Basic Medical Sciences, Clinical Sciences, Faculty of Sciences). "
     f"Sample size: Yamane formula at 95% CI, 5% MoE → n = 359; +10% non-response → 395 questionnaires distributed. "
     f"Proportionate stratified sampling by faculty was planned; however, data collection used Google Forms "
     f"with convenience/self-selection. All {N} distributed questionnaires were returned and consented.")

h2("2.2 Instrument")
para("A structured, self-administered questionnaire with five sections: "
     "A — Demographics (age, sex, level, faculty, religion, marital status, living arrangement, monthly allowance); "
     "B — Substance Use (ever use, past-3-month use, substance types multi-select, frequency, poly-use, "
     "CAGE-type items for problem use); "
     "C — Factors Influencing Substance Abuse (13 items, 5-point Likert SA=5…SD=1); "
     "D — Perceived Health Implications (12 items, 5-point Likert); "
     "E — Prevention & Control Strategies (8 items, 5-point Likert). "
     "Face/content validity was assessed by experts; internal consistency was evaluated with Cronbach's α.")

h2("2.3 Data Processing & Analysis")
para("Data were cleaned in Python (pandas). Substance multi-select responses (semicolon-delimited) were parsed. "
     "Frequency was coded 0=Not at all/Not applicable, 1=Less than once a week, 2=1–2 times/week, 3=3–6 times/week. "
     "Problem use was derived from CAGE-type items (should reduce, withdrawal, poly-use) — flag = 1 if any positive. "
     "Factor, Health, and Prevention scores were computed as mean of respective items. "
     "Analysis: descriptive (frequencies, percentages, means, SDs), chi-square/Fisher's exact with Cramér's V "
     "for categorical associations, Kruskal-Wallis/Mann-Whitney for group comparisons, Spearman/Pearson correlations, "
     "and logistic regression (supplementary). Significance: p < 0.05. "
     "Software: Python (pandas, scipy, statsmodels, matplotlib, seaborn, python-docx, openpyxl).")

# ---- 3. SAMPLE CHARACTERISTICS ----
h1("3. SAMPLE CHARACTERISTICS (n = {})".format(N))
add_csv_table("D01_demographics.csv", "Table 1. Demographic characteristics of respondents")
add_figure("sub_F01_sampling.png", "Figure 1. Sampling framework vs achieved sample")
add_figure("sub_F02_demographics.png", "Figure 2. Demographic distribution")

# ---- 4. SUBSTANCE USE ----
h1("4. SUBSTANCE USE PATTERNS")
para(f"Ever used any psychoactive substance (non-medical/recreational): {ever_yes} ({ever_yes/N*100:.1f}%). "
     f"Used in past 3 months: {past3_yes} ({past3_yes/N*100:.1f}%). "
     f"Problem use (CAGE-type flag): {prob_yes} ({prob_yes/N*100:.1f}%).")
add_csv_table("D02_ever_use.csv", "Table 2. Ever used any substance")
add_csv_table("D02_past_3mo.csv", "Table 3. Used substance in past 3 months")
add_csv_table("D02_problem_use.csv", "Table 4. Problem use flag (CAGE-type)")
add_figure("sub_F03_cascade.png", "Figure 3. Substance use cascade")

h2("4.1 Substances Used (Past 3 Months)")
para(f"Primary substance among past-3-month users (n={past3_yes}): Alcohol {alc_n}, "
     f"Codeine-containing cough syrup {cod_n}, Tobacco/cigarettes {tob_n}, "
     f"Sedatives/sleeping pills {sed_n}, Tramadol/opioids {tra_n}, Cannabis {can_n}.")
add_csv_table("D02_substance_specific.csv", "Table 5. Specific substances used (past 3 months)")
add_figure("sub_F04_substances.png", "Figure 4. Substances used in past 3 months")

h2("4.2 Frequency of Use")
para(f"Frequency (past 30 days, among past-3-month users): "
     f"Less than once/week {freq_dist.get(1, 0)}, "
     f"1–2 times/week {freq_dist.get(2, 0)}, "
     f"3–6 times/week {freq_dist.get(3, 0)}.")
add_csv_table("D02_frequency.csv", "Table 6. Frequency of substance use (past 30 days)")
add_figure("sub_F05_frequency.png", "Figure 5. Frequency distribution")

h2("4.3 Poly-use & CAGE-type Indicators")
add_csv_table("D02_poly_use.csv", "Table 7. Poly-substance use (past 3 months)")
add_csv_table("D02_should_reduce.csv", "Table 8. Felt should reduce/stop use")
add_csv_table("D02_withdrawal.csv", "Table 9. Withdrawal symptoms")
add_csv_table("D02_problem_use_flag.csv", "Table 10. Problem use flag (any CAGE-type positive)")
add_figure("sub_F15_problem_use.png", "Figure 15. Problem use indicators")

# ---- 5. FACTORS INFLUENCING SUBSTANCE ABUSE ----
h1("5. FACTORS INFLUENCING SUBSTANCE ABUSE (13 items, 5-point Likert)")
para("All 13 factors scored high (means 3.89–4.67/5). % Strongly Agree + Agree: "
     "Peer pressure 97.7%, Emotional distress 93.2%, Coping with pain/stress/sleep 93.2%, "
     "Limited parental monitoring 93.2%, Curiosity/experimentation 90.9%, Academic stress 90.2%, "
     "Easy availability 86.4%, Social media exposure 84.8%, Social gatherings/parties 81.1%, "
     "Family member use 81.1%, Inadequate policy enforcement 79.5%, Low self-esteem 72.7%, "
     "Boredom/unstructured time 71.2%.")
add_csv_table("D03_factors_descriptive.csv", "Table 11. Factor item descriptives (mean, SD, % SA+A)")
add_csv_table("D03_factors_sa_a.csv", "Table 12. Factors % SA+A (ranked)")
add_csv_table("D03_factor_subscales.csv", "Table 13. Factor subscales (mean, SD)")
add_figure("sub_F06_factors_ranking.png", "Figure 6. Factors % SA+A (ranked)")
add_figure("sub_F07_factors_stacked.png", "Figure 7. Factor response distribution (stacked)")

# ---- 6. PERCEIVED HEALTH IMPLICATIONS ----
h1("6. PERCEIVED HEALTH IMPLICATIONS (12 items, 5-point Likert)")
para("All 12 health implications scored very high (means 4.38–4.63/5). % SA+A ≥95.5% for all items. "
     "Top concerns: Dependence/addiction 100%, Long-term organ damage 100%, Cardiovascular problems 99.2%, "
     "Respiratory problems 99.2%, Anxiety/depression/mental health 98.5%, Academic performance 98.5%, "
     "Sleep disturbances 98.5%, Impaired concentration/memory 98.5%, Impaired judgement/decision-making 97.7%, "
     "Risky sexual behaviour 96.9%, Accidents/injuries 97.7%, Relationship problems 96.9%.")
add_csv_table("D04_health_descriptive.csv", "Table 14. Health implication item descriptives")
add_csv_table("D04_health_sa_a.csv", "Table 15. Health implications % SA+A (ranked)")
add_csv_table("D04_health_domains.csv", "Table 16. Health domains (Physical, Psychological, Academic, Social)")
add_figure("sub_F08_health_ranking.png", "Figure 8. Health implications % SA+A")
add_figure("sub_F09_health_domains.png", "Figure 9. Health domains by mean score")

# ---- 7. PREVENTION & CONTROL STRATEGIES ----
h1("7. PERCEIVED PREVENTION AND CONTROL STRATEGIES (8 items, 5-point Likert)")
para("All 8 strategies scored high (means 4.26–4.43/5). % SA+A: Counselling/mental health 97.7%, "
     "Education/awareness campaigns 97.7%, Parental/family involvement 96.2%, "
     "University policies/disciplinary measures 95.5%, Recreational/extracurricular 93.9%, "
     "Early identification/screening/referral 93.2%, Peer-led education/support 91.7%, "
     "Religious/spiritual support 88.6%.")
add_csv_table("D05_prevention_descriptive.csv", "Table 17. Prevention item descriptives")
add_csv_table("D05_prevention_sa_a.csv", "Table 18. Prevention strategies % SA+A (ranked)")
add_figure("sub_F10_prevention_ranking.png", "Figure 10. Prevention strategies % SA+A")
add_figure("sub_F10b_prevention_stacked.png", "Figure 10b. Prevention response distribution")

# ---- 8. SCALE RELIABILITY ----
h1("8. SCALE RELIABILITY")
para("All three scales show excellent internal consistency: "
     "Factors α = 0.908 (13 items, n={}), "
     "Health Implications α = 0.937 (12 items, n={}), "
     "Prevention α = 0.904 (8 items, n={}). All well above the 0.70 threshold.".format(N, N, N))
add_csv_table("D06_reliability.csv", "Table 19. Reliability statistics")

# ---- 9. BIVARIATE ASSOCIATIONS ----
h1("9. BIVARIATE ASSOCIATIONS (CHI-SQUARE / FISHER'S EXACT)")
para("Associations between ever use / past 3-month use / problem use and demographics. "
     "Significant associations (p < 0.05) are highlighted.")
add_csv_table("D07_bivariate_demographics.csv", "Table 20. Bivariate associations (ever use, past 3mo, problem use × demographics)")
add_figure("sub_F11_subgroup.png", "Figure 11. Subgroup analysis: ever use by key demographics")

# ---- 10. SCORE COMPARISONS ----
h1("10. SCORE COMPARISONS ACROSS GROUPS (KRUSKAL-WALLIS / MANN-WHITNEY)")
para("Factor, Health, and Prevention scores compared across demographic groups. "
     "Significant differences (p < 0.05) are reported.")
add_csv_table("D08_score_by_demographics.csv", "Table 21. Score comparisons by demographics")

# ---- 11. CORRELATIONS ----
h1("11. CORRELATIONS (SPEARMAN / PEARSON)")
para("Inter-scale correlations and correlations with continuous demographics (age ordinal, allowance ordinal). "
     "Key finding: Factor score ↔ Health score ρ = 0.27 (p = 0.002); "
     "Factor score ↔ Prevention score ρ = 0.30 (p < 0.001); "
     "Health score ↔ Prevention score ρ = 0.53 (p < 0.001).")
add_csv_table("D09_correlations.csv", "Table 22. Spearman correlation matrix (key scales + demographics)")
add_csv_table("D09b_spearman_matrix.csv", "Table 23. Full Spearman matrix")
add_csv_table("D09c_pearson_matrix.csv", "Table 24. Pearson correlation matrix")
add_figure("sub_F13_corr_heatmap.png", "Figure 13. Correlation heatmap")

# ---- 12. LOGISTIC REGRESSION (SUPPLEMENTARY) ----
h1("12. LOGISTIC REGRESSION — SUPPLEMENTARY")
para("Binary logistic regression for ever use, past 3-month use, and problem use. "
     "Predictors: demographics + factor/health/prevention scores. "
     "Only significant predictors (p < 0.05) are discussed.")
add_csv_table("D10_logistic_models.csv", "Table 25. Logistic regression models (supplementary)")

# ---- 13. KEY FINDINGS & RECOMMENDATIONS ----
h1("13. KEY FINDINGS AND RECOMMENDATIONS")
bullets([
    f"Prevalence: {ever_yes/N*100:.1f}% ever used, {past3_yes/N*100:.1f}% used in past 3 months, {prob_yes/N*100:.1f}% problem use.",
    "Alcohol is the most used substance (primary for {} of {} past-3-month users), followed by codeine cough syrup ({}).".format(alc_n, past3_yes, cod_n),
    f"Problem use is concentrated: {prob_yes} respondents ({prob_yes/N*100:.1f}%) flagged positive on CAGE-type indicators.",
    "Top influencing factors: Peer pressure (97.7% SA+A), Emotional distress/Coping/Parental monitoring (all 93.2% SA+A).",
    "Health implications are universally recognised: ≥95.5% SA+A for all 12 items; mean health score 4.54/5 (SD 0.41).",
    "Prevention strategies strongly endorsed: Counselling/Education 97.7% SA+A; mean prevention score 4.36/5 (SD 0.47).",
    "All scales highly reliable: Factors α=0.908, Health α=0.937, Prevention α=0.904.",
    "Bivariate: Ever use associated with Sex (p<0.001), Faculty (p=0.005), Allowance (p=0.010), Level (p=0.032). "
    "Past 3mo use associated with Sex (p=0.011), Religion (p=0.004). Problem use with Religion (p<0.001).",
    "Logistic (ever use): Male aOR=10.13 (95% CI 2.51–40.97, p=0.001); Faculty of Sciences aOR=8.29 (p=0.006); "
    "Low allowance aOR=0.06 (p=0.007). Other models: no significant predictors.",
])

h2("Recommendations (HBM-aligned)")
bullets([
    "Targeted alcohol-focused interventions (most prevalent substance, 10.4% of total sample).",
    "Peer-led education programmes — peer pressure is the #1 factor (97.7% SA+A).",
    "Integrate mental health/coping skills into curriculum — emotional distress (93.2%) and coping (93.2%) are top drivers.",
    "Strengthen campus health centre substance-use screening and brief intervention capacity.",
    "Parental engagement programmes — parental monitoring is a key factor (93.2% SA+A).",
    "Policy enforcement review — 79.5% agree inadequate enforcement influences use.",
    "Health education on specific organ damage (cardiovascular, respiratory, neurocognitive) — awareness already high (99%+), leverage for behaviour change.",
    "Early identification & referral pathways for the 5.6% with problem use indicators.",
])

# ---- 14. LIMITATIONS ----
h1("14. LIMITATIONS")
bullets([
    "Cross-sectional design — cannot infer causality.",
    "Self-reported data — subject to recall and social desirability bias.",
    "Convenience sampling via Google Forms — not strictly proportionate stratified as planned; limits generalisability.",
    "CAGE-type items adapted for student context — not a validated diagnostic tool.",
    "Effective margin of error ±4.9% (n=395) vs planned ±5%; adequate for descriptive estimates but underpowered for some subgroup logistic regressions.",
    "Frequency measure combines 'Not at all' and 'Not applicable' — cannot distinguish never-users from non-current users among ever-users.",
])

doc.add_page_break()

# ---- 15. APPENDIX ----
h1("15. APPENDIX — TABLES AND FIGURES MANIFEST")
para("The following deliverables accompany this report:", bold=True)
bullets([
    "01_Report — this document (DOCX).",
    "02_Workbook — Excel workbook with 13 sheets (README, Data Dictionary, Cleaned Data, Demographics, "
    "Substance Use, Factors, Health, Prevention, Bivariate, Correlations, Logistic, Charts_Native, Key_Findings) "
    "including 10 native Excel charts.",
    "03_Tables — 54 CSV tables (T01–T10, D01–D10, DX_*).",
    "04_Figures — 16 PNG charts (sub_F01–sub_F16).",
    "05_Data — cleaned analysis dataset (substance_abuse_cleaned_full.csv, 395 rows × 116 columns).",
])
para("All analyses are reproducible from the cleaned dataset and the Python pipeline scripts.", italic=True)

doc.save(OUT_FILE)
print("Saved:", OUT_FILE.name)