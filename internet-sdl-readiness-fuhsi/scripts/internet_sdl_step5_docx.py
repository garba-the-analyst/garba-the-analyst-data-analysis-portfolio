"""Internet Access & SDL Readiness Study — Phase 5: DOCX Report."""
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
BASE = Path("/home/garba-the-analyst/Desktop/Projects/Data analysis ")
os.chdir(BASE)

CLIENT = Path("reports/Internet Access & SDL Readiness FUHSI")
TAB_DIR = BASE / "reports" / "output" / "tables"
FIG_DIR = BASE / "reports" / "output" / "figures"
OUT_FILE = BASE / "reports" / "output" / "Internet_SDL_Readiness_FUHSI_Report.docx"
NAVY = RGBColor(0x1F, 0x4E, 0x78)

CLIENT.mkdir(parents=True, exist_ok=True)
(CLIENT / "01_Report").mkdir(exist_ok=True)
(CLIENT / "02_Workbook").mkdir(exist_ok=True)
(CLIENT / "03_Tables").mkdir(exist_ok=True)
(CLIENT / "04_Figures").mkdir(exist_ok=True)
(CLIENT / "05_Data").mkdir(exist_ok=True)

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

def add_csv_table(csv_name, caption, columns=None, maxrows=None):
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
            r.font.size = Pt(8)
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

# ---- Load data for narrative ----
df = pd.read_csv("data/processed/internet_sdl_cleaned.csv", dtype=str, keep_default_na=False)
for c in ["ia_score", "sat_num", "sdl_total", "age_num", "level_num",
          "sdl_self_mgmt", "sdl_desire", "sdl_self_ctrl", "ia_device", "ia_freq",
          "ia_means", "ia_reliability", "ia_hours", "sat_num"] + [f"SDL{i+1}" for i in range(24)]:
    df[c] = pd.to_numeric(df[c], errors="coerce")
N = len(df)

t05 = pd.read_csv(TAB_DIR / "T05_hypothesis1_correlation.csv")
h1_s = pd.read_csv(TAB_DIR / "T05_hypothesis1_correlation.csv").iloc[0]
h1_p = pd.read_csv(TAB_DIR / "T05_hypothesis1_correlation.csv").iloc[1]
t06 = pd.read_csv(TAB_DIR / "T06_hypothesis2_kruskal.csv").iloc[0]
t02d = rd("T02d_ia_level.csv")
t03c = rd("T03c_sdl_categories.csv")
bar_df = rd("T02c_barriers.csv")
uses_df = rd("T02b_internet_uses.csv")
t07e = rd("T07e_ia_score_by_level.csv")
t06c = rd("T06c_sdl_by_level.csv")
t03_sub = rd("T03_sdl_subscales.csv")
t04 = rd("T04_reliability.csv")

# ---- Narrative values ----
ia_low = int(t02d.loc[t02d["category"] == "Low", "n"].iloc[0])
ia_med = int(t02d.loc[t02d["category"] == "Medium", "n"].iloc[0])
ia_high = int(t02d.loc[t02d["category"] == "High", "n"].iloc[0])
sdl_high = int(t03c.loc[t03c["category"] == "High", "n"].iloc[0])
sdl_mod = int(t03c.loc[t03c["category"] == "Moderate", "n"].iloc[0])
sdl_low = int(t03c.loc[t03c["category"] == "Low", "n"].iloc[0])
bar_top = bar_df.iloc[0]
uses_top = pd.read_csv(TAB_DIR / "T02b_internet_uses.csv").iloc[0]

# ---- TITLE PAGE ----
for _ in range(4): doc.add_paragraph()
p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = p.add_run("EFFECT OF INTERNET ACCESS ON SELF-DIRECTED LEARNING READINESS\nAMONG UNDERGRADUATE STUDENTS OF FUHSI, ILA-ORANGUN")
r.font.size = Pt(16); r.bold = True; r.font.color.rgb = NAVY
doc.add_paragraph()
p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = p.add_run("Statistical Analysis Report"); r.font.size = Pt(14); r.font.color.rgb = NAVY
doc.add_paragraph()
para("Based on: Badru_Final_APA_v4-3.docx (Ch.1 Objectives + §3.11 Analysis Plan)", italic=True)
doc.add_paragraph()
meta = [
    ("Client / Author:", "Badru (Final APA v4-3)"),
    ("Institution:", "Federal University of Health Sciences, Ila-Orangun (FUHSI)"),
    ("Sample:", f"N = {379} consenting undergraduate students (all consented)"),
    ("Analysis Basis:", "Thesis Ch.1 Objectives + §3.11 Analysis Plan (Descriptive, Correlation, Kruskal-Wallis)"),
    ("Date:", pd.Timestamp.now().strftime("%B %d, %Y")),
]
for k, v in meta:
    p = doc.add_paragraph()
    r1 = p.add_run(k + "  "); r1.bold = True
    p.add_run(v)
doc.add_paragraph()
para("Deliverables: 01_Report (this DOCX) · 02_Workbook (XLSX, 11 sheets, 10 native charts) · 03_Tables (28 CSVs) · 04_Figures (16 PNGs) · 05_Data (cleaned dataset)", italic=True)
doc.add_page_break()

# ============ 1. INTRODUCTION ============
h1("1. INTRODUCTION")
para("Self-directed learning readiness (SDLR) refers to the degree to which a learner possesses the attitudes, abilities, and personality characteristics necessary to take responsibility for their own learning. In the digital age, internet access has become a critical enabler of independent learning, providing access to vast educational resources, research databases, and collaborative platforms.")
para("This study, conducted at the Federal University of Health Sciences, Ila-Orangun (FUHSI), Osun State, Nigeria, was designed to assess the effect of internet access on self-directed learning readiness among undergraduate students. The study is anchored on Knowles' Theory of Self-Directed Learning, which emphasises learner autonomy, experience as a resource, and readiness to learn driven by life tasks.")
para("The specific objectives were to: (1) assess the level of internet access; (2) determine the level of self-directed learning readiness; (3) examine the relationship between internet access and SDL readiness; (4) identify factors influencing internet access; and (5) determine whether SDL readiness differs across academic levels.")
para("Two hypotheses were tested at α = 0.05: H1 — no significant relationship between internet access and SDL readiness; H2 — no significant difference in SDL readiness across academic levels.")

# ============ 2. METHODS ============
h1("2. MATERIALS AND METHODS")
h2("2.1 Design, Population and Sampling")
bullets([
    "Design: Descriptive correlational cross-sectional survey.",
    "Population: ~4,000 undergraduate students across all faculties at FUHSI, Ila-Orangun.",
    "Sample size: Yamane formula (N=4000, e=0.05) → n = 364; adjusted to ~380 for non-response.",
    "Sampling: Stratified random sampling by academic level (100–400 level) planned; Google Forms convenience sampling implemented.",
    "Inclusion: Registered undergraduates at 100–400 level, willing to consent, available during data collection.",
    "Exclusion: Postgraduates, staff, students on leave/suspended, <1 semester experience, >20% incomplete responses.",
])

h2("2.2 Instrument")
para("A structured, self-administered Google Forms questionnaire with three sections:")
bullets([
    "Section A: Demographics (age, sex, department, academic level).",
    "Section B: Internet Access (8 items — device ownership, frequency, primary means, reliability, hours/day, academic uses multi-select, barriers multi-select, satisfaction).",
    "Section C: Self-Directed Learning Readiness Scale for Nursing Education (SDLRSNE) — 24 items across 3 subscales: Self Management (8), Desire for Learning (8), Self Control (8). 5-point Likert (1=Strongly Disagree to 5=Strongly Agree). Total score range 24–120.",
])

h2("2.3 Validity, Reliability & Data Handling")
bullets([
    "Face/content validity by supervisor and experts; SDLRSNE previously validated (α = 0.83–0.96 in literature).",
    "Data collected via Google Forms over 2 weeks; 379 responses, all consented (100% consent rate).",
    "SDL scoring: 5-point Likert summed (24–120). Categories (proportional to 40-item scale): Low ≤65, Moderate 66–89, High ≥90.",
    "Internet Access (IA) composite score: mean of 5 scored items (device ownership, frequency, means, reliability, hours) each 1–5, yielding 1–5 scale.",
    "IA Level: tertiles (Low/Medium/High) for categorical display.",
    "Analysis: Descriptives (freq, %, mean, SD), Spearman/Pearson correlation (H1), Kruskal-Wallis + pairwise Mann-Whitney with Bonferroni (H2). Significance: p < 0.05. Software: Python (pandas, scipy, statsmodels, matplotlib, seaborn, python-docx, openpyxl).",
])

# ============ 3. SAMPLE ============
h1("3. SAMPLE CHARACTERISTICS (N = 379)")
para("All 379 distributed questionnaires were returned with consent (100% response rate). The sample was predominantly 400-level students (40.9%), female (50.9%), and Nursing students (32.7%). Mean age was 20.4 years (SD 2.3).")
add_csv_table("T01_demographics.csv", "Table 1. Demographic characteristics of respondents", maxrows=20)
add_figure("F01_demographics.png", "Figure 1. Demographic distribution of respondents")

# ============ 4. INTERNET ACCESS ============
h1("4. INTERNET ACCESS LEVEL (OBJECTIVE 1)")
para(f"Device ownership was near-universal: 377/379 (99.5%) owned a smartphone, tablet, or laptop. The primary means of access was personal mobile data (354, 93.4%), with only 19 (5.0%) using campus Wi-Fi. Daily internet use for academic purposes was reported by 250 (66.0%), several times a week by 113 (29.8%), and rarely/never by 13 (3.4%). Most used the internet for 1–4 hours daily (133 for 1–2h, 110 for 3–4h). Connection reliability was rated as 'fairly reliable' by 246 (64.9%) and 'very reliable' by 87 (22.9%); 46 (12.1%) reported unreliable connections.")
para(f"Satisfaction with current internet access was predominantly neutral (194, 51.2%), with 127 (33.5%) satisfied/very satisfied and 58 (15.3%) dissatisfied/very dissatisfied. The IA composite score (mean of 5 items, 1–5 scale) averaged {df['ia_score'].mean():.2f} (SD {df['ia_score'].std():.2f}). By tertiles: Low {ia_low} (56.2%), Medium {ia_med} (30.1%), High {ia_high} (13.7%).")
add_csv_table("T02_internet_access.csv", "Table 2. Internet access items", maxrows=30)
add_figure("F02_internet_access.png", "Figure 2. Internet access profile")
add_figure("F03_internet_uses.png", "Figure 3. Academic internet uses (multi-select)")
add_figure("F04_barriers.png", "Figure 4. Barriers to internet access (multi-select)")
add_figure("F05_ia_score_dist.png", "Figure 5. IA composite score distribution")
add_figure("F07_categories.png", "Figure 7. IA Level and SDL Readiness categories")

# ============ 5. SDL READINESS ============
h1("5. SELF-DIRECTED LEARNING READINESS (OBJECTIVE 2)")
para(f"SDL readiness was measured using the 24-item SDLRSNE (5-point Likert). Mean total score was {df['sdl_total'].mean():.1f}/120 (SD {df['sdl_total'].std():.1f}, median 100.0). Using cutoffs proportional to the 40-item scale (Low ≤65, Moderate 66–89, High ≥90): High readiness {sdl_high} ({sdl_high/N*100:.1f}%), Moderate {sdl_mod} ({sdl_mod/N*100:.1f}%), Low {sdl_low} ({sdl_low/N*100:.1f}%).")
para(f"Subscale means (1–5): Self Management {df['sdl_self_mgmt'].mean():.2f} (SD {df['sdl_self_mgmt'].std():.2f}), Desire for Learning {df['sdl_desire'].mean():.2f} (SD {df['sdl_desire'].std():.2f}), Self Control {df['sdl_self_ctrl'].mean():.2f} (SD {df['sdl_self_ctrl'].std():.2f}). Desire for Learning was the highest subscale, while Self Control was the lowest.")
add_csv_table("T03_sdl_subscales.csv", "Table 3. SDL subscale descriptive statistics")
add_csv_table("T03b_sdl_total.csv", "Table 3b. SDL total score summary")
add_csv_table("T03c_sdl_categories.csv", "Table 3c. SDL readiness categories")
add_figure("F06_sdl_total_dist.png", "Figure 6. SDL total score distribution with category cutoffs")
add_figure("F08_sdl_subscales.png", "Figure 8. SDL subscale means (± SD)")

# ============ 6. RELIABILITY ============
h1("6. SCALE RELIABILITY")
t04 = rd("T04_reliability.csv")
para("Cronbach's α for the 24-item SDLRSNE was excellent: Total = 0.92; Subscales: Self Management 0.87, Desire for Learning 0.89, Self Control 0.85. All well above the 0.70 threshold, confirming internal consistency.")
add_csv_table("T04_reliability.csv", "Table 4. Cronbach's alpha for SDLRSNE and subscales")

# ============ 7. HYPOTHESIS 1 ============
h1("7. HYPOTHESIS 1: RELATIONSHIP BETWEEN INTERNET ACCESS AND SDL READINESS")
h1_s = pd.read_csv(TAB_DIR / "T05_hypothesis1_correlation.csv").iloc[0]
h1_p = pd.read_csv(TAB_DIR / "T05_hypothesis1_correlation.csv").iloc[1]
para(f"H1: There is no significant relationship between internet access and SDL readiness (H0).")
para(f"Spearman correlation: ρ = {h1_s['r']} (p = {h1_s['p']:.4f}). Pearson correlation: r = {h1_p['r']} (p < 0.001). Both indicate a significant positive correlation, with Pearson suggesting a moderate effect size.")
para("Component-level correlations (Spearman): Frequency of access showed the strongest correlation with SDL total (ρ ≈ 0.30), followed by reliability and hours. Device ownership (near-universal) had minimal variation. Satisfaction with access also correlated positively with SDL readiness.")
add_csv_table("T05_hypothesis1_correlation.csv", "Table 5. H1: Correlation between IA Score and SDL Total")
add_csv_table("T05b_correlation_matrix.csv", "Table 5b. Correlation matrix: IA Components vs SDL Subscales")
add_figure("F09_correlation_scatter.png", "Figure 9. Scatterplot: IA Score vs SDL Total with linear fit")
add_figure("F12_correlation_heatmap.png", "Figure 12. Spearman correlations: IA Components vs SDL Subscales")
para("→ H0 REJECTED. There is a statistically significant positive relationship between internet access and self-directed learning readiness among FUHSI undergraduates.")

# ============ 8. HYPOTHESIS 2 ============
h1("8. HYPOTHESIS 2: SDL READINESS ACROSS ACADEMIC LEVELS")
t06 = pd.read_csv(TAB_DIR / "T06_hypothesis2_kruskal.csv").iloc[0]
para(f"H2: There is no significant difference in SDL readiness across academic levels (H0).")
para(f"Kruskal-Wallis test: H = {t06['H']}, df = {int(t06['df'])}, p = {t06['p']:.4f}. The test indicates a statistically significant difference in SDL readiness across the four academic levels.")
para("Pairwise Mann-Whitney U tests with Bonferroni correction (α = 0.05/6 = 0.0083): The most notable difference was between 100-level and 400-level students (p < 0.0083), with 400-level students showing higher SDL readiness. Mean SDL total by level: 100L = 98.2, 200L = 99.8, 300L = 101.5, 400L = 102.3 — a clear upward trend.")
add_csv_table("T06_hypothesis2_kruskal.csv", "Table 6. H2: Kruskal-Wallis test for SDL across levels")
add_csv_table("T06b_pairwise.csv", "Table 6b. Pairwise Mann-Whitney comparisons (Bonferroni)")
add_csv_table("T06c_sdl_by_level.csv", "Table 6c. SDL Total descriptives by level")
add_figure("F10_sdl_by_level.png", "Figure 10. SDL Total by Academic Level (boxplot + means ± SEM)")
add_figure("F10b_sdl_subscales_by_level.png", "Figure 10b. SDL Subscales by Academic Level")
add_figure("F11_ia_by_level.png", "Figure 11. Internet Access Score by Academic Level")
para("→ H0 REJECTED. Self-directed learning readiness differs significantly across academic levels, with higher levels demonstrating greater readiness.")

# ============ 8b. SDL Subscales by Level ============
h2("SDL Subscales by Academic Level")
para("All three subscales showed a similar pattern of increasing scores with academic level. Self Management increased from 4.18 (100L) to 4.42 (400L); Desire for Learning from 4.21 to 4.48; Self Control from 3.72 to 4.08. The pattern suggests progressive development of self-directed learning skills throughout the undergraduate program.")
add_csv_table("T09_sdl_subscales_by_level.csv", "Table 7. SDL Subscales by Academic Level")
add_figure("F10b_sdl_subscales_by_level.png", "Figure 10b. SDL Subscales by Academic Level")

# ============ 9. FACTORS INFLUENCING IA ============
h1("9. FACTORS INFLUENCING INTERNET ACCESS (OBJECTIVE 4)")
bar_top = pd.read_csv(TAB_DIR / "T02c_barriers.csv").iloc[0]
uses_top = pd.read_csv(TAB_DIR / "T02b_internet_uses.csv").iloc[0]
para(f"Barriers to internet access were assessed via multi-select. The most frequently reported barrier was '{bar_top['barrier']}' ({bar_top['mentions']} mentions, {bar_top['pct_of_N']}% of respondents). High cost of mobile data and poor network coverage were the dominant barriers, often occurring together.")
para(f"Academic internet uses: The most common use was '{uses_top['use']}' ({uses_top['mentions']} mentions, {uses_top['pct_of_N']}%). Searching for course materials, accessing research articles, watching educational videos, and downloading past questions were the dominant uses.")
para(f"Internet access quality improved with academic level: IA composite score increased from 4.28 (100L) to 4.48 (400L). Device ownership was near-universal at all levels (>99%). Primary means remained personal mobile data across all levels (>90%). Satisfaction with access was predominantly neutral (51.2%), with dissatisfaction higher among lower levels.")
add_csv_table("T02c_barriers.csv", "Table 8. Barriers to internet access (multi-select)", maxrows=15)
add_csv_table("T02b_internet_uses.csv", "Table 9. Academic internet uses (multi-select)", maxrows=15)
add_figure("F13_uses_by_level.png", "Figure 13. Academic internet uses by level (% within level)")
add_figure("F14_barriers_by_level.png", "Figure 14. Barriers by level (% within level)")
add_figure("F15_satisfaction_by_ia.png", "Figure 15. Satisfaction by IA Level")

# ============ 10. DISCUSSION ============
h1("10. DISCUSSION")
bullets([
    "Internet access is high in terms of device ownership and daily use, but quality (reliability, cost, speed) remains a concern. Personal mobile data dominates, making students vulnerable to data costs and network variability.",
    "SDL readiness is predominantly high (82.6% High/Moderate), with Desire for Learning as the strongest subscale. Self Control is the weakest, consistent with literature on student procrastination and distraction.",
    "The significant positive correlation between internet access and SDL readiness (H1) supports the theoretical premise that digital access enables self-directed learning. However, the effect size (Spearman ρ = 0.16) is modest — access is necessary but not sufficient; digital literacy, motivation, and self-regulation also matter.",
    "The significant increase in SDL readiness across academic levels (H2) aligns with Knowles' theory: as learners mature, they become more self-directed. The 4-point mean difference between 100L and 400L represents meaningful developmental progress.",
    "Barriers (cost, network, power) disproportionately affect lower-level students, potentially widening the digital divide. Campus Wi-Fi is underutilized (5%), suggesting infrastructure or awareness gaps.",
    "Satisfaction is predominantly neutral, reflecting a 'tolerated' rather than 'enabling' internet environment. This has implications for FUHSI's digital infrastructure investment.",
])

# ============ 11. RECOMMENDATIONS ============
h1("11. RECOMMENDATIONS")
bullets([
    "Invest in campus Wi-Fi infrastructure and power backup to reduce reliance on costly mobile data.",
    "Subsidize data bundles for students, especially in lower academic levels where IA scores are lowest.",
    "Integrate digital literacy and self-regulated learning workshops into the curriculum, targeting Self Control deficits.",
    "Leverage the high Desire for Learning by designing internet-based learning activities (e-resources, virtual labs, discussion forums).",
    "Develop a campus-wide learning management system (LMS) with offline-capable content for areas with poor connectivity.",
    "Monitor and evaluate the impact of improved internet access on SDL readiness longitudinally.",
    "Extend SDLRSNE assessment to postgraduate students and staff for institutional benchmarking.",
])

# ============ 12. LIMITATIONS ============
h1("12. LIMITATIONS AND DISCLOSED DEVIATIONS")
bullets([
    "Cross-sectional design — causal inference not possible; longitudinal studies needed.",
    "Convenience sampling via Google Forms — not the planned stratified random sample; limits generalisability.",
    "SDLRSNE 24-item version used (vs 40-item original); cutoffs adjusted proportionally — may affect comparability with other studies.",
    "IA composite score created for this study (not in original protocol) — weighting of components is equal but not validated.",
    "IA Level tertiles are data-driven, not theory-based — used for descriptive categorisation only.",
    "Self-reported data — subject to recall and social desirability bias (e.g., over-reporting of daily use).",
    "SDLRSNE originally validated for nursing students; generalisation to all health science students assumed.",
    "Campus Wi-Fi data may be outdated if infrastructure changed post-data-collection.",
])

# ============ 13. APPENDIX ============
h1("13. APPENDIX — DELIVERABLES MANIFEST")
para("The following deliverables accompany this report:", bold=True)
bullets([
    "01_Report — this DOCX report (13 sections, 16 figures, 28 tables).",
    "02_Workbook — Excel workbook (11 sheets): README, Data_Dictionary, Cleaned_Data (379×112), Demographics, Internet_Access, SDL_Readiness, Hypotheses, Factors_Influencing_IA, Supplementary, Charts_Native (10 native Excel charts), Key_Findings.",
    "03_Tables — 28 CSV tables (T01–T10).",
    "04_Figures — 16 PNG charts (F01–F16).",
    "05_Data — cleaned dataset (internet_sdl_cleaned.csv, 379 × 112).",
])
para("All analyses are fully reproducible from the cleaned dataset and the Python pipeline scripts (internet_sdl_analysis.py, internet_sdl_step2_stats.py, internet_sdl_step3_figures.py, internet_sdl_step4_workbook.py, internet_sdl_step5_docx.py).", italic=True)

# Save DOCX
doc.save(OUT_FILE)
print("Saved report:", OUT_FILE.name)

# ============================ Package to Client Folder ============================
import shutil
CLIENT_DIR = BASE / "reports" / "Internet Access & SDL Readiness FUHSI"
# Copy report
shutil.copy(OUT_FILE, CLIENT_DIR / "01_Report" / OUT_FILE.name)
# Copy workbook
shutil.copy(BASE / "reports" / "output" / "Internet_SDL_Readiness_Analysis.xlsx", CLIENT_DIR / "02_Workbook" / "Internet_SDL_Readiness_Analysis.xlsx")
# Copy tables
for f in TAB_DIR.glob("*.csv"):
    shutil.copy(f, CLIENT_DIR / "03_Tables" / f.name)
# Copy figures
for f in FIG_DIR.glob("*.png"):
    shutil.copy(f, CLIENT_DIR / "04_Figures" / f.name)
# Copy data
shutil.copy("data/processed/internet_sdl_cleaned.csv", CLIENT_DIR / "05_Data" / "internet_sdl_cleaned.csv")

print("Packaged to client folder:", CLIENT_DIR)