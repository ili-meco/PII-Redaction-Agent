# env_loader.py
# Minimal .env loader (no external dependency). Loads KEY=VALUE pairs into os.environ.
import os
from pathlib import Path

def load_dotenv(dotenv_path: str = None):
    if dotenv_path is None:
        # Try multiple possible locations for PII detection folder
        possible_paths = [
            "../../../config/.env",
            ".env",
            "config/.env",
            "../config/.env"
        ]
        dotenv_path = None
        for path in possible_paths:
            if Path(path).exists():
                dotenv_path = path
                break
        if dotenv_path is None:
            return
    
    p = Path(dotenv_path)
    if not p.exists():
        return
    for raw in p.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        k, v = line.split("=", 1)
        k = k.strip()
        v = v.strip().strip("'").strip('"')
        if k and v:  # Remove the "and k not in os.environ" condition
            os.environ[k] = v
