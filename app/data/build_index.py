"""Utility script to build FAISS internship index from internships.json."""

from __future__ import annotations

import sys
from pathlib import Path

# Ensure project root is importable when script is executed directly.
ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.services.vector_store import build_and_save_index


def main() -> None:
    result = build_and_save_index(force_rebuild=True)
    print("Internship index build completed")
    print(result)


if __name__ == "__main__":
    main()
