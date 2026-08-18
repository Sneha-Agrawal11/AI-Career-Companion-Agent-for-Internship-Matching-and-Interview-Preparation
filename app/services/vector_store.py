"""FAISS-based vector store for internship retrieval."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import faiss
import numpy as np

from app.services.embedding_service import get_embedding_service

APP_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = APP_DIR / "data"
INTERNSHIP_DATA_FILE = DATA_DIR / "internships.json"
VECTOR_STORE_DIR = DATA_DIR / "vector_store"
INDEX_FILE = VECTOR_STORE_DIR / "internships.index"
METADATA_FILE = VECTOR_STORE_DIR / "internship_metadata.json"


def internship_to_embedding_text(internship: dict[str, Any]) -> str:
    """Build normalized text used for internship embeddings."""
    sections = [
        f"Title: {internship.get('title', '')}",
        f"Company: {internship.get('company', '')}",
        f"Domain: {internship.get('domain', '')}",
        f"Description: {internship.get('description', '')}",
        f"Required Skills: {', '.join(internship.get('required_skills', []))}",
        f"Preferred Skills: {', '.join(internship.get('preferred_skills', []))}",
        f"Education Requirements: {internship.get('education_requirements', '')}",
        f"Experience Requirements: {internship.get('experience_requirements', '')}",
        f"Responsibilities: {'; '.join(internship.get('responsibilities', []))}",
        f"Eligibility: {internship.get('eligibility', '')}",
        f"Location: {internship.get('location', '')}",
        f"Work Mode: {internship.get('work_mode', '')}",
        f"Duration: {internship.get('duration', '')}",
    ]
    return "\n".join(item for item in sections if item.split(": ", 1)[1])


def _read_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8-sig") as file:
        return json.load(file)


def load_internships() -> list[dict[str, Any]]:
    """Load internship records from JSON file."""
    if not INTERNSHIP_DATA_FILE.exists():
        raise FileNotFoundError(
            f"Internship dataset not found at {INTERNSHIP_DATA_FILE}."
        )

    records = _read_json(INTERNSHIP_DATA_FILE)
    if not isinstance(records, list):
        raise ValueError("Internship dataset must be a list of objects.")
    return records


def get_internship_by_id(internship_id: int) -> dict[str, Any] | None:
    for internship in load_internships():
        if internship.get("id") == internship_id:
            return internship
    return None


def build_and_save_index(force_rebuild: bool = True) -> dict[str, Any]:
    """Build the FAISS index and persist index plus metadata files."""
    internships = load_internships()
    if not internships:
        raise ValueError("Internship dataset is empty.")

    VECTOR_STORE_DIR.mkdir(parents=True, exist_ok=True)

    texts = [internship_to_embedding_text(item) for item in internships]
    embedding_service = get_embedding_service()
    embeddings = embedding_service.encode_texts(texts)

    dimension = embeddings.shape[1]
    index = faiss.IndexFlatIP(dimension)
    index.add(embeddings)

    if force_rebuild or not INDEX_FILE.exists():
        faiss.write_index(index, str(INDEX_FILE))

    metadata = {
        "embedding_model": embedding_service.model_name,
        "dimension": dimension,
        "count": len(internships),
        "items": internships,
    }

    with METADATA_FILE.open("w", encoding="utf-8") as file:
        json.dump(metadata, file, indent=2)

    return {
        "index_path": str(INDEX_FILE),
        "metadata_path": str(METADATA_FILE),
        "records_indexed": len(internships),
        "dimension": dimension,
    }


def load_index_and_metadata() -> tuple[faiss.Index, dict[str, Any]]:
    """Load FAISS index and metadata from disk."""
    if not INDEX_FILE.exists() or not METADATA_FILE.exists():
        raise FileNotFoundError(
            "Vector store files not found. Build index first using /internships/build-index."
        )

    index = faiss.read_index(str(INDEX_FILE))
    metadata = _read_json(METADATA_FILE)
    return index, metadata


def search_internships(candidate_embedding: np.ndarray, top_k: int = 5) -> list[dict[str, Any]]:
    """Search top-K similar internships using cosine similarity in FAISS."""
    index, metadata = load_index_and_metadata()

    top_k = max(1, min(top_k, 10))
    query = np.asarray(candidate_embedding, dtype=np.float32).reshape(1, -1)

    scores, indices = index.search(query, top_k)

    items = metadata.get("items", [])
    results: list[dict[str, Any]] = []
    for score, idx in zip(scores[0], indices[0]):
        if idx < 0 or idx >= len(items):
            continue
        results.append(
            {
                "internship": items[idx],
                "semantic_similarity": float(score),
            }
        )

    return results
