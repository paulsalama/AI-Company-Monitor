from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Tuple

import yaml


def repo_root() -> Path:
  """Return repository root (two levels up from this file)."""
  return Path(__file__).resolve().parents[2]


def load_yaml(path: Path) -> Dict[str, Any]:
  with path.open("r", encoding="utf-8") as f:
    return yaml.safe_load(f) or {}


def load_sources_and_keywords(
  sources_path: Path | None = None, keywords_path: Path | None = None
) -> Tuple[Dict[str, Any], Dict[str, Any]]:
  root = repo_root()
  sources_path = sources_path or root / "config" / "sources.yaml"
  keywords_path = keywords_path or root / "config" / "keywords.yaml"

  if not sources_path.exists():
    raise FileNotFoundError(f"Missing sources config at {sources_path}")
  if not keywords_path.exists():
    raise FileNotFoundError(f"Missing keywords config at {keywords_path}")

  return load_yaml(sources_path), load_yaml(keywords_path)


def ensure_data_dirs() -> Path:
  """
  Create data directories if they don't exist and return the data root path.
  """
  root = repo_root()
  data_root = root / "data"
  for child in ["snapshots", "reports", "models"]:
    (data_root / child).mkdir(parents=True, exist_ok=True)
  return data_root


def default_db_path() -> Path:
  return repo_root() / "data" / "monitor.db"


def to_json(obj: Any) -> str:
  """Helper to store JSON fields as strings."""
  return json.dumps(obj, ensure_ascii=False)
