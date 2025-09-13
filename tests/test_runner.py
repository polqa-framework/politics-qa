from polqa.evaluation.runner import parse_provider_specs, select_questions
import random

def test_parse_provider_specs():
    specs = parse_provider_specs("dummy, openai:gpt-4o, gemini:gemini-1.5-flash")
    assert specs[0]["name"] == "dummy"
    assert specs[1]["name"] == "openai" and specs[1]["model"] == "gpt-4o"
    assert specs[2]["name"] == "gemini"

def test_select_questions_deterministic():
    rows = [{"id": str(i), "prompt":"","options":{"A":{"text":"","scores":{"economic":0,"social":0}}}} for i in range(100)]
    rng = random.Random(42)
    sel1 = select_questions(rows, size_mode="lite", size=None, rng=rng)
    rng = random.Random(42)
    sel2 = select_questions(rows, size_mode="lite", size=None, rng=rng)
    assert [r["id"] for r in sel1] == [r["id"] for r in sel2]
    assert len(sel1) == 20
