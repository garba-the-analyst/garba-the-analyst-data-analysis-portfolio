# Substance Abuse & Perceived Health Implications — FUHSI

**Client context:** Public Health undergraduate thesis, FUHSI · **N = 395** consenting respondents · Health Belief Model (HBM) framework · 5-script reproducible pipeline.

## 🎯 Study Objectives

1. Determine the **prevalence and pattern** of substance use (objective 1)
2. Assess **factors influencing** substance use among undergraduates (objective 2)
3. Assess **perceived health implications** (objective 3)
4. Assess **perceived prevention strategies** (objective 4)
5. Reliability + bivariate + correlation + logistic supplementary analyses

## 🧪 Methods

- **Prevalence cascade**: ever-use → past-3-month use → problem use (CAGE-type screening indicators)
- **Factors / Health / Prevention scales**: 5-point Likert composites + sub-scale breakdown; HBM constructs
- **Reliability**: Cronbach's α per scale (Factors α = **0.908**, Health α = **0.937**, Prevention α = **0.904**)
- **Bivariate**: chi-square across demographics (Cramér's V)
- **Correlation**: Spearman matrix (continuous composites + demographics)
- **Logistic** (supplementary): ever-use, past-3-month, problem-use models with aORs and 95% CIs

## 📊 Headline Results (n = 395)

### Prevalence cascade
| Stage | n | % |
|---|---|---|
| **Ever used** any psychoactive substance | 63 | **15.9%** |
| Used in the **past 3 months** | 37 | 9.4% |
| **Problem use** flagged (CAGE-type) | 22 | 5.6% |
| Alcohol = most used substance (41 | 10.4% of sample); then codeine cough syrup (10), tobacco (15), sedatives (12), tramadol (7), cannabis (5) | | |

### Factors influencing use (objective 2)
| Factor | SA+A |
|---|---|
| **Peer pressure** | **97.7%** |
| Emotional distress | 93.2% |
| Coping | 93.2% |
| Parental monitoring | 93.2% |

### Perceived health implications (objective 3)
- All 12 items ≥ **95.5%** SA+A — near-universal harm recognition
- Mean health-implications score **4.54 / 5** (SD 0.41)
- Top: dependence (100%), organ damage (100%), cardiovascular/respiratory/concentration/accidents (99.2%)

### Prevention strategies (objective 4)
- Counselling & education **97.7%** SA+A; parental involvement 96.2%; policy measures 95.5%; mean prevention score **4.36 / 5**
- 79.5% agree *inadequate enforcement* influences use

### Associations & regression (supplementary)
- Ever-use associated with: **Sex** (*p* < 0.001), Faculty (*p* = 0.005), Allowance (*p* = 0.010), Level (*p* = 0.032)
- Logistic model (ever use): **Male aOR = 10.13** (95% CI 2.51–40.97, *p* = 0.001); Faculty of Sciences aOR = 8.29 (*p* = 0.006); lower allowance aOR = 0.06 (*p* = 0.007)

## 💡 Smart Insights

1. **An awareness–behaviour gap, not an awareness deficit.** Harm recognition is ≥95.5% across every domain, and prevention endorsement ~97% — yet 15.9% have used. Information campaigns alone are saturated; interventions must target *social context* (peer pressure 97.7%) rather than knowledge.
2. **The problem population is small and concentrated (5.6%)** — a brief-intervention/referral pathway aimed at ~22 high-risk respondents out of 395 is a feasible, high-yield campus intervention.
3. **Male students carry ~10× the odds** of ever-use (aOR 10.13) — gender-targeted messaging (not gender-blind programming) is statistically justified.
4. **Peer pressure is the dominant, most-endorsed driver at 97.7%** — practically no room for it to rise. That points to peer-led normative campaigns ("most students don't use") as the highest-leverage lever, consistent with Social Learning Theory.
5. **Alcohol is the gateway and the biggest volume**: 10.4% of the total sample named it, ~2–4× any single other substance — the 79.5% enforcement-opinion suggests campus policy is the pressure point.

## 🗂 Deliverables in this folder

| Path | Content |
|---|---|
| `scripts/` | 5-phase pipeline: cleaning/scoring → statistics → figures → workbook → DOCX report |
| `tables/` | 23 aggregate tables (D01–D10 + logistic models) |
| `figures/` | 17 charts (sub_F01–sub_F16 incl. cascade, radar, heatmaps) |

> 🔒 **Data note:** raw and cleaned respondent datasets are excluded for confidentiality. Scripts read `FUHSI_Substance_Abuse_Survey_395_Responses.csv` as input.

## ▶️ How to run

```bash
pip install -r requirements.txt   # repo root
python scripts/sub_analysis.py
python scripts/sub_step2_stats.py
python scripts/sub_step3_figures.py
python scripts/sub_step4_workbook.py
python scripts/sub_step5_docx.py
```
