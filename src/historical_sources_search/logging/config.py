import json
from pathlib import Path

with open(Path(__file__).parent / "config-dict.json") as f:
    LOGGING_CONFIG_DICT = json.load(f)
