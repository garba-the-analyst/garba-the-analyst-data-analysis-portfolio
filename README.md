# 📊 Garba-The-Analyst — Data Analysis Portfolio

Production-grade statistical analysis projects executed end-to-end for real research clients (undergraduate thesis studies at **Federal University of Health Sciences, Ila-Orangun, FUHSI**): from **raw survey data → cleaning & scoring → hypothesis testing → publication-ready APA reports, Excel workbooks, and client delivery folders**.

Each project is a fully reproducible Python pipeline — not a one-off notebook.

## 🧰 Tech Stack

| Layer | Tools |
|---|---|
| Data processing | Python, pandas, NumPy, openpyxl |
| Statistics | SciPy (chi-square, Mann-Whitney, Kruskal-Wallis, Spearman/Pearson), statsmodels (logistic regression) |
| Visualisation | matplotlib, seaborn |
| Reporting | python-docx (APA-style reports), openpyxl (native Excel charts) |
| Versioning of deliverables | Per-client folders: report, workbook, tables, figures, cleaned data |

## 🗂 Projects

### 1. [Malaria Prevention KAP](./malaria-kap-fuhsi) — N = 321
**Knowledge & Practice of Malaria Prevention among Undergraduates (Orem's Self-Care Deficit framework).**
Knowledge is high (8.78/10; 83.8% "good") but practice is moderate (29.39/40; only 5.3% always sleep under ITNs) — a classic **knowledge–practice gap** confirmed statistically: χ² = 20.75, *p* = 0.0004; Spearman ρ = 0.39.

### 2. [Substance Abuse & Health Implications](./substance-abuse-fuhsi) — N = 395
Awareness of harms is near-universal (≥95.5%) among undergraduates and problem use is concentrated (5.6%) — prevalence 15.9% ever-use; male students show ~10× odds of ever-use (*a*OR = 10.13, *p* = 0.001). Driven by peer pressure, endorsed by 97.7% as the top factor.

### 3. [Internet Access & Self-Directed Learning](./internet-sdl-readiness-fuhsi) — N = 379
99.5% own a device and 82.6% show high SDL readiness (α = 0.92) — but readiness **declines** with seniority (103.6 at 100L → 99.0 at 400L). Internet access correlates with SDL readiness (Pearson r = 0.371, *p* < 0.001).

### 4. [Menstrual Irregularities KAP & Health-Seeking](./menstrual-kap-fuhsi) — N = 376
Good knowledge (69.1%) and positive attitudes (52.7%), yet only **42% of students who experienced irregular cycles sought medical care** — the top barrier is the belief symptoms will "resolve on their own" (70.7%). Knowledge predicts help-seeking (χ²(1) = 6.87, *p* = 0.0088).

## 📌 Methodology Highlights (all studies)

- **Instrument fidelity**: scoring keys, categorisations and analysis plans reconstructed from each study's thesis document (e.g. §3.10/§3.11 analysis plan), with disclosed deviations
- **Dual categorisation**: fixed clinical cutoffs **and** median splits reported side-by-side
- **Non-parametric rigor**: Kruskal-Wallis + Bonferroni-corrected Mann-Whitney pairwise tests; Cramér's V and exact tests flagged when cell counts < 5
- **Supplementary depth**: logistic regressions (odds ratios with 95% CI), gap scores, reliability analysis (Cronbach's α / KR-20) per instrument section
- **Deliverable discipline**: DOCX report (auto-narrated from computed values — no hardcoded numbers), Excel workbook with native charts + cleaned data, per-table CSVs with figures

## 🔒 Data Policy

Survey instruments and cleaned respondent datasets are **excluded from this repository for research-ethics/confidentiality reasons**. Each project folder contains: the full analysis scripts, all aggregate statistical tables (CSV), and figures (PNG). The pipelines are parameterised to run against the raw response CSVs.

## 📬 Contact

**Garba Abdullahi** — Data Analyst
Email: garbaabdullahi344@gmail.com
