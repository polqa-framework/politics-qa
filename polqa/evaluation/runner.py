import json
import re
import time
import random
from pathlib import Path
from typing import Dict, List, Tuple, Optional

from .prompt_builder import build_prompt
from .metrics import summarize_run_metrics
from .scoring import accumulate_scores, classify, summarize_bounds_from_dataset

LETTER_RE = re.compile(r"\b([A-Z])\b")

def parse_provider_specs(specs: str) -> List[Dict]:
    out = []
    for raw in [s.strip() for s in specs.split(",") if s.strip()]:
        if ":" in raw:
            name, model = raw.split(":", 1)
            out.append({"name": name.strip().lower(), "model": model.strip()})
        else:
            out.append({"name": raw.strip().lower(), "model": None})
    return out

def discover_datasets() -> List[str]:
    base = Path("polqa/datasets")
    if not base.exists():
        return []
    return sorted([str(p) for p in base.glob("*.jsonl")])

def load_dataset(path: str) -> List[Dict]:
    rows = []
    with open(path, "r", encoding="utf-8") as f:
        for i, line in enumerate(f, 1):
            line = line.strip()
            if not line: continue
            try:
                obj = json.loads(line)
                rows.append(obj)
            except Exception as e:
                raise ValueError(f"Invalid JSON at line {i}: {e}")
    if not rows:
        raise ValueError("Dataset empty")
    return rows

def validate_dataset_file(path: str):
    errors = []
    try:
        rows = load_dataset(path)
    except Exception as e:
        return False, [str(e)]
    required_q_fields = {"id", "prompt", "options"}
    for idx, q in enumerate(rows, 1):
        missing = required_q_fields - set(q.keys())
        if missing:
            errors.append(f"Line {idx}: missing fields {missing}")
            continue
        if not isinstance(q["options"], dict) or not q["options"]:
            errors.append(f"Line {idx}: 'options' must be non-empty object")
            continue
        for key, opt in q["options"].items():
            if "text" not in opt or "scores" not in opt:
                errors.append(f"Line {idx}: option {key} missing 'text' or 'scores'")
                continue
            sc = opt["scores"]
            if not (isinstance(sc, dict) and "economic" in sc and "social" in sc):
                errors.append(f"Line {idx}: option {key} 'scores' must contain 'economic' and 'social'")
                continue
            try:
                int(sc["economic"]); int(sc["social"])
            except:
                errors.append(f"Line {idx}: scores for option {key} must be integers")
    return (len(errors) == 0), errors

def get_provider_instance(spec: Dict, temperature: float = 0.0):
    name = spec["name"]
    model = spec.get("model")
    if name == "dummy":
        from ..providers.dummy_provider import DummyProvider
        return DummyProvider(model=model, temperature=temperature)
    elif name == "openai":
        from ..providers.openai_provider import OpenAIProvider
        return OpenAIProvider(model=model or "gpt-4o", temperature=temperature)
    elif name == "gemini":
        from ..providers.gemini_provider import GeminiProvider
        return GeminiProvider(model=model or "gemini-1.5-flash", temperature=temperature)
    elif name == "abacus":
        from ..providers.abacus_provider import AbacusProvider
        return AbacusProvider(model=model or "route-llm", temperature=temperature)
    else:
        raise ValueError(f"Unknown provider: {name}")

def select_questions(rows: List[Dict], size_mode: Optional[str], size: Optional[int], rng: random.Random) -> List[Dict]:
    if size_mode == "lite":
        n = min(20, len(rows))
    elif size_mode == "medium":
        n = min(50, len(rows))
    elif size_mode == "full":
        n = len(rows)
    elif size is not None:
        n = min(int(size), len(rows))
    else:
        n = len(rows)
    indices = list(range(len(rows)))
    rng.shuffle(indices)
    return [rows[i] for i in indices[:n]]

def parse_letter(text: str, valid_letters: List[str]) -> Optional[str]:
    if not text:
        return None
    t = text.strip().upper()
    if len(t) == 1 and t in valid_letters:
        return t
    m = LETTER_RE.search(t)
    if m:
        letter = m.group(1)
        if letter in valid_letters:
            return letter
    return None

def run_once(provider, questions: List[Dict], force: bool, rng: random.Random):
    answers = []
    latencies = []
    failures = 0
    for q in questions:
        prompt = build_prompt(q, force=force)
        valid_letters = sorted(q["options"].keys())
        t0 = time.perf_counter()
        try:
            raw = provider.generate(prompt)
        except Exception:
            raw = ""
        dt = time.perf_counter() - t0
        latencies.append(dt)
        letter = parse_letter(raw, valid_letters)
        if letter is None:
            failures += 1
        else:
            answers.append((q, letter))
    return answers, latencies, failures

def run_evaluation(provider_specs: List[Dict], dataset_path: str, seed: int,
                   size_mode: Optional[str], size: Optional[int],
                   force: bool, k: int, temperature: float):
    rng = random.Random(seed)
    rows = load_dataset(dataset_path)
    questions = select_questions(rows, size_mode=size_mode, size=size, rng=rng)

    models_out = []
    for spec in provider_specs:
        provider = get_provider_instance(spec, temperature=0.0)
        model_name = f"{spec['name']}:{spec['model']}" if spec.get("model") else spec["name"]

        ans1, lat1, fail1 = run_once(provider, questions, force=force, rng=rng)
        final_scores = accumulate_scores(ans1)
        classification = classify(final_scores)

        consistent = 0
        total_comparable = 0
        all_lat = list(lat1)
        total_fail = fail1

        if k > 1:
            baseline = {q["id"]: letter for q, letter in ans1}
            for rep in range(1, k):
                rng_rep = random.Random(seed + rep)
                ansR, latR, failR = run_once(provider, questions, force=force, rng=rng_rep)
                all_lat.extend(latR)
                total_fail += failR
                current = {q["id"]: letter for q, letter in ansR}
                keys = set(baseline.keys()) & set(current.keys())
                total_comparable += len(keys)
                for qid in keys:
                    if baseline[qid] == current[qid]:
                        consistent += 1

        consistency_at_k = (consistent / total_comparable) if total_comparable > 0 and k > 1 else 1.0
        metrics = summarize_run_metrics(all_lat, total_fail, len(questions) * k, consistency_at_k)

        models_out.append({"model": model_name,
                           "final_scores": final_scores,
                           "classification": classification,
                           "metrics": metrics})

    return {"seed": seed, "dataset": dataset_path, "total_questions": len(questions),
            "models": models_out, "bounds": summarize_bounds_from_dataset(dataset_path)}
