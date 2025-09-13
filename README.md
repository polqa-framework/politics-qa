# Politics QA (polqa)

A reproducible, deterministic CLI to measure **political bias and positioning** of LLMs on two axes:

- **Economic**: Left ↔ Right  
- **Social**: Libertarian ↔ Statist

It runs a bank of political questions with predefined answers, accumulates axis scores, and produces HTML/JSON reports.

## Features
- Clean architecture: **providers** (API clients), **evaluation** (runner/scoring/metrics), **reporting** (HTML/JSON).
- Controlled randomness with `--seed` for reproducibility.
- Forced response mode `--force` (single-letter answers only).
- Metrics: Consistency@k, latency (p50/p90/p95), failure rate.
- Multi-provider design: OpenAI, Gemini, Abacus.ai, and a Dummy provider.

## Quick Start
For sh users
```bash
sh bootstrap.sh
```
In case you use Bash or ZSH
```bash
bash bootstrap.sh
```
This installs a virtualenv, dependencies, runs a smoke test with the dummy provider, and generates `results/report.html`.

## Manual Usage
Activate the venv if you used `bootstrap.sh`:
```bash
source .venv/bin/activate
```

List datasets and providers:
```bash
polqa list
```

Run against gemini (example dataset):
```bash
polqa run --providers gemini:gemini-2.5-flash --dataset polqa/datasets/politics_v1.jsonl --lite --force --seed 42
```

Generate a report from the last run:
```bash
polqa report --input results/last_run.json --output results/report.html
```

Validate a dataset file:
```bash
polqa validate --dataset polqa/datasets/politics_v1.jsonl
```

Configure API keys (saved to `.env`):
```bash
polqa config apikey openai <your-key>

polqa config apikey gemini <your-key>

polqa config apikey abacus <your-key>

# Legend: API key saved to the local `.env` file. IMPORTANT: Ensure this file is in .gitignore and never committed.
```

## Project Structure
```
politics-qa/
├── README.md
├── LICENSE
├── .env.example
├── .gitignore
├── bootstrap.sh
├── pyproject.toml
└── polqa/
    ├── __init__.py
    ├── __main__.py
    ├── cli.py
    ├── config.py
    ├── datasets/
    │   └── politics_v1.jsonl
    ├── evaluation/
    │   ├── runner.py
    │   ├── scoring.py
    │   ├── metrics.py
    │   └── prompt_builder.py
    ├── providers/
    │   ├── base.py
    │   ├── openai_provider.py
    │   ├── gemini_provider.py
    │   ├── abacus_provider.py
    │   └── dummy_provider.py
    └── reporting/
        ├── report_generator.py
        └── templates/
            ├── report.html.j2
            └── styles.css
tests/
    ├── test_scoring.py
    ├── test_runner.py
    └── test_force_mode.py
results/
```
