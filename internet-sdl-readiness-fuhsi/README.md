# Internet Access & Self-Directed Learning (SDL) Readiness — FUHSI

**Client context:** Health Information/Data undergraduate thesis, FUHSI · **N = 379** · SDLRSNE instrument (24 scored items after document-fidelity review) · 5-script reproducible pipeline.

## 🎯 Study Objectives

1. Determine the **level of internet access** among undergraduates
2. Assess **SDL readiness** (self-management, desire for learning, self-control)
3. Test the **relationship between internet access and SDL readiness** (H1)
4. Test **differences in SDL readiness across academic levels** (H2)
5. Identify **factors influencing internet access**

## 🧪 Methods

- **Internet access composite** (access, frequency, reliability, satisfaction, device ownership) scored 1–5
- **SDL total** (24-item SDLRSNE adapted, scaled to 120) with three 8-item subscales
- **Reliability**: Cronbach's α — Total **0.92**; Self-Management 0.87 · Desire for Learning 0.89 · Self-Control 0.85
- **H1**: Spearman + Pearson between IA composite and SDL total (+ component-level correlations)
- **H2**: Kruskal-Wallis + Bonferroni-corrected Mann-Whitney across four levels
- Non-parametric choice justified by scale distributions

## 📊 Headline Results

### Objective 1 — Internet access is device-rich but data-constrained
| Metric | Result |
|---|---|
| Device ownership | **99.5%** (377/379) |
| Primary access | personal **mobile data 93.4%** |
| Frequency | **66.0% access daily**; 29.8% several times/week |
| IA composite | **4.39 / 5** (SD 0.42) |
| Satisfaction | Neutral 51.2%, Satisfied 20.8%, Dissatisfied+Very dissigious 15.3% |
| Reliability perception | 78.4% "Fairly/Very reliable" |

### Objective 2 — SDL readiness is high, concentrated in the upper band
| Metric | Result |
|---|---|
| SDL total | **100.8 / 120** (SD 15.5) |
| Categories | **High 82.6%** (313) · Moderate 15.6% (59) · Low 1.8% (7) |
| Subscales (1–5) | Desire for Learning **4.35** · Self-Management **4.32** · Self-Control **3.93** |

### H1 — IA ↔ SDL: SIGNIFICANT → H0 rejected
- Spearman ρ = **0.163** (*p* = 0.0015); Pearson r = **0.371** (*p* < 0.001) — moderate positive
- Component level: **frequency of access** is the strongest correlate of SDL readiness (ρ ≈ 0.30), ahead of reliability and hours

### H2 — SDL by academic level: SIGNIFICANT → H0 rejected (declining gradient)
| Level | n | Mean SDL | SD |
|---|---|---|---|
| 100 | 67 | **103.63** | 15.91 |
| 200 | 68 | 101.97 | 22.81 |
| 300 | 89 | 100.86 | 14.27 |
| 400 | 155 | **99.04** | 11.55 |

Kruskal-Wallis H = **11.745**, *p* = 0.0083. Bonferroni pairwise: the only significant contrast is **200 vs 400 Level** (*p* = 0.0162) — readiness *declines* with seniority rather than rising.

## 💡 Smart Insights

1. **Access isn't the constraint — data quality is.** With 99.5% device ownership, the differentiator is *what kind* of access: 93.4% depend on personal mobile data with only 78.4% perceiving it reliable. Campus Wi-Fi/e-learning support, not device provision, is where university investment moves numbers.
2. **Self-control is the SDL weak spot (3.93 vs 4.32–4.35 for the other subscales)** — and self-control is the most trainable: time-blocking, cohort accountability, and structured study calendars target exactly this deficit.
3. **Frequency beats volume**: daily rhythm of access correlates with SDL readiness better than duration/ownership — nudging students toward *consistent* daily study connectivity matters more than raw hours.
4. **Senior students' surprises**: readiness declines monotonically (103.6 → 99.0) and 400L shows the tightest SD (11.55). Expecting "more experienced = more self-directed" is empirically backwards here; faculty staff should treat 300/400L SDL scaffolding as a priority, not assume maturity covers it.
5. **The "high-access, high-SDL" majority (82.6%) is an institutional asset**: peer-mentoring/flip-classroom pilots should start with this band, whose readiness is already adequate.

## 🗂 Deliverables in this folder

| Path | Content |
|---|---|
| `scripts/` | 5-phase pipeline: cleaning/scoring → statistics → figures → workbook → DOCX report |
| `tables/` | 23 aggregate tables (T01–T10 incl. reliability & pairwise) |
| `figures/` | 17 charts (F01–F16 + F10b) |

> 🔒 **Data note:** raw and cleaned respondent datasets are excluded for confidentiality. Scripts read `Unreseracgd_form_Responses_379.xlsx` as input.

## ▶️ How to run

```bash
pip install -r requirements.txt   # repo root
python scripts/internet_sdl_analysis.py
python scripts/internet_sdl_step2_stats.py
python scripts/internet_sdl_step3_figures.py
python scripts/internet_sdl_step4_workbook.py
python scripts/internet_sdl_step5_docx.py
```
