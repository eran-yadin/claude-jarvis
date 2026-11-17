"""Loads config.yaml + secrets.env. Everything else imports settings from here."""
import os
from pathlib import Path

import yaml
from dotenv import load_dotenv

DATA_DIR = Path(os.environ.get("JARVIS_DATA", Path(__file__).resolve().parent.parent / "jarvis-data"))

load_dotenv(DATA_DIR / "secrets.env")

with open(DATA_DIR / "config.yaml", encoding="utf-8") as f:
    CONFIG = yaml.safe_load(f)

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
JARVIS_TOKEN = os.environ.get("JARVIS_TOKEN", "")
