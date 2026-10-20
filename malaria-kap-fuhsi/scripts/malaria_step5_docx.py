"""Malaria Prevention KAP Study — Phase 5: DOCX Report."""
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

CLIENT = Path("reports/Assessment of Knowledge and Practice of Malaria Prevention among Undergraduate Students of FUHSI (Q-MPKP)")
TAB_DIR = BASE / "reports" / "output" / "tables"
FIG_DIR = BASE / "reports" / "output" / "figures"
OUT_FILE = BASE / "reports" / "output" / "Malaria_KAP_FUHSI_Report.docx"
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
CLEAN = BASE / "data" / "processed" / "malaria_kap_cleaned.csv"
df = pd.read_csv(CLEAN, dtype=str, keep_default_na=False)
for c in ["know_score", "know_pct", "prac_score", "mis_score", "gap_score",
          "level_num", "age_ord"] + [f"K{i+1}" for i in range(10)] + \
           [f"P{i+1}" for i in range(8)] + [f"M{i+1}" for i in range(8)]:
    df[c] = pd.to_numeric(df[c], errors="coerce")
N = len(df)

# Runtime narrative values
t07 = rd("T07_hypothesis1_chi2.csv")
h1_fixed = t07[t07["test"] == "H1 Primary"].iloc[0]
t07c = rd("T07b_correlation_continuous.csv")
h1_s = t07c[t07c["test"] == "Spearman"].iloc[0]
h1_p = t07c[t07c["test"] == "Pearson"].iloc[0]
t08 = rd("T08_kruskal_level.csv")
k_level = t08[t08["variable"] == "Knowledge"].iloc[0]
p_level = t08[t08["variable"] == "Practice"].iloc[0]
t01 = rd("T01_demographics.csv")
t02 = rd("T02_knowledge_items.csv")
t03 = rd("T03_practice_items.csv")
t04 = rd("T04_misconceptions.csv")
t05 = rd("T05_training_experience.csv")

# Key counts
good_fixed = int((df['know_cat_fixed']=='Good (≥8)').sum())
mod_fixed = int((df['know_cat_fixed']=='Moderate (5-7)').sum())
poor_fixed = int((df['know_cat_fixed']=='Poor (<5)').sum())
prac_good_fixed = int((df['prac_cat_fixed']=='Good (≥30)').sum())
prac_mod_fixed = int((df['prac_cat_fixed']=='Moderate (18-29)').sum())
prac_poor_fixed = int((df['prac_cat_fixed']=='Poor (<18)').sum())
itn_yes = int((df['itn_own_c']=='Yes').sum())
itn_pct = itn_yes / N * 100
src_school = int((df['source_c']=='School/Course').sum())
src_hw = int((df['source_c']=='Health worker/Clinic').sum())

def _alpha(dfx, cols):
    m = dfx[cols].apply(pd.to_numeric, errors="coerce").dropna()
    k = m.shape[1]
    return k / (k - 1) * (1 - m.var(axis=0, ddof=1).sum() / m.sum(axis=1).var(ddof=1))

kr_alpha_k = _alpha(df, [f"K{i+1}" for i in range(10)])
kr_alpha_p = _alpha(df, [f"P{i+1}" for i in range(8)])
kr_alpha_m = _alpha(df, [f"M{i+1}" for i in range(8)])

net_purchase = df["net_purchase_c"].str.strip().value_counts()
np_likely = int(net_purchase.get("Likely", 0)) + int(net_purchase.get("Very Likely", 0))
np_unlikely = int(net_purchase.get("Unlikely", 0)) + int(net_purchase.get("Very Unlikely", 0))
sanit_will = int((df["sanit_c"].isin(["Willing", "Very Willing"])).sum())
talk_likely = int((df["talk_c"].isin(["Likely", "Very Likely"])).sum())
treat24_likely = int((df["treat24_c"].isin(["Likely", "Very Likely"])).sum())
comfort_uncomf = int((df["comfort_c"].isin(["Uncomfortable", "Very Uncomfortable"])).sum())
comfort_comf = int((df["comfort_c"].isin(["Comfortable", "Very Comfortable"])).sum())
access_easy = int((df["access_c"].isin(["Easy", "Very Easy"])).sum())
access_diff = int((df["access_c"].isin(["Difficult", "Very Difficult"])).sum())

# Per-level means (computed, not hardcoded)
km_by_level = df.groupby("level_c")["know_score"].mean()
pm_by_level = df.groupby("level_c")["prac_score"].mean()
mm_by_level = df.groupby("level_c")["mis_score"].mean()
lev_l = {l: km_by_level[l] for l in ["100 Level", "200 Level", "300 Level", "400 Level"]}

# ============ TITLE PAGE ============
for _ in range(4): doc.add_paragraph()
p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = p.add_run("ASSESSMENT OF KNOWLEDGE AND PRACTICE OF MALARIA PREVENTION\nAMONG UNDERGRADUATE STUDENTS OF FUHSI, ILA-ORANGUN, OSUN STATE")
r.font.size = Pt(16); r.bold = True; r.font.color.rgb = NAVY
doc.add_paragraph()
p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = p.add_run("Statistical Analysis Report"); r.font.size = Pt(14); r.bold = True; r.font.color.rgb = NAVY
doc.add_paragraph()
para("Based on: YUSUF_KHADIJAT_Malaria_Prevention_KAP_FUHSI_REVISED.docx (Ch.1 Objectives + §3.10 Analysis Plan)", italic=True)
doc.add_paragraph()
meta = [
    ("Client / Author:", "Yusuf Khadijat Opeyemi, Department of Nursing Science"),
    ("Institution:", "Federal University of Health Sciences, Ila-Orangun (FUHSI)"),
    ("Sample:", f"N = {N} consenting undergraduate students (100% consent rate)"),
    ("Analysis Basis:", "Thesis Ch.1 Objectives + §3.10 Analysis Plan (Descriptive, Chi-square, Kruskal-Wallis, Correlation)"),
    ("Theoretical Framework:", "Orem's Self-Care Deficit Nursing Theory"),
    ("Date of Analysis:", pd.Timestamp.now().strftime("%B %d, %Y")),
]
for k, v in meta:
    p = doc.add_paragraph()
    r1 = p.add_run(k + "  "); r1.bold = True
    p.add_run(v)
doc.add_paragraph()
para("Deliverables: 01_Report (this DOCX) · 02_Workbook (XLSX, 12 sheets, 10 native charts) · 03_Tables (21 CSVs) · 04_Figures (16 PNGs) · 05_Data (cleaned dataset)", italic=True)
doc.add_page_break()

# ============ 1. INTRODUCTION ============
h1("1. INTRODUCTION")
para("Malaria remains one of the most persistent and devastating infectious diseases confronting public health systems in tropical and sub-tropical regions. According to the WHO World Malaria Report 2025, an estimated 282 million cases and 610,000 deaths occurred globally, with Nigeria bearing a disproportionate burden.")
para("Undergraduate students in Nigerian tertiary institutions represent a vulnerable population segment. Many reside in hostel accommodation or off-campus housing with poor screening, inadequate drainage, and proximity to mosquito breeding sites. Despite high malaria knowledge in some studies, a persistent knowledge-practice gap has been documented across Nigerian universities.")
para("This study, grounded in Dorothea Orem's Self-Care Deficit Nursing Theory, assessed the knowledge and practice of malaria prevention among undergraduate students of FUHSI, Ila-Orangun. The theory posits that self-care is a deliberate, learned behaviour, and that self-care agency (knowledge + ability) must meet therapeutic self-care demand (preventive actions). A deficit arises when knowledge or practice is insufficient, increasing malaria risk.")
para("Specific objectives: (1) Knowledge level, (2) Practice level, (3) Knowledge-practice relationship, (4) Information sources, (5) Differences by level/department. Hypothesis: No significant relationship between knowledge and practice (H0).")

# ============ 2. METHODS ============
h1("2. MATERIALS AND METHODS")
h2("2.1 Design, Population and Sampling")
bullets([
    "Design: Descriptive cross-sectional survey (descriptive for levels, correlational for knowledge-practice relationship).",
    "Population: ~1,500 undergraduate students across 100–400 levels at FUHSI, Ila-Orangun.",
    "Sample size: Yamane formula (N=1500, e=0.05) → n = 316; adjusted to ~330. Achieved N = 321 (all consented).",
    "Sampling: Stratified random sampling by level (strata: 100–400) as planned in §3.5; recruitment was executed online via Google Forms, so the realized distribution (100L=76, 200L=48, 300L=81, 400L=116) is convenience-like rather than strictly proportional (see Limitations).",
    "Inclusion: Registered undergraduates 100–400 level, consenting, available during data collection.",
    "Exclusion: Non-consenting, postgraduates, staff, >20% incomplete responses.",
])

h2("2.2 Instrument")
para("Structured self-administered questionnaire (Google Forms) with sections:")
bullets([
    "A: Demographics (age, sex, department, level, residence).",
    "B: Knowledge (10 MCQs — cause, vector, transmission, symptoms, ITN, IRS, sanitation, treatment-seeking, immunity, ITN maintenance).",
    "C: Practice (8 frequency items, 5-pt Likert: Always=5 to Never=1).",
    "D: Misconceptions (8 agreement items, 4-pt Likert, reverse-scored).",
    "E: Training/Experience (training, source, diagnosis, ITN ownership, access rating).",
    "F: Barriers/Intent (comfort, 24h treatment, sanitation, health talk).",
])

h2("2.3 Scoring & Analysis")
bullets([
    "Knowledge: 1 point per correct answer (0-10). Categorised: Fixed (Good≥8, Moderate 5-7, Poor<5) + Median split (Good/Poor).",
    "Practice: 5-pt Likert summed (8-40). Categorised: Fixed (Good≥30, Moderate 18-29, Poor<18) + Median split.",
    "Misconceptions: Reverse-coded (SD=5..SA=1); higher = fewer misconceptions (8-40).",
    "Hypothesis 1: Chi-square (categories) + Spearman/Pearson (continuous).",
    "Hypothesis 2: Kruskal-Wallis (non-parametric) across levels + pairwise Mann-Whitney (Bonferroni).",
    "Supplementary: Misconceptions, Gap score, Logistic regressions (labelled).",
    f"Reliability (internal consistency, computed separately): Knowledge (dichotomous items, KR-20) α = {(kr_alpha_k):.2f}; Practice α = {kr_alpha_p:.2f}; Misconceptions α = {kr_alpha_m:.2f}.",
    "Software: Python (pandas, scipy, statsmodels, matplotlib, seaborn, python-docx, openpyxl).",
])

# ============ 3. SAMPLE ============
h1("3. SAMPLE CHARACTERISTICS (N = {})".format(N))
para(f"All {N} distributed questionnaires were returned with consent (100%). Mean age: 16–20 years (61.4%), 21–25 (32.7%), 26–30 (5.9%). Female 172 (53.6%), Male 149 (46.4%). Level distribution: 400L 116 (36.1%), 300L 81 (25.2%), 100L 76 (23.7%), 200L 48 (15.0%). Residence: Off-campus 272 (84.7%), On-campus 37 (11.5%), Family 12 (3.7%).")
add_csv_table("T01_demographics.csv", "Table 1. Demographic characteristics of respondents", maxrows=20)
add_figure("F01_demographics.png", "Figure 1. Demographic distribution")

# ============ 4. KNOWLEDGE ============
h1("4. KNOWLEDGE OF MALARIA PREVENTION (OBJECTIVE 1)")
para(f"Mean knowledge score: {df['know_score'].mean():.2f}/10 (SD {df['know_score'].std():.2f}, median 9.0). Fixed categorisation: Good {good_fixed} ({good_fixed/N*100:.1f}%), Moderate {mod_fixed} ({mod_fixed/N*100:.1f}%), Poor {poor_fixed} ({poor_fixed/N*100:.1f}%). Median split: Good {int((df['know_cat_median']=='Good (≥median)').sum())}, Poor {int((df['know_cat_median']=='Poor (<median)').sum())}.")
para("Item-level performance (Table 2): Highest — 'Transmission by Anopheles bite' (90.3%), 'Fever/chills/headache' (100%), 'ITN most effective' (98.1%), 'IRS proven method' (100%). Lowest — 'ITN maintenance' (72.0%), 'Environmental sanitation mechanism' (81.9%), 'Prompt treatment-seeking' (75.7%).")
add_csv_table("T02_knowledge_items.csv", "Table 2. Knowledge items — % correct", maxrows=12)
add_csv_table("T02b_knowledge_summary.csv", "Table 2b. Knowledge score summary & categorisation")
add_figure("F02_knowledge_items.png", "Figure 2. Knowledge items — % correct", width=6.2)
add_figure("F04_knowledge_scores.png", "Figure 4. Knowledge score distribution")

# ============ 5. PRACTICE ============
h1("5. PRACTICE OF MALARIA PREVENTION (OBJECTIVE 2)")
para(f"Mean practice score: {df['prac_score'].mean():.2f}/40 (SD {df['prac_score'].std():.2f}, median 29.0). Fixed categorisation: Good {prac_good_fixed} ({prac_good_fixed/N*100:.1f}%), Moderate {prac_mod_fixed} ({prac_mod_fixed/N*100:.1f}%), Poor {prac_poor_fixed} ({prac_poor_fixed/N*100:.1f}%). Median split: Good {int((df['prac_cat_median']=='Good (≥median)').sum())}, Poor {int((df['prac_cat_median']=='Poor (<median)').sum())}.")
para("Item patterns (Table 3, Figure 3): Most consistent — 'Screen/close windows' (Always 63.2%), 'Dispose refuse' (Always 59.2%). Least — 'ITN every night' (Always 5.3%, Sometimes 40.8%), 'Long sleeves' (Always 20.6%, Never 13.4%).")
add_csv_table("T03_practice_items.csv", "Table 3. Practice items — frequency distribution", maxrows=12)
add_csv_table("T03b_practice_summary.csv", "Table 3b. Practice score summary & categorisation")
add_figure("F03_practice_items.png", "Figure 3. Practice items — frequency distribution", width=6.4)
add_figure("F05_practice_scores.png", "Figure 5. Practice score distribution")

# ============ 6. MISCONCEPTIONS ============
h1("6. MISCONCEPTIONS ABOUT MALARIA (OBJECTIVE 1 — Separate Subscale)")
para(f"Mean misconception score: {df['mis_score'].mean():.2f}/40 (SD {df['mis_score'].std():.2f}); higher = fewer misconceptions. All 8 statements are false; disagreement indicates correct understanding.")
t04["agreement_pct"] = t04["SA_pct"] + t04["A_pct"]
mis_most = t04.nlargest(1, "agreement_pct").iloc[0]
mis_best = t04.nsmallest(1, "agreement_pct").iloc[0]
para(f"Agreement with the false statements was uniformly low (SA+A range {t04['SA_pct'].add(t04['A_pct']).min():.1f}%–{t04['SA_pct'].add(t04['A_pct']).max():.1f}%): respondents overwhelmingly disagreed with all eight. Most persistent misconception: '{mis_most['statement']}' ({mis_most['agreement_pct']:.1f}% agreement, mean {mis_most['mean_1to5']:.2f}/5). Best-corrected statement: '{mis_best['statement']}' ({mis_best['agreement_pct']:.1f}% agreement, mean {mis_best['mean_1to5']:.2f}/5).")
add_csv_table("T04_misconceptions.csv", "Table 4. Misconceptions — agreement distribution", maxrows=12)
add_csv_table("T04b_misconceptions_summary.csv", "Table 4b. Misconception score summary")
add_figure("F06_misconceptions.png", "Figure 6. Misconceptions — agreement distribution", width=6.4)

# ============ 7. HYPOTHESIS 1 ============
h1("7. HYPOTHESIS 1: KNOWLEDGE ↔ PRACTICE RELATIONSHIP")
h1_fixed = pd.read_csv(TAB_DIR / "T07_hypothesis1_chi2.csv")
h1_row = h1_fixed[h1_fixed["test"] == "H1 Primary"].iloc[0]
h1_s = pd.read_csv(TAB_DIR / "T07b_correlation_continuous.csv").iloc[0]
h1_p = pd.read_csv(TAB_DIR / "T07b_correlation_continuous.csv").iloc[1]

para(f"H1: No significant relationship between knowledge and practice (H0).")
para(f"Chi-square (Fixed categories): χ²={h1_row['chi2']}, df={h1_row['dof']}, p={h1_row['p']:.4f}, Cramér's V={h1_row['cramers_v']} — significant (some cells expected <5).")
para(f"Continuous: Spearman ρ={h1_s['r']} (p={h1_s['p']:.4f}), Pearson r={h1_p['r']} (p={h1_p['p']:.4f}) — moderate positive correlation.")
para("→ H0 REJECTED. Knowledge is significantly associated with practice; higher knowledge associated with better preventive practice.")
add_csv_table("T07_hypothesis1_chi2.csv", "Table 5. H1: Chi-square (Knowledge × Practice categories)")
add_csv_table("T07b_correlation_continuous.csv", "Table 5b. Continuous correlation (Spearman + Pearson)")
add_figure("F07_knowledge_practice_scatter.png", "Figure 7. Knowledge vs Practice scatter with linear fit")
add_figure("F15_correlation_heatmap.png", "Figure 15. Knowledge, Practice & Misconception correlation heatmap")
add_figure("F14_know_practice_stacked.png", "Figure 14. Practice category within Knowledge category")

# ============ 8. HYPOTHESIS 2 ============
h1("8. HYPOTHESIS 2: SCORE DIFFERENCES BY ACADEMIC LEVEL & FACULTY")
k_level = pd.read_csv(TAB_DIR / "T08_kruskal_level.csv")
k_know = k_level[k_level["variable"] == "Knowledge"].iloc[0]
k_prac = k_level[k_level["variable"] == "Practice"].iloc[0]
k_mis = k_level[k_level["variable"] == "Misconceptions"].iloc[0]

para(f"H2: No significant difference in knowledge/practice across academic levels (H0).")
para(f"Knowledge: Kruskal-Wallis H={k_know['H']}, df=3, p={k_know['p']:.4f} — significant. Means: 100L={km_by_level['100 Level']:.2f}, 200L={km_by_level['200 Level']:.2f}, 300L={km_by_level['300 Level']:.2f}, 400L={km_by_level['400 Level']:.2f} — rises to 300L then plateaus. Pairwise MW (Bonferroni): 100L vs 300L (p=0.0007), 100L vs 400L (p=0.0002), 200L vs 300L (p=0.0494), 200L vs 400L (p=0.0273); 100L vs 200L and 300L vs 400L not significant.")
para(f"Practice: Kruskal-Wallis H={k_prac['H']:.3f}, df=3, p={k_prac['p']:.4f} — significant. Means: 100L={pm_by_level['100 Level']:.2f}, 200L={pm_by_level['200 Level']:.2f}, 300L={pm_by_level['300 Level']:.2f}, 400L={pm_by_level['400 Level']:.2f} — non-monotonic: a 200L dip below 100L, with the best practice at 300/400L. Pairwise (Bonferroni): 100L vs 300L (p=0.0008), 100L vs 400L (p<0.0001), 200L vs 300L (p<0.0001), 200L vs 400L (p<0.0001); 100L vs 200L and 300L vs 400L not significant.")
para(f"Misconceptions: H={k_mis['H']:.3f}, p={k_mis['p']:.4f} — significant but modest and non-monotonic. Means: 100L={mm_by_level['100 Level']:.2f} (highest), 200L={mm_by_level['200 Level']:.2f} (lowest), 300L={mm_by_level['300 Level']:.2f}, 400L={mm_by_level['400 Level']:.2f}. No pairwise contrast survives Bonferroni correction (raw p<0.05 for 100L vs 200L, 100L vs 400L and 300L vs 400L only).")
add_csv_table("T08_kruskal_level.csv", "Table 6. Kruskal-Wallis + Mann-Whitney (Level)", maxrows=20)
add_csv_table("T08b_kruskal_faculty.csv", "Table 6b. Kruskal-Wallis (Faculty Group)")
add_csv_table("T08c_category_demographics.csv", "Table 6c. Categories × Demographics (Chi-square)")
add_figure("F08_knowledge_by_level_faculty.png", "Figure 8. Knowledge by Level & Faculty")
add_figure("F09_practice_by_level_faculty.png", "Figure 9. Practice by Level & Faculty")
add_figure("F13_misconceptions_by_level.png", "Figure 13. Misconceptions by Level")
add_figure("F16_gap_by_level.png", "Figure 16. Knowledge-Practice Gap Score by Level")

# ============ 9. INFORMATION SOURCES ============
h1("9. SOURCES OF MALARIA PREVENTION KNOWLEDGE (OBJECTIVE 4)")
para(f"Primary sources: School/Course {src_school} ({src_school/N*100:.1f}%), Health worker/Clinic {src_hw} ({src_hw/N*100:.1f}%), Media (radio, TV, internet) {int((df['source_c']=='Media (radio, TV, internet)').sum())} ({int((df['source_c']=='Media (radio, TV, internet)').sum())/N*100:.1f}%), Family/Friends {int((df['source_c']=='Family/Friends').sum())} ({int((df['source_c']=='Family/Friends').sum())/N*100:.1f}%). Formal training: {int((df['training_c']=='Yes').sum())} (97.5%).")
add_csv_table("T09_info_sources.csv", "Table 7. Sources of malaria prevention knowledge")
add_figure("F11_info_sources.png", "Figure 11. Primary sources of knowledge")

# ============ 10. ITN OWNERSHIP & BARRIERS ============
h1("10. ITN OWNERSHIP, ACCESS & BARRIERS (OBJECTIVES 1, 2, 4)")
itn_yes = int((df['itn_own_c']=='Yes').sum())
itn_pct = itn_yes / N * 100
para(f"ITN ownership: {itn_yes} ({itn_pct:.1f}%). Access rating: Easy/Very Easy {access_easy} ({access_easy/N*100:.1f}%), Difficult/Very Difficult {access_diff} ({access_diff/N*100:.1f}%). Comfort under ITN: Comfortable/Very Comfortable {comfort_comf} ({comfort_comf/N*100:.1f}%), Uncomfortable/Very Uncomfortable {comfort_uncomf} ({comfort_uncomf/N*100:.1f}%).")
itn_yes = int((df['itn_own_c']=='Yes').sum())
itn_pct = itn_yes / N * 100
para(f"Purchase or replace ITN: Likely/Very Likely {np_likely} ({np_likely/N*100:.1f}%), Unlikely/Very Unlikely {np_unlikely} ({np_unlikely/N*100:.1f}%). Willing to participate in sanitation: {sanit_will} ({sanit_will/N*100:.1f}%); Likely to attend health talk: {talk_likely} ({talk_likely/N*100:.1f}%); Likely to seek treatment within 24h: {treat24_likely} ({treat24_likely/N*100:.1f}%).")
add_csv_table("T05_training_experience.csv", "Table 8. Training, ITN, Access", maxrows=15)
add_csv_table("T05b_itn_ownership_by_level.csv", "Table 9. ITN Ownership by Level")
add_csv_table("T06_barriers_intent.csv", "Table 10. Barriers & Future Intent")
add_figure("F10_itn_ownership_by_level.png", "Figure 10. ITN Ownership by Level")
add_figure("F12_barriers_intent.png", "Figure 12. Barriers & Future Intent")

# ============ 11. DISCUSSION ============
h1("11. DISCUSSION")
bullets([
    "Knowledge is high (mean 8.78/10) but practice is moderate (mean 29.4/40) — a clear knowledge-practice gap. ITN use is the weakest practice item (5.3% always), despite high knowledge (98.1% know ITN is most effective).",
    "Significant knowledge-practice correlation (Spearman ρ=0.39) confirms H1, but effect is moderate — knowledge alone insufficient; barriers (cost, discomfort, access) mediate the relationship.",
    "Knowledge rises with academic level (100L 7.66 → 300L 9.25 → 400L 9.25), reflecting curricular exposure, but practice improves less consistently: it dips at 200L (25.7) before peaking at 400L (31.3), knowledge alone does not translate into practice.",
    "ITN ownership only 50.2% despite near-universal knowledge of its effectiveness — discomfort (45.5% uncomfortable), cost and access barriers are key. Only 44.2% say they are likely to purchase/replace a net when torn — net maintenance is the critical weak point. Campus health infrastructure gaps evident.",
    "Orem's Self-Care Deficit Theory: Knowledge (foundational capability) is present, but self-care agency (practice) is compromised by barriers (basic conditioning factors: cost, access, environment). The self-care deficit manifests as inconsistent ITN use.",
])

# ============ 12. RECOMMENDATIONS ============
h1("12. RECOMMENDATIONS")
bullets([
    "Institutional ITN distribution programme (free/subsidised) targeting 100/200-level students with lowest ownership.",
    "Campus environmental sanitation programme: scheduled drainage clearing, larviciding, waste management — aligns with 65.4% willing to participate.",
    "Integrate mandatory malaria prevention module into 100-level orientation (GES/GST courses) covering ITN use, prompt treatment, misconceptions.",
    "Monitor & evaluate: annual KAP surveys, ITN distribution tracking, malaria incidence at university clinic.",
    "Establish peer health educator network (trained senior students) for hostel-based ITN promotion and myth-busting.",
    "Promote net maintenance: campus ITN repair/re-treatment days and subsidised replacement — only 44.2% are likely to purchase a replacement net (a key contributor to the 5.3% 'Always sleep under ITN' rate).",
    "Collaborate with Osun State Ministry of Health for IRS campaigns in off-campus hostels (84.7% off-campus).",
])

# ============ 13. LIMITATIONS ============
h1("13. LIMITATIONS & DISCLOSED DEVIATIONS")
bullets([
    "Cross-sectional design — causal inference limited; longitudinal studies needed.",
    "Convenience sampling via Google Forms — not strict stratified random sample; 100% consent but potential self-selection bias.",
    "Self-reported practice — subject to recall and social desirability bias (over-reporting of 'Always').",
    "Fixed + median categorisations for knowledge/practice (document doesn't specify cutoffs).",
    "Misconceptions scored separately (not merged with knowledge) — reverse-coded 4-pt scale.",
    "Department grouped into faculties using col 43 mapping + text cleaning; 243/321 'Other' due to missing faculty data.",
    "ITN ownership treated as both practice item and separate outcome.",
    "Logistic regressions (supplementary): estimated on binary categorisations; ORs/presented with CIs in the workbook (S06/S07); interpret with caution.",
    "No laboratory confirmation of malaria parasitaemia — practice based on self-report only.",
])

# ============ 14. APPENDIX ============
h1("14. APPENDIX — DELIVERABLES MANIFEST")
para("The following deliverables accompany this report:", bold=True)
bullets([
    "01_Report — this DOCX report (14 sections, 16 figures, 16 tables).",
    "02_Workbook — Excel workbook (12 sheets): README, Data_Dictionary, Cleaned_Data (321×137), Demographics, Knowledge, Practice, Misconceptions, Hypotheses, Training_Barriers, Supplementary (S01–S07), Charts_Native (10 native charts), Key_Findings.",
    "03_Tables — 21 CSV tables (T01–T13 incl. T02b/T03b/T04b/T07b/T08b/T08c/T10/T13).",
    "04_Figures — 16 PNG charts (F01–F16).",
    "05_Data — cleaned dataset (malaria_kap_cleaned.csv, 321×137) + item labels JSON.",
])
para("All analyses are fully reproducible from the cleaned dataset and the Python pipeline scripts (malaria_analysis.py, malaria_step2_stats.py, malaria_step3_figures.py, malaria_step4_workbook.py, malaria_step5_docx.py).", italic=True)

doc.save(OUT_FILE)
print("Saved:", OUT_FILE.name)

# ============================ Package to Client Folder ============================
import shutil
CLIENT_DIR = BASE / "reports" / "Assessment of Knowledge and Practice of Malaria Prevention among Undergraduate Students of FUHSI (Q-MPKP)"
shutil.copy(OUT_FILE, CLIENT_DIR / "01_Report" / OUT_FILE.name)
shutil.copy(BASE / "reports" / "output" / "Malaria_KAP_Analysis.xlsx", CLIENT_DIR / "02_Workbook" / "Malaria_KAP_Analysis.xlsx")
for f in TAB_DIR.glob("*.csv"):
    if f.name.startswith("T"):
        shutil.copy(f, CLIENT_DIR / "03_Tables" / f.name)
for f in FIG_DIR.glob("F*.png"):
    shutil.copy(f, CLIENT_DIR / "04_Figures" / f.name)
shutil.copy(CLEAN, CLIENT_DIR / "05_Data" / "malaria_kap_cleaned.csv")
shutil.copy(BASE / "data" / "processed" / "malaria_item_labels.json", CLIENT_DIR / "05_Data" / "malaria_item_labels.json")

print("Packaged to client folder:", CLIENT_DIR)
