"""Chroma vector store over packaged attack corpus; ingest + retrieval for LLM grounding."""

from __future__ import annotations

import hashlib
import os
import re
import threading
from pathlib import Path
from typing import Any

from nids_explain.config import (
    RAG_EMBEDDING_MODEL,
    RAG_PERSIST_DIR,
    RAG_TOP_K,
    RAG_TOP_K_FILTERED,
)

_CORPUS_DIR = Path(__file__).resolve().parent / "rag_corpus"
_COLLECTION_NAME = "nids_attack_corpus"
_FINGERPRINT_FILE = "corpus_fingerprint.txt"

_FILENAME_TO_FAMILY: dict[str, str] = {
    "benign": "BENIGN",
    "brute_force": "BRUTE_FORCE",
    "ddos": "DDOS",
    "dos": "DOS",
    "mirai": "MIRAI",
    "recon": "RECON",
    "spoofing": "SPOOFING",
    "web_attack": "WEB_ATTACK",
}

_lock = threading.Lock()
_client_bundle: tuple[Any, Any, str] | None = None


def _slug(s: str) -> str:
    s = re.sub(r"[^\w\s-]", "", s, flags=re.ASCII)
    s = re.sub(r"[-\s]+", "-", s).strip("-").lower()
    return s[:80] or "section"


def corpus_fingerprint(corpus_dir: Path) -> str:
    """Hash of corpus markdown for automatic re-ingest after edits."""
    h = hashlib.sha256()
    for path in sorted(corpus_dir.glob("*.md")):
        h.update(path.name.encode())
        h.update(path.read_bytes())
    return h.hexdigest()[:32]


def _parse_markdown_corpus(corpus_dir: Path) -> list[dict[str, str]]:
    """Split each *.md by ## headings into retrieval chunks."""
    chunks: list[dict[str, str]] = []
    if not corpus_dir.is_dir():
        return chunks

    for path in sorted(corpus_dir.glob("*.md")):
        stem = path.stem.lower()
        family = _FILENAME_TO_FAMILY.get(stem)
        if not family:
            continue
        raw = path.read_text(encoding="utf-8")
        sections: list[tuple[str, str]] = []
        current_heading = "Introduction"
        current_lines: list[str] = []

        for line in raw.splitlines():
            if line.startswith("## ") and line[3:].strip():
                body = "\n".join(current_lines).strip()
                if body:
                    sections.append((current_heading, body))
                current_heading = line[3:].strip()
                current_lines = []
                continue
            current_lines.append(line)

        tail = "\n".join(current_lines).strip()
        if tail:
            sections.append((current_heading, tail))

        for heading, body in sections:
            if not body.strip():
                continue
            cid = f"{stem}-{_slug(heading)}"
            embed_text = (
                f"Attack coarse class: {family}. Section: {heading}.\n\n{body.strip()}"
            )
            chunks.append(
                {
                    "id": cid,
                    "attack_family": family,
                    "section": heading[:200],
                    "text": embed_text,
                }
            )

    return chunks


def _get_embedding_fn():
    from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction

    return SentenceTransformerEmbeddingFunction(model_name=RAG_EMBEDDING_MODEL)


def _ensure_bundle():
    """Lazily open Chroma, ingest or refresh corpus if fingerprint changed."""
    global _client_bundle
    with _lock:
        fp = corpus_fingerprint(_CORPUS_DIR)
        force_rebuild = os.environ.get("RAG_FORCE_REBUILD", "").strip().lower() in (
            "1",
            "true",
            "yes",
        )
        if (
            _client_bundle is not None
            and len(_client_bundle) == 3
            and _client_bundle[2] == fp
            and not force_rebuild
        ):
            return _client_bundle[0], _client_bundle[1]

        from chromadb import PersistentClient

        RAG_PERSIST_DIR.mkdir(parents=True, exist_ok=True)
        ef = _get_embedding_fn()
        client = PersistentClient(path=str(RAG_PERSIST_DIR))

        chunk_rows = _parse_markdown_corpus(_CORPUS_DIR)
        if not chunk_rows:
            raise RuntimeError(f"No RAG corpus markdown found under {_CORPUS_DIR}")

        if force_rebuild:
            try:
                client.delete_collection(_COLLECTION_NAME)
            except Exception:
                pass

        fp_path = RAG_PERSIST_DIR / _FINGERPRINT_FILE
        stored_fp = fp_path.read_text(encoding="utf-8").strip() if fp_path.exists() else ""

        try:
            collection = client.get_collection(
                name=_COLLECTION_NAME, embedding_function=ef
            )
            if stored_fp == fp and not force_rebuild:
                _client_bundle = (client, collection, fp)
                return client, collection
        except Exception:
            pass

        try:
            client.delete_collection(_COLLECTION_NAME)
        except Exception:
            pass

        collection = client.create_collection(
            name=_COLLECTION_NAME,
            embedding_function=ef,
            metadata={"hnsw:space": "cosine"},
        )
        docs = [c["text"] for c in chunk_rows]
        ids = [c["id"] for c in chunk_rows]
        metadatas = [
            {
                "attack_family": c["attack_family"],
                "section": c["section"],
            }
            for c in chunk_rows
        ]
        collection.add(documents=docs, ids=ids, metadatas=metadatas)
        fp_path.write_text(fp, encoding="utf-8")
        _client_bundle = (client, collection, fp)

        return client, collection


def build_query_text(predicted_class: str, event: dict | None) -> str:
    """Merge prediction, top-probability string, and SHAP feature names for retrieval."""
    from nids_explain.config import RAG_QUERY_TOP_SHAP

    fam = str(predicted_class or "BENIGN").strip().upper()
    bits = [
        "Network intrusion detection flow-feature window explanation.",
        f"Predicted coarse class / attack family: {fam}.",
    ]
    if event:
        t3 = event.get("top3_str")
        if t3:
            bits.append(f"Alternative class probabilities hint: {t3}.")
        feats = event.get("shap_top_features") or []
        for row in feats[: RAG_QUERY_TOP_SHAP]:
            name = row.get("feature") if isinstance(row, dict) else None
            if name:
                bits.append(f"Important flow feature name for this window: {name}.")
    return " ".join(bits)


def retrieve_for_incident(predicted_class: str, event: dict | None) -> list[dict[str, Any]]:
    """Return ranked chunk dicts: text, metadata, rank."""
    _, collection = _ensure_bundle()
    fam = str(predicted_class or "BENIGN").strip().upper()
    q = build_query_text(predicted_class, event)
    k_filtered = max(1, min(RAG_TOP_K_FILTERED, RAG_TOP_K))
    k_total = max(1, RAG_TOP_K)

    def _normalize(res: dict) -> list[tuple[str, str, str, float]]:
        out: list[tuple[str, str, str, float]] = []
        if not res or not res.get("ids") or not res["ids"][0]:
            return out
        for i, doc_id in enumerate(res["ids"][0]):
            doc = (res["documents"] or [[]])[0][i]
            meta = (res["metadatas"] or [[]])[0][i] or {}
            dist = (res["distances"] or [[]])[0][i] if res.get("distances") else 0.0
            out.append((str(doc_id), str(doc), str(meta.get("section", "")), float(dist)))
        return out

    seen: set[str] = set()
    merged: list[tuple[str, str, str, float]] = []

    try:
        r1 = collection.query(
            query_texts=[q],
            n_results=k_filtered,
            where={"attack_family": fam},
            include=["documents", "metadatas", "distances"],
        )
        for item in _normalize(r1):
            if item[0] not in seen:
                seen.add(item[0])
                merged.append(item)
    except Exception:
        pass

    need = k_total - len(merged)
    if need > 0:
        r2 = collection.query(
            query_texts=[q],
            n_results=k_total + k_filtered,
            include=["documents", "metadatas", "distances"],
        )
        for item in _normalize(r2):
            if len(merged) >= k_total:
                break
            if item[0] not in seen:
                seen.add(item[0])
                merged.append(item)

    ordered: list[dict[str, Any]] = []
    for rank, (doc_id, doc, sec, _) in enumerate(merged, start=1):
        ordered.append({"id": doc_id, "section": sec, "text": doc, "rank": rank})
    return ordered


def format_chunks_for_prompt(chunks: list[dict[str, Any]]) -> str:
    """Human-readable grounding block for Gemini."""
    if not chunks:
        return "(No corpus chunks retrieved.)"
    lines = []
    for c in chunks:
        lines.append(
            f"[Source rank {c['rank']}: chunk_id={c['id']} · section={c['section']}]\n{c['text']}"
        )
    return "\n\n---\n\n".join(lines)
