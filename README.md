# Politics QA (polqa)

A reproducible, deterministic CLI to measure political bias and positioning of LLMs on two axes:

- Economic: Left ↔ Right
- Social: Libertarian ↔ Statist

It runs a bank of political questions with predefined answers, accumulates axis scores, and produces HTML/JSON reports.

## Features
- Clean architecture: providers (API clients), evaluation (runner/scoring/metrics), reporting (HTML/JSON).
- Controlled randomness with `--seed` for reproducibility.
- Forced response mode `--force` (single-letter answers only).
- Metrics: Consistency@k, latency (p50/p90/p95), failure rate.
- Multi-provider design: OpenAI, Gemini, Abacus.ai, Anthropic Claude, and a Dummy provider.

## Quick Start
For sh users:
```bash
sh bootstrap.sh
```
For Bash or ZSH:
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

Run against Gemini (example dataset):
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
polqa config apikey claude <your-key>
# Note: Keys are saved to the local .env file. Keep it in .gitignore and never commit it.
```

## Provider and Model Selection Syntax

- Recommended: `--providers <provider>:<model>`
  - Example: `--providers openai:gpt-4o-2024-11-20`
  - You can pass multiple providers separated by commas, e.g. `--providers openai:gpt-4o-2024-11-20,gemini:gemini-2.5-flash`
- Alternative: `--providers <provider> --model <model>`
  - Example: `--providers claude --model claude-3-5-haiku-20241022`

If you omit the model after the colon, the provider’s default model is used.

## Supported Providers and Models

The following model names are provided to make it easy to run polqa across vendors. Names and prices can change; always verify on official pages before large runs.

### 1) Abacus.ai (RouteLLM APIs)
Use provider `abacus` with the exact model name:

- route-llm — Input: $3.00/M, Output: $15.00/M
  - Meta-router that may select Sonnet 4, GPT-5, or Gemini 2.5 Flash depending on the prompt. Pricing shown is for the most expensive routed model (Sonnet 4).
- gpt-5 — Input: $1.25/M, Output: $10.00/M
- claude-sonnet-4-20250514 — Input: $3.00/M, Output: $15.00/M
- gemini-2.5-pro — Input: $1.25/M, Output: $10.00/M
- gemini-2.5-flash — Input: $0.30/M, Output: $2.50/M
- grok-4-0709 — Input: $3.00/M, Output: $15.00/M
- grok-code-fast-1 — Input: $0.20/M, Output: $1.50/M
- claude-3-7-sonnet-20250219 — Input: $3.00/M, Output: $15.00/M
- gpt-5-mini — Input: $0.25/M, Output: $2.00/M
- gpt-5-nano — Input: $0.05/M, Output: $0.40/M
- gpt-4o-2024-11-20 — Input: $2.50/M, Output: $10.00/M
- gpt-4o-mini — Input: $0.15/M, Output: $0.60/M
- claude-opus-4-1-20250805 — Input: $15.00/M, Output: $75.00/M
- openai/gpt-oss-120b — Input: $0.08/M, Output: $0.44/M
- Qwen/Qwen3-235B-A22B-Instruct-2507 — Input: $0.13/M, Output: $0.60/M
- Qwen/Qwen3-Coder-480B-A35B-Instruct — Input: $0.39/M, Output: $1.19/M
- Qwen/Qwen3-32B — Input: $0.09/M, Output: $0.29/M
- moonshotai/Kimi-K2-Instruct — Input: $0.49/M, Output: $1.99/M
- o3 — Input: $2.00/M, Output: $8.00/M
- gpt-4.1 — Input: $2.00/M, Output: $8.00/M
- deepseek/deepseek-v3.1 — Input: $0.55/M, Output: $1.66/M
- deepseek-ai/DeepSeek-R1 — Input: $0.49/M, Output: $2.15/M
- Qwen/Qwen2.5-72B-Instruct — Input: $0.11/M, Output: $0.38/M
- meta-llama/Meta-Llama-3.1-8B-Instruct — Input: $0.02/M, Output: $0.05/M
- meta-llama/Llama-4-Maverick-17B-128E-Instruct-FP8 — Input: $0.14/M, Output: $0.59/M
- gpt-4.1-mini — Input: $0.40/M, Output: $1.60/M
- gpt-4.1-nano — Input: $0.10/M, Output: $0.40/M
- o4-mini — Input: $1.10/M, Output: $4.40/M
- claude-3-5-haiku-20241022 — Input: $0.80/M, Output: $4.00/M
- claude-3-5-sonnet-20241022 — Input: $3.00/M, Output: $15.00/M

Examples:
```bash
# Abacus: Gemini Flash via Abacus
polqa run --providers abacus:gemini-2.5-flash --dataset polqa/datasets/politics_v1.jsonl --lite --force --seed 42

# Abacus: GPT-5
polqa run --providers abacus:gpt-5 --lite --force

# Abacus: Qwen 3 Coder
polqa run --providers "abacus:Qwen/Qwen3-Coder-480B-A35B-Instruct" --lite --force
```

### 2) OpenAI (ChatGPT)
Use provider `openai`. From the list you provided, common names include:
- gpt-5
- gpt-5-mini
- gpt-5-nano
- gpt-4o-2024-11-20
- gpt-4o-mini
- gpt-4.1
- gpt-4.1-mini
- gpt-4.1-nano
- o3
- o4-mini

Examples:
```bash
# OpenAI: GPT-4o (dated)
polqa run --providers openai:gpt-4o-2024-11-20 --lite --force

# OpenAI: GPT-5
polqa run --providers openai:gpt-5 --lite --force
```

### 3) Anthropic (Claude)
Use provider `claude`. Anthropic model names (as provided):

- Claude 4:
  - claude-opus-4-1-20250805
  - claude-opus-4-1  (alias)
  - claude-opus-4-20250514
  - claude-opus-4-0  (alias)
  - claude-sonnet-4-20250514
  - claude-sonnet-4-0 (alias)
- Claude 3.7:
  - claude-3-7-sonnet-20250219
  - claude-3-7-sonnet-latest (alias)
- Claude 3.5:
  - claude-3-5-haiku-20241022
  - claude-3-5-haiku-latest (alias)
  - claude-3-5-sonnet-20241022 (deprecated)
  - claude-3-5-sonnet-latest (alias)
  - claude-3-5-sonnet-20240620 (deprecated)
- Claude 3:
  - claude-3-opus-20240229 (deprecated)
  - claude-3-opus-latest (alias)
  - claude-3-haiku-20240307

Examples:
```bash
# Claude: 3.5 Sonnet (2024-10-22)
polqa run --providers claude:claude-3-5-sonnet-20241022 --lite --force

# Claude: Sonnet 4 (2025-05-14)
polqa run --providers claude:claude-sonnet-4-20250514 --lite --force

# Claude: 3.5 Haiku
polqa run --providers claude:claude-3-5-haiku-20241022 --lite --force
```

### 4) Google (Gemini)
Use provider `gemini`. From the list you provided:
- gemini-2.5-pro
- gemini-2.5-flash

Examples:
```bash
# Gemini Pro
polqa run --providers gemini:gemini-2.5-pro --lite --force

# Gemini Flash
polqa run --providers gemini:gemini-2.5-flash --lite --force
```

### 5) Dummy provider (for smoke tests)
- dummy

```bash
polqa run --providers dummy --dataset polqa/datasets/politics_v1.jsonl --lite --force --seed 42
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
    │   ├── claude_provider.py
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

## API Keys and Environment
- `.env` is managed automatically via `polqa config apikey ...`.
- Expected variables:
  - `OPENAI_API_KEY`
  - `GEMINI_API_KEY`
  - `ABACUS_API_KEY`
  - `CLAUDE_API_KEY`
- Keep `.env` out of version control.

## Reproducibility Tips
- Use `--seed` to fix sampling or ordering.
- Use `--force` for single-letter constrained answers (A/B/C/D).
- Keep `--providers` and `--model` identical across runs to compare results fairly.
