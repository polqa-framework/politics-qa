import os
from pathlib import Path
from dotenv import load_dotenv

ENV_PATH = Path(".env")

def load_env():
    if ENV_PATH.exists():
        load_dotenv(dotenv_path=ENV_PATH)

def set_env_key(key: str, value: str):
    lines = []
    if ENV_PATH.exists():
        with open(ENV_PATH, "r", encoding="utf-8") as f:
            lines = f.read().splitlines()
    found = False
    new_lines = []
    for line in lines:
        if line.startswith(f"{key}="):
            new_lines.append(f"{key}={value}")
            found = True
        else:
            new_lines.append(line)
    if not found:
        new_lines.append(f"{key}={value}")
    with open(ENV_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(new_lines))
