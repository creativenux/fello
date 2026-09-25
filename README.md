# Peer Matching For People with LTC

The purpose of this research is to investigate whether a rules-based multi-attribute matching system can help form more compatible and supportive peer groups for people with long-term health conditions. It is motivated by the growing need for safe, structured peer support systems that reduce isolation and improve ongoing social support outside formal healthcare settings

## Project layout

```
fello/
├── dataset_generation/   synthetic data generator (schema, generation, validation report, figures)
├── matching/             matching engine: hard rules, weighted Gower, group assembly, baselines, explanations
├── tests/                unit and end-to-end tests
├── output/               every result lands here, so any part of the project can read it
│   ├── n<n>/             datasets of size n: profiles_seed<seed>.csv, validation report, figures
│   └── matching/         matching results: matching_n<n>_seed<seed>.json
├── paths.py              the single definition of these locations
├── run_matching.py       command-line matching runner
└── DECISIONS.md          design decisions and judgement calls
```

## How to run

```bash
pip3 install -r requirements.txt

# 1. Generate a dataset (writes to output/n3000/)
python3 dataset_generation/generate_dataset.py --n 3000 --seed 42

# 2. Match it with the full method and every baseline (reads output/n3000/, writes output/matching/)
python3 run_matching.py --n 3000 --seed 42

# Tests
python3 -m pytest
```
