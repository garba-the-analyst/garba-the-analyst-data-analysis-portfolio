# Malaria Prevention — Knowledge, Attitude & Practice (KAP) Analysis, FUHSI

**Client context:** Nursing Science undergraduate thesis, Federal University of Health Sciences, Ila-Orangun (FUHSI) · **N = 321** (100% consent rate) · Descriptive cross-sectional survey · 5-script reproducible pipeline.

## 🎯 Study Objectives

1. Assess the **level of knowledge** of malaria prevention among undergraduate students
2. Assess the **level of practice** of malaria prevention
3. Test whether **knowledge relates to practice** (H1)
4. Identify **sources of malaria prevention information**
5. Examine **differences by academic level / faculty** (H2), plus misconceptions, ITN ownership, access & barriers

Theoretical framework: **Orem's Self-Care Deficit Nursing Theory** — knowledge (foundational capability) vs. practice (self-care agency) vs. conditioning factors (cost, comfort, access).

## 🧪 Methods

- **Knowledge** (10 MCQs): dichotomous scoring (KR-20 = 0.73); categorised by fixed cutoffs (Good ≥8 / Moderate 5–7 / Poor <5) *and* median split
- **Practice** (8 Likert items): summed 8–40 (α = 0.82); fixed cutoffs (Good ≥30 / 18–29 / <18) *and* median split
- **Misconceptions** (8 false statements, reverse-coded): separate subscale (α = 0.97), never merged with knowledge
- **H1**: χ² on categories (+ Fisher exact where expected <5) **and** Spearman/Pearson on continuous scores
- **H2**: Kruskal-Wallis + Bonferroni-corrected Mann-Whitney pairwise; faculty grouping via document's department mapping
- **Supplementary (labelled)**: logistic regression (ITN ownership; good practice), gap score analysis, per-level breakdowns

## 📊 Headline Results

| Domain | Result |
|---|---|
| Knowledge | **8.78 / 10** (SD 1.69, median 9) — Good **83.8%**, Moderate 11.8%, Poor 4.4% |
| Practice | **29.39 / 40** (SD 5.21, median 29) — Good **49.5%**, Moderate 49.2%, Poor 1.2% |
| Misconceptions | **34.57 / 40** — agreement with all 8 false statements only **0.9–4.3%** |
| ITN ownership | **50.2%** (161/321) |

### H1 — Knowledge ↔ Practice: SIGNIFICANT → H0 rejected
- χ²(4) = **20.75**, *p* = 0.0004, Cramér's V = 0.18 (by level: strongest gradient at 100 Level, V = 0.38)
- Continuous: Spearman ρ = **0.39**, Pearson r = **0.355** (both *p* < 0.001)
- Logistic: each additional correct knowledge answer → **OR = 1.51** for ITN ownership (95% CI 1.27–1.79); OR = 1.38 for "good" practice (*p* = 0.0012)

### H2 — Differences by level: SIGNIFICANT for all three scores
| Score | Kruskal-Wallis | Pattern (means) |
|---|---|---|
| Knowledge | H = **25.31**, *p* < 0.001 | 7.66 → 8.65 → 9.25 → 9.25 (rises then plateaus) |
| Practice | H = **50.94**, *p* < 0.001 | 27.58 → **25.71 (dip)** → 30.57 → 31.28 (non-monotonic) |
| Misconceptions | H = **11.37**, *p* = 0.0099 | 100L highest (35.42); only 200/400 lowest-ish; non-monotonic, no pairwise survives Bonferroni |

### Practice Item Spectrum (most → least consistent)
Screen/close windows (63.2% "always") · refuse disposal (59.2%) · **ITN every night — only 5.3% "always"**, 40.8% "sometimes" · long sleeves (20.6% "always", 13.4% "never")

### Information & Barriers
- Sources: **School/Course 55.4%**, health worker/clinic 28.7%, media 11.2%, family 3.7%; 97.5% had formal malaria training
- Access to preventives: Easy/Very Easy 59.2%, Difficult/Very Difficult 17.1%
- Comfort sleeping under ITN: **45.5% uncomfortable**, only 27.4% comfortable
- Would purchase/replace a torn net: **44.2% likely** · willing to join campus sanitation: **65.4%** · likely to attend a health talk: **68.2%** · would seek treatment within 24h of fever: **35.8%**
- Residence: 84.7% off-campus hostels (IRS intervention target)

## 💡 Smart Insights

1. **The knowledge–practice gap is real but structural, not educational.** 98.1% know ITNs are the most effective method, 50.2% own one, 5.3% sleep under one nightly. Knowledge matters (OR 1.51), but **comfort (45.5% uncomfortable), net maintenance (44.2% replace-intent) and access** are the binding constraints — precisely Orem's "basic conditioning factors".
2. **The 200-Level practice dip is the actionable anomaly.** Practice drops below 100L (25.71 vs 27.58) despite higher knowledge — the transition year, not orientation, is where preventive habits collapse. A 200L-refresher would be more efficient than a 100L one.
3. **Misconceptions are nearly eliminated but not uniform.** Only 0.9–4.3% endorse any false statement; the residual is the *seasonality myth* ("nets only needed in rainy season") — an easy communication target tied to net-attrition messaging.
4. **The net lifecycle is the weakest link in the whole ITN chain.** Ownership (50.2%) → nightly use (5.3%) → replacement intent (44.2%) forms a funnel where every stage loses ~half of the previous stage's participants.
5. **Knowledge plateaus at 300L** (9.25 ≈ 9.25) — the teaching effect saturates; further gains must come from practice-side interventions, not more lectures.

## 🗂 Deliverables in this folder

| Path | Content |
|---|---|
| `scripts/` | 5-phase pipeline: cleaning/scoring → statistics → figures → Excel workbook → DOCX report |
| `tables/` | 21 aggregate result tables (T01–T13 incl. logistic models) |
| `figures/` | 16 publication-style charts (F01–F16) |
| `README.md` | this file |

> 🔒 **Data note:** raw and cleaned respondent datasets are excluded for confidentiality. Pipeline scripts read the survey response CSV (`FUHSI_Malaria_Prevention_Survey_321_Responses.csv`) as input.

## ▶️ How to run

```bash
pip install -r requirements.txt   # repo root
python scripts/malaria_analysis.py        # clean + score -> cleaned CSV
python scripts/malaria_step2_stats.py     # statistics -> tables/
python scripts/malaria_step3_figures.py   # charts -> figures/
python scripts/malaria_step4_workbook.py  # Excel workbook (12 sheets, 10 native charts)
python scripts/malaria_step5_docx.py      # APA-style DOCX report with embedded tables/figures
```
