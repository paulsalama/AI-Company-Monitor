from __future__ import annotations

import difflib
from pathlib import Path


def diff_text(prev: Path, curr: Path) -> str:
  prev_lines = prev.read_text(encoding="utf-8").splitlines()
  curr_lines = curr.read_text(encoding="utf-8").splitlines()
  return "\n".join(difflib.unified_diff(prev_lines, curr_lines, fromfile=str(prev), tofile=str(curr)))
