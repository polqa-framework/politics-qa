from typing import Dict

def build_prompt(q: Dict, force: bool = False) -> str:
    lines = [f"Question: {q['prompt']}", "Options:"]
    for key in sorted(q["options"].keys()):
        text = q["options"][key]["text"]
        lines.append(f"{key}) {text}")
    if force:
        allowed = ", ".join([k for k in sorted(q["options"].keys())])
        lines.append(f"Respond only with the letter of your choice ({allowed}). Do not include any other text, explanation, or punctuation.")
    return "\n".join(lines)
