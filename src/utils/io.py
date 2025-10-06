import os
import json
from typing import Any, Dict

import yaml


def ensure_dir(path: str) -> None:
	if path and not os.path.exists(path):
		os.makedirs(path, exist_ok=True)


def load_yaml(path: str) -> Dict[str, Any]:
	with open(path, "r", encoding="utf-8") as f:
		return yaml.safe_load(f)


def save_json(data: Dict[str, Any], path: str) -> None:
	ensure_dir(os.path.dirname(path))
	with open(path, "w", encoding="utf-8") as f:
		json.dump(data, f, indent=2)


