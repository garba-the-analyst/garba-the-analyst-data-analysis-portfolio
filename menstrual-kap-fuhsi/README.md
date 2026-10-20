# Menstrual Irregularities — Knowledge, Attitude & Health-Seeking Behaviour — FUHSI

**Client context:** Public Health undergraduate thesis, FUHSI · **N = 376** female undergraduates · Health Belief Model framework over a classic 3-objective KAP design · 5-script reproducible pipeline.

## 🎯 Study Objectives

1. Assess the **level of knowledge** of menstrual irregularities
2. Assess the **attitudes** toward menstrual irregularities
3. Describe **health-seeking behaviour patterns**
4. Determine **barriers to health-seeking** (HBM constructs)
5. Test **knowledge ↔ health-seeking behaviour** (H1) and demographic associations (H2)

## 🧪 Methods

- **Knowledge** (12 dichotomous items): fixed + mean/median dual categorisation, KR-20 = **0.772**
- **Attitudes** (10 items, 1–5): composite 10–50, α = 0.43 (low — **disclosed verbatim in the report** as a design limitation)
- **Health-seeking behaviour**: ever-experience, types experienced, first response, timeliness, facility choice, future intent
- **HBM constructs**: perceived susceptibility / severity / benefits / barriers / self-efficacy (α = 0.822)
- **H1 / H2**: chi-square with Cramér's V; Pearson correlations for scale relationships
- **Supplementary (labelled)**: Bloom's grading crossover, group comparisons, logistic regression for future help-seeking intent

## 📊 Headline Results (n = 376)

| Domain | Result |
|---|---|
| Knowledge | **10.63 / 12** (median 11, SD 2.00) — Good **69.1%** (260), Poor 30.9%; identical under mean & median splits |
| Attitude | **40.39 / 50** (median 41, SD 4.09) — Positive **52.7%** (198), Negative 47.3% |
| Ever experienced irregularity | **68.4%** (257/376) |
| Top experience type | Irregular cycle length (51.6% of respondents listing types) |
| Future help-seeking intent | **88.0%** (331) say they would consult a professional |

### The health-seeking paradox (objective 3)
- Among the 257 who experienced irregularity: only **42.0% sought medical care**
- Most common first response to symptoms: **"ignored it"**
- Campus health centre: used by only **13.8%**

### Barriers (objective 4)
- #1 barrier — *"Belief that it would resolve on its own"* (**266 mentions; 70.7%** of the whole sample): symptomatic-normalisation dominates ahead of cost, time, embarrassment, or access unawareness

### Hypothesis tests
| Test | Result | Decision |
|---|---|---|
| H1: knowledge ↔ help-seeking intention | χ²(1) = **6.865**, *p* = 0.0088, V = 0.135 | **Reject H0** — significant |
| H2: knowledge/attitude × demographics | not significant | Retain H0 |
| Knowledge ↔ HBM self-efficacy | r = **0.50**, *p* < 0.001 | strong positive |
| Knowledge ↔ perceived severity / susceptibility | r = 0.44 / 0.32 | moderate positive |
| Logistic (future intent ~ knowledge + level) | knowledge OR = 1.22 (*p* = 0.005); level OR = 0.59 per step (*p* = 0.002) | both significant |

## 💡 Smart Insights

1. **Knowledge and attitude aren't the problem — symptom normalisation is.** 69% good knowledge, 88% future intent, yet barely 42% of affected students sought care. The single dominant barrier is the *belief that menstrual irregularity resolves on its own* (70.7%) — a clinical-education mismatch: what students have learned treats it as routine, so no internal alarm fires.
2. **The knowledge→efficacy link (r = 0.50) is the campaign entry point.** Since knowledge strongly predicts self-efficacy, and self-efficacy is the HBM determinant most amenable to change, an awareness module that pairs "when is an irregular cycle a red flag" with a concrete action script ("book at the campus clinic within X days") converts knowledge into care-seeking.
3. **Campus clinic is bypassed (13.8%)** even though the preferred first contact point for students. Digital/telehealth triage for menstrual complaints (amounts to workflow redesign, not new facilities) fits perfectly with an already 99%-connected student population.
4. **Youngest students carry highest risk with lowest action**: mean age 19.7, 72.9% aged 16–20 — a demographic segment at peak cycle-instability age with 274 of it in the youngest band, and each level step *down* the logistic reduces intent (OR 0.59 per level step) — junior students need a targeted first-contact programme, not senior-style self-referral.
5. **The 47.3% negative-attitude minority is the attitude battleground**: with attitudes split nearly down the middle, peer testimonials (HEB self-rated relevance) in cohort groups can shift the median — attitude is malleable where infrastructure already exists.

## 🗂 Deliverables in this folder

| Path | Content |
|---|---|
| `scripts/` | 5-phase pipeline: cleaning/scoring → statistics → figures → workbook → DOCX report |
| `tables/` | 28 aggregate tables (T01–T07 + S01–S04 supplementary) |
| `figures/` | 16 charts (F01–F16) |

> 🔒 **Data note:** raw and cleaned respondent datasets are excluded for confidentiality. Scripts read the menstrual-irregularities survey response CSV as input.

## ▶️ How to run

```bash
pip install -r requirements.txt   # repo root
python scripts/kap_analysis.py
python scripts/kap_step2_stats.py
python scripts/kap_step3_figures.py
python scripts/kap_step4_workbook.py
python scripts/kap_step5_docx.py
```
