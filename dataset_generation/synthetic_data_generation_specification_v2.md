# Synthetic Dataset Generation Specification (v2)

## 1. Purpose and how to use this document

This document is the single source of truth for how the synthetic dataset is designed, generated, and validated. It is written so that a second person could reproduce the dataset from the document and the accompanying code alone.

Every calibration figure below traces to a named, verifiable source. Where no source exists, the figure is a stated assumption, not a disguised fact. Design choices that are clinical or methodological judgement not fixed by evidence are flagged for supervisor sign-off.

---

## 2. Scope and governing principles

**In scope.** A two-stage rules-based matching method (hard-rule filtering, then weighted multi-attribute similarity scoring), forming peer groups from synthetic profiles of UK adults living with a long-term condition (LTC), entirely computationally.

**Out of scope.** 
- Human participants of any kind
- Real or online-sourced patient data
- Machine-learned or trained models
- Any deployable product or consent workflow
- Populations outside the UK

Four principles govern the design: 
- Traceability (every distribution is sourced or declared an assumption)
- Internal consistency (a generated profile must be logically possible)
- Sufficiency rather than realism theatre (the dataset needs to exercise the matching method and support the planned statistics, not simulate every feature of the real population)
- A clear separation between calibration attributes and matching attributes

---

## 3. Design decisions record

This section records what was decided, when and why

**Age and demography.** Age is represented as an ordinal band, not a real age per row, so that no generated value ties to an individual. Demography beyond gender is optional and included only where it supports the aim; ethnicity and region are removed entirely, since neither feeds a matching attribute or the cohesion outcome. Gender is retained because it is a committed soft matching attribute. Deprivation (IMD quintile) is retained, but only as an internal driver of the isolation score, not as a demographic in its own right.

**Dataset size.** The tension between "calibrate to the latest national UK figures" and "the laptop must be able to process it" is resolved by separating two numbers. The population being *represented* is national scale: around 25 million people in England live with at least one long-term condition, and multiple long-term conditions affect roughly 14 to 15% of the England population, about 14 million people (Valabhji et al., 2024). These are the calibration targets; the generated distributions are shaped to look like this population. The number of profiles actually *generated and matched in one run* is bounded by computation, not by the size of the real population. The core matching method, weighted Gower distance, is an all-pairs computation of order n-squared in both time and memory; Liu et al. (2024), the project's own method reference, report a runtime of about three minutes on 3,760 records, and a precomputed distance matrix becomes heavy in minutes and several gigabytes of memory at around 35,000 records (Schubert & Rousseeuw, 2021). A single pairwise computation across millions of records is not feasible on a laptop. The resolution: calibrate the generator to the national figures, generate as large a representative pool as useful (generation is linear and cheap; roughly 50,000 profiles in 20 seconds on this project's development machine), but run the matching evaluation on tractable samples, in the low thousands to about 10,000 profiles, matching within eligible cohorts rather than as one distance matrix across the whole population, mirroring how a real service would operate. **[Supervisor sign-off]** confirm this reconciliation and the working sample size for the matching evaluation.

**Poster.** The assessment brief and Moodle resources are the authority for poster content and are not reproduced here.

### 3.2 Decisions from this session (dataset attributes)

- **Communication language** — resolved from Census 2021 (Office for National Statistics, 2022), England-specific main-language shares. No longer an assumption.
- **Region** — removed entirely (demography, not needed for the aim).
- **Living alone by age band** — anchored to Census 2021 living-arrangements data (Office for National Statistics, 2023), interpolated across bands.
- **Age-band weights** — kept as the LTC-shifted approximation informed by Barnett et al. (2012) and Valabhji et al. (2024), since no single published source gives the exact age distribution of an LTC-only population and age was de-prioritised in the 1 July call.
- **Primary support goal** — categories set to `emotional_support`, `self_management_info`, `social_connection`, `accountability`, `shared_activity`, with an agreed proportional split. Remains an assumption (no population data exists for a peer-support service).
- **Support orientation** — kept (Seeking / Balanced / Offering).
- **Communication modality** — removed.
- **Engagement level** — kept (Low / Medium / High).
- **Safeguarding exclusion flag** — removed. It fed only one hard-rule field and one audit check, neither of which affects the cohesion evaluation; a randomly generated safeguarding flag on synthetic data was not defensible. The hard rule remains part of the method's design narrative, understood to require real data in any live deployment.
- **Isolation score construct** — scaled using the UCLA Loneliness Scale, Version 3 (Russell, 1996) range of 20 to 80, anchored to loneliness health gradients (NHS England, 2026) and the mortality risk of living alone (Holt-Lunstad et al., 2015). The high-isolation threshold (50) follows the categorisation used in loneliness-intervention trials registered on ClinicalTrials.gov (e.g. NCT03442296): 20–34 low, 35–49 moderate, 50–64 moderately high, 65–80 high; 50 marks the start of "moderately high."
- **Condition weights** — kept as the whole-population Payne et al. (2020) prevalences. No published source breaks condition prevalence down within an LTC-only population for this condition set; conditioning on "has at least one LTC" divides every condition's prevalence by a broadly similar factor, so using whole-population prevalences as relative sampling weights does not materially distort the *relative* ordering between conditions. Stated as a limitation.
- **Minimum onset age (`MIN_ONSET_AGE`)** — retained, but its role changed. With no real age generated, it now serves only as a band-eligibility gate (stopping, for example, heart failure appearing in the 18–29 band), not a per-row numeric constraint. Still clinical judgement; for supervisor sign-off.
- **Optional conditions** (epilepsy, irritable bowel syndrome, serious mental illness, alcohol problems) — removed.
- **Optional demographics** (ethnicity, region) — removed.
- **IMD quintile** — kept, per the 1 July call, purely as the driver of the isolation score, not stored as demography for its own sake (though it is retained as a field so the deprivation-isolation association can be validated).

---

## 4. Condition taxonomy

### 4.1 Source and rationale

The **Cambridge Multimorbidity Score (CMS)** condition list (Payne et al., 2020) is the taxonomy backbone, cross-checked against Barnett et al. (2012). Both were verified directly from the primary papers during this project (not reconstructed from memory), which matters because the taxonomy's defensibility depends on it being inspectable rather than asserted.

Payne et al. (2020) modelled the association between 37 morbidities and three outcomes (primary care consultations, unplanned hospital admission, and death) using development (n = 300,000) and validation (n = 150,000) samples drawn from the UK Clinical Practice Research Datalink, and derived a simplified 20-condition score that performed nearly as well as the full 37-condition version and outperformed the older Charlson Comorbidity Index across all three outcomes. Table 2 of that paper gives the verified prevalence and outcome weights for all 20 conditions; this project uses those prevalences directly (reproduced in section 4.2).

Barnett et al. (2012) is the foundational UK epidemiological source for multimorbidity as a phenomenon (age gradient, deprivation gradient, physical-to-mental-health coupling) rather than as a condition list. It is a cross-sectional study of 1,751,841 people registered with 314 medical practices in Scotland (2007), examining 40 morbidities. Because it is older and Scotland-specific, it is used here to ground the *relationships* in the data (how multimorbidity varies with age and deprivation), not the condition list itself.

### 4.2 The curated condition set

From the 20 CMS conditions, the taxonomy is curated to chronic conditions with a documented association with loneliness or social isolation (National Academies of Sciences, Engineering, and Medicine, 2020) that also form a meaningful basis for a peer support group.

| Parent category | Sub-types | CMS prevalence (%), whole population |
|---|---|---|
| Cardiovascular | Coronary heart disease, Heart failure, Stroke and TIA, Atrial fibrillation | 4.79, 1.04, 2.55, 2.72 |
| Metabolic and endocrine | Diabetes mellitus | 6.58 |
| Respiratory | COPD | 2.46 |
| Mental health | Anxiety or depression | 12.85 |
| Musculoskeletal and chronic pain | Painful condition, Connective tissue disorder | 11.63, 2.33 |
| Renal | Chronic kidney disease | 4.50 |
| Cancer experience | Cancer | 2.15 |

Prevalences are from Payne et al. (2020, Table 2), the development cohort.

**Excluded, with reason:**
- Hearing loss, blindness/low vision — sensory; not a peer-group basis (project direction).
- Hypertension — largely asymptomatic; not loneliness-defining, so excluded from the group-forming taxonomy.
- Constipation, irritable bowel syndrome — weak isolation evidence for group formation.
- Dementia — high isolation, but raises capacity and consent issues for a self-directed peer group.
- Psychosis/bipolar disorder, alcohol problems — high isolation, but distinct safeguarding and peer-support domains, outside this project's scope.
- Epilepsy — considered for inclusion given documented stigma-related isolation, but removed to keep the taxonomy tight (supervisor decision, this session).

**[Supervisor sign-off]** the final parent-category mapping (which conditions group together for eligibility) and the exclusion list above.

### 4.3 Whole-population versus LTC-population prevalence

The CMS prevalences in section 4.2 are whole-population primary-care figures, not the distribution within an LTC-only population, and no published source breaks the curated 11-condition set down within an LTC-only population. Because conditioning on "has at least one LTC" divides every condition's prevalence by a broadly similar factor, using the whole-population prevalences as *relative* sampling weights does not materially distort the ordering between conditions, even though the absolute magnitudes would shift under true conditioning. This is a stated limitation, not a hidden one.

---

## 5. Profile attribute schema

| Attribute | Purpose | Type | Categories | Source / status |
|---|---|---|---|---|
| `profile_id` | Unique key | String | Sequential | N/A |
| `age_band` | Matching attribute; drives condition plausibility | Ordinal | 18-29, 30-44, 45-59, 60-74, 75+ | Weights informed by Barnett et al. (2012); Valabhji et al. (2024) |
| `gender` | Soft matching attribute | Categorical | Woman, Man, Non-binary or self-describe | Women over-represented per Barnett et al. (2012); non-cisgender share per ONS (2023) |
| `imd_quintile` | Internal driver of isolation score | Ordinal | 1 (most deprived) to 5 (least) | Sampled uniformly; drives isolation gradient (NHS England, 2026) |
| `communication_language` | Hard-rule eligibility | Categorical | English, Polish, Romanian, Panjabi, Urdu, Other | Census 2021, England (ONS, 2022) |
| `lives_alone` | Feeds isolation score | Boolean | — | Anchored to Census 2021 (ONS, 2023) |
| `primary_condition_category` | Parent category for eligibility | Categorical | Section 4.2 | Payne et al. (2020) |
| `primary_condition_subtype` | Matching attribute (homogeneity) | Categorical | Section 4.2 | Payne et al. (2020) |
| `condition_count` | Multimorbidity indicator | Integer | ≥ 1 | Barnett et al. (2012, Table 1) |
| `comorbidities` | Secondary conditions | Set (semicolon-joined) | Section 4.2, excludes primary | Barnett et al. (2012) for count distribution and mental-health coupling |
| `condition_duration_band` | Matching attribute (homogeneity) | Ordinal | <1, 1-2, 3-5, 6-10, 11-20, 20+ | Capped by adult years in the age band |
| `primary_support_goal` | Matching (homogeneity) | Categorical | emotional_support, self_management_info, social_connection, accountability, shared_activity | Assumption (agreed with supervisor) |
| `support_orientation` | Matching (complementarity) | Ordinal | Seeking, Balanced, Offering | Assumption (agreed with supervisor) |
| `psychosocial_isolation_score` | Matching (balanced) | Numeric, 20-80 | — | UCLA-derived construct (Russell, 1996); conditioned per NHS England (2026), Holt-Lunstad et al. (2015) |
| `engagement_level` | Matching (homogeneity) | Ordinal | Low, Medium, High | Assumption (agreed with supervisor) |

No integer age, ethnicity, region, communication modality, or safeguarding flag is generated (removed per sections 3.1–3.2).

---

## 6. Internal consistency rules

Enforced at generation time; a profile failing any rule is not produced.

1. **Duration fits the age band.** `condition_duration_band` must be one whose minimum years do not exceed the adult years available in the profile's age band.
2. **Sub-type belongs to its parent.** `primary_condition_subtype` is sampled only from its stated `primary_condition_category`'s members.
3. **Condition plausible for the band.** A condition cannot appear in a band younger than its minimum onset age (`MIN_ONSET_AGE`, band-level gate only, since no real age is generated).
4. **Comorbidity coherence.** Comorbidities are distinct from the primary condition and from each other, and their count matches `condition_count - 1`.
5. **Isolation score in range.** `psychosocial_isolation_score` is clamped to 20–80.
6. **Hard-rule readiness.** Every profile carries `age_band`, `primary_condition_category`, and `communication_language`, the fields the hard-rule filter needs.

The consistency audit in `data_generation.py` checks all six and should report zero violations on every run; a non-zero count indicates a generation bug, not a data-quality issue to tolerate.

---

## 7. Dataset size

See section 3.1 for the full reasoning. In summary: calibrate to the national LTC population (about 25 million people in England with an LTC, about 14 million with multiple; Valabhji et al., 2024), generate as large a representative pool as useful (cheap and linear), but run the matching evaluation, which is the O(n²) bottleneck, on samples in the low thousands to about 10,000 profiles, matched within eligible cohorts. The default in `generate_dataset.py` is 5,000 profiles per run, adjustable from the command line, with a `--replicates` option for generating multiple independent datasets for the statistical comparisons against baselines.

---

## 8. Validation methodology

`generate_dataset.py` produces a validation report for every run, covering:

- **Logical consistency** — the six rules in section 6, reported as violation counts (target: zero for all).
- **Distributional fidelity** — generated versus target proportions for `communication_language`, `gender`, and `age_band`, with a dependency-free chi-square goodness-of-fit statistic (no p-value, since scipy is deliberately not used; see section 9).
- **Association checks** — confirming the intended relationships are present, not just the marginal distributions: multimorbidity rate rising with age band, mean isolation score falling as IMD quintile rises (less deprived), mean isolation score higher when living alone, and the five most common conditions matching the expectation that anxiety or depression and painful condition sit near the top (Payne et al., 2020).

Before trusting any matching result, run the method on a small generated sample and confirm hard rules exclude who they should, groups fall within the target size range, and behaviour is sane before scaling up.

---

## 9. Software design

The generator is split into three files for readability and separation of concerns:

- **`schema.py`** — defines the attribute schema, the condition taxonomy, and every calibration constant, each with a one-line source citation. Contains no generation logic. This is the file to edit when a calibration figure changes.
- **`data_generation.py`** — implements the schema: samples one profile at a time, enforces the consistency rules, and provides the consistency audit. Imports `schema.py`.
- **`generate_dataset.py`** — the command-line entry point. Generates a dataset (or several replicate datasets), writes CSV or JSON output, and writes a validation report. Imports `data_generation.py`.

**No scipy dependency.** The distributional check uses a dependency-free chi-square goodness-of-fit statistic implemented directly with numpy; no p-value is computed. This keeps the toolchain to numpy, pandas, and optionally tabulate (for markdown table rendering in the report; the code falls back to plain text if tabulate is absent).

**Reproducibility.** Every generation call is seeded (`numpy.random.default_rng(seed)`); the same seed produces byte-identical output, confirmed by re-running the generator twice with the same seed and diffing the result.

---

## 10. Limitations to acknowledge in the dissertation

- **Entirely synthetic profiles.** No profile corresponds to a real person; no claim about real-world peer-support outcomes follows from this dataset.
- **Assumption-based matching attributes.** Support goal, support orientation, and engagement level have no population statistics and are generated from stated assumptions, agreed with the supervisor rather than derived from evidence. This is precisely why the weight sensitivity analysis (see the master design specification) is central, not optional.
- **Whole-population condition prevalences used as relative weights.** The CMS prevalences are whole-population, not LTC-population; see section 4.3.
- **Barnett et al. (2012) as a proxy for multimorbidity structure.** It is a 2007 Scotland dataset, all ages, 40 morbidities, used as the best available conditional target for a curated 11-condition, England-focused, adult-only dataset. The count distribution likely mildly overstates multimorbidity for the smaller curated set.
- **Age-band weights are informed, not directly sourced.** No single published table gives the age distribution of an LTC-only population for the exact bands used here; the weights are a defensible approximation shaped by the known multimorbidity/age gradient.
- **Living-alone rates by band are interpolated,** anchored to two Census 2021 data points (the 16–49 rate and the concentration of one-person households at 66+), not a full published by-band table.
- **UK, and in practice England, only.** The taxonomy, prevalences, and demographic anchors are England-specific and should not be presented as generalising elsewhere.
- **Weight validity remains the primary risk**, as stated in the original proposal: setting attribute weights without real patient data. This dataset does not remove that risk; it is mitigated by literature-grounded weights and the sensitivity analysis.

---

## 11. Outstanding items for supervisor sign-off

1. The parent-category mapping and exclusion list for the condition taxonomy (section 4.2).
2. The minimum onset ages used as band-eligibility gates (section 3.2).
3. The dataset-size reconciliation: national-scale calibration with matching evaluated on tractable samples (section 3.1, section 7), and the specific working sample size for the matching evaluation.
4. Confirmation that the assumption-based matching attributes (support goal, orientation, engagement level) are acceptable as stated assumptions rather than requiring further grounding.

---

## 12. References (APA 7)

Barnett, K., Mercer, S. W., Norbury, M., Watt, G., Wyke, S., & Guthrie, B. (2012). Epidemiology of multimorbidity and implications for health care, research, and medical education: A cross-sectional study. *The Lancet, 380*(9836), 37–43. https://doi.org/10.1016/S0140-6736(12)60240-2

Holt-Lunstad, J., Smith, T. B., Baker, M., Harris, T., & Stephenson, D. (2015). Loneliness and social isolation as risk factors for mortality: A meta-analytic review. *Perspectives on Psychological Science, 10*(2), 227–237. https://doi.org/10.1177/1745691614568352

Liu, P., Yuan, H., Ning, Y., Chakraborty, B., Liu, N., & Peres, M. A. (2024). A modified and weighted Gower distance-based clustering analysis for mixed type data: A simulation and empirical analyses. *BMC Medical Research Methodology, 24*(1), 305. https://doi.org/10.1186/s12874-024-02427-8

National Academies of Sciences, Engineering, and Medicine. (2020). *Social isolation and loneliness in older adults: Opportunities for the health care system.* The National Academies Press. https://doi.org/10.17226/25663

NHS England. (2026). *Health Survey for England, 2024: Loneliness and wellbeing.* NHS England Digital. https://digital.nhs.uk/data-and-information/publications/statistical/health-survey-for-england/2024

Office for National Statistics. (2022). *Language, England and Wales: Census 2021.* https://www.ons.gov.uk/peoplepopulationandcommunity/culturalidentity/language/bulletins/languageenglandandwales/census2021

Office for National Statistics. (2022). *Household and resident characteristics, England and Wales: Census 2021.* https://www.ons.gov.uk/peoplepopulationandcommunity/householdcharacteristics/homeinternetandsocialmediausage/bulletins/householdandresidentcharacteristicsenglandandwales/census2021

Office for National Statistics. (2023). *People's living arrangements in England and Wales: Census 2021.* https://www.ons.gov.uk/peoplepopulationandcommunity/householdcharacteristics/homeinternetandsocialmediausage/articles/livingarrangementsofpeopleinenglandandwales/census2021

Office for National Statistics. (2023). *Ethnic group, England and Wales: Census 2021.* https://www.ons.gov.uk/peoplepopulationandcommunity/culturalidentity/ethnicity/bulletins/ethnicgroupenglandandwales/census2021

Payne, R. A., Mendonca, S. C., Elliott, M. N., Saunders, C. L., Edwards, D. A., Marshall, M., & Roland, M. (2020). Development and validation of the Cambridge Multimorbidity Score. *Canadian Medical Association Journal, 192*(5), E107–E114. https://doi.org/10.1503/cmaj.190757

Russell, D. W. (1996). UCLA Loneliness Scale (Version 3): Reliability, validity, and factor structure. *Journal of Personality Assessment, 66*(1), 20–40. https://doi.org/10.1207/s15327752jpa6601_2

Schubert, E., & Rousseeuw, P. J. (2021). Fast and eager k-medoids clustering: O(k) runtime improvement of the PAM, CLARA, and CLARANS algorithms. *Information Systems, 101*, 101804. https://doi.org/10.1016/j.is.2021.101804

Valabhji, J., Barron, E., Pratt, A., Hafezparast, N., Dunbar-Rees, R., Bragan Turner, E., Roberts, K., Mathews, J., Deegan, R., Cornelius, V., Pickles, J., Wainman, G., Bakhai, C., Johnston, D. G., Gregg, E. W., & Khunti, K. (2024). Prevalence of multiple long-term conditions (multimorbidity) in England: A whole population study of over 60 million people. *Journal of the Royal Society of Medicine.* https://doi.org/10.1177/01410768231206033
