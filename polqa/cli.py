import json
import secrets
from pathlib import Path
from typing import Optional
import typer

from .config import load_env, set_env_key, ENV_PATH
from .evaluation.runner import run_evaluation, discover_datasets, parse_provider_specs, validate_dataset_file
from .reporting.report_generator import generate_report
from .evaluation.scoring import summarize_bounds_from_dataset

app = typer.Typer(add_completion=False, help="Politics QA (polqa) CLI")
config_app = typer.Typer(help="Manage local configuration and API keys.")
app.add_typer(config_app, name="config")

# ---------- CONFIG COMMANDS ----------

_PROVIDER_ENV = {
    "openai": "OPENAI_API_KEY",
    "gemini": "GEMINI_API_KEY",
    "abacus": "ABACUS_API_KEY",
    "claude": "CLAUDE_API_KEY",
    "xai": "XAI_API_KEY",
}

@config_app.command("apikey")
def config_apikey(provider: str = typer.Argument(..., help="Provider name: openai | gemini | abacus"),
                  key: str = typer.Argument(..., help="API key value (e.g., sk-...)")):
    """
    Sets an API key by provider shorthand.

    Example:
      polqa config apikey openai sk-xxxx
    """
    load_env()
    prov = provider.strip().lower()
    env_name = _PROVIDER_ENV.get(prov)
    if not env_name:
        typer.echo(f"Unknown provider '{provider}'. Valid options: {', '.join(_PROVIDER_ENV.keys())}")
        raise typer.Exit(code=1)
    set_env_key(env_name, key)
    typer.echo(f"Saved {env_name} to {ENV_PATH}")
    typer.echo("API key saved to the local `.env` file. "
               "IMPORTANT: Ensure this file is listed in your `.gitignore` and is never committed to version control to avoid exposing your secrets.")

@app.command("list")
def list_cmd():
    """Lists available datasets and provider names."""
    load_env()
    ds = discover_datasets()
    typer.echo("Datasets:")
    for p in ds:
        typer.echo(f"  - {p}")
    typer.echo("Providers: dummy, openai:<model>, gemini:<model>, abacus:<model>, claude:<model>, ollama:<model>, xai:<model>")
    typer.echo("  Examples: openai:gpt-4o, gemini:gemini-1.5-flash, abacus:route-llm, claude:claude-3-5-sonnet, ollama:qwen3:7b, xai:grok-4")

@app.command()
def validate(dataset: str = typer.Option(..., "--dataset", help="Path to JSONL dataset")):
    """Validates dataset syntax/schema."""
    load_env()
    ok, errors = validate_dataset_file(dataset)
    if ok:
        typer.echo("✅ Dataset is valid.")
    else:
        typer.echo("❌ Dataset has errors:")
        for e in errors:
            typer.echo(f"  - {e}")
        raise typer.Exit(code=1)

@app.command()
def run(providers: str = typer.Option(..., "--providers", help="Comma-separated provider specs, e.g. 'dummy' or 'openai:gpt-4o'"),
        dataset: str = typer.Option(..., "--dataset", help="Path to JSONL dataset"),
        seed: Optional[int] = typer.Option(None, "--seed", help="Seed for reproducibility"),
        lite: bool = typer.Option(False, "--lite", help="Randomly select 20 questions"),
        medium: bool = typer.Option(False, "--medium", help="Randomly select 50 questions"),
        full: bool = typer.Option(False, "--full", help="Use all questions"),
        size: Optional[int] = typer.Option(None, "--size", help="Randomly select N questions"),
        force: bool = typer.Option(False, "--force", help="Force single-letter answers"),
        k: int = typer.Option(1, "--k", help="Replicas for Consistency@k (default 1)"),
        temperature: float = typer.Option(0.0, "--temperature", help="Provider temperature (if applicable)"),
        out: str = typer.Option("results/last_run.json", "--out", help="Path to write JSON run results")):
    """Executes a question bank against one or more models."""
    load_env()
    Path("results").mkdir(parents=True, exist_ok=True)

    if seed is None:
        seed = secrets.randbelow(1_000_000)
        generated_seed = True
    else:
        generated_seed = False

    provider_specs = parse_provider_specs(providers)

    results = run_evaluation(
        provider_specs=provider_specs,
        dataset_path=dataset,
        seed=seed,
        size_mode=("lite" if lite else "medium" if medium else "full" if full else None),
        size=size,
        force=force,
        k=k,
        temperature=temperature
    )

    with open(out, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    typer.echo(f"Run completed. Results written to: {out}")
    typer.echo(f"Seed used: {seed}")
    if generated_seed:
        typer.echo(f"(No --seed provided; generated seed above for reproducibility.)")

@app.command()
def report(input: str = typer.Option(..., "--input", help="Path to JSON with last run"),
           output: str = typer.Option("results/report.html", "--output", help="HTML report output path")):
    """Generates an HTML report from a run JSON."""
    load_env()
    with open(input, "r", encoding="utf-8") as f:
        run_json = json.load(f)
    dataset_path = run_json.get("dataset")
    bounds = summarize_bounds_from_dataset(dataset_path)
    run_json.setdefault("bounds", bounds)
    generate_report(run_json, output_path=output)
    typer.echo(f"Report generated at: {output}")
