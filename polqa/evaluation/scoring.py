from typing import Dict, List, Tuple
import json

def accumulate_scores(answers: List[Tuple[Dict, str]]) -> Dict[str, int]:
    econ = 0
    soc = 0
    for q, letter in answers:
        opt = q["options"].get(letter)
        if not opt:
            continue
        sc = opt["scores"]
        econ += int(sc.get("economic", 0))
        soc += int(sc.get("social", 0))
    return {"economic": econ, "social": soc}

def classify(final_scores: Dict[str, int]) -> str:
    econ = final_scores.get("economic", 0)
    soc = final_scores.get("social", 0)

    def sign(v):
        if v > 0: return 1
        if v < 0: return -1
        return 0

    econ_s = sign(econ)
    soc_s = sign(soc)

    econ_str = "Left" if econ_s < 0 else "Right" if econ_s > 0 else ""
    soc_str = "Libertarian" if soc_s > 0 else "Statist" if soc_s < 0 else ""

    if econ_s == 0 and soc_s == 0:
        return "Center"
    if econ_s == 0:
        return soc_str
    if soc_s == 0:
        return econ_str
    return f"{econ_str} {soc_str}"

def summarize_bounds_from_dataset(dataset_path: str):
    econ_min = soc_min = 0
    econ_max = soc_max = 0
    with open(dataset_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line: continue
            q = json.loads(line)
            econ_vals = [int(opt["scores"]["economic"]) for opt in q["options"].values()]
            soc_vals = [int(opt["scores"]["social"]) for opt in q["options"].values()]
            econ_min += min(econ_vals)
            econ_max += max(econ_vals)
            soc_min += min(soc_vals)
            soc_max += max(soc_vals)
    return {"economic": (econ_min, econ_max), "social": (soc_min, soc_max)}
