"""
Attack-type knowledge for LLM grounding: Chroma vector RAG over packaged corpus.

Set RAG_DISABLE=1 to fall back to compact static paragraphs (no embedding load).
RAG_FORCE_REBUILD=1 wipes the local Chroma store and re-ingests markdown corpus.
"""

from __future__ import annotations

import os
from typing import Any

from nids_explain.config import RAG_PROMPT_MAX_CHARS

# Fallback when RAG is disabled or ingestion/embedding fails (keeps pipeline usable offline).
_STATIC_ATTACK_KNOWLEDGE: dict[str, str] = {
    "BENIGN": (
        "Benign traffic: normal device or user sessions without attack semantics. "
        "Expect protocol mixes that match asset roles and baselines."
    ),
    "BRUTE_FORCE": (
        "Brute-force attempts: repeated authentication trials toward services; "
        "often many short sessions or churn vs baseline."
    ),
    "DDOS": (
        "Distributed denial-of-service: many sources flooding targets to exhaust "
        "bandwidth, state, or CPU; often high fan-in and volumetric anomalies."
    ),
    "DOS": (
        "Denial-of-service from concentrated sources: sustained abusive volume "
        "targeting availability with narrower apparent fan-in than DDoS."
    ),
    "MIRAI": (
        "Mirai-class IoT botnet motifs: scanning, default-credential abuse, "
        "and coordinated flood participation from embedded devices."
    ),
    "RECON": (
        "Reconnaissance: mapping activity such as sweeps and probes preceding exploitation; "
        "often many short flows to diverse destinations/ports."
    ),
    "SPOOFING": (
        "Spoofing / path-identity manipulation motifs: forged or inconsistent addressing roles; "
        "interpretation depends on which L3/L7 signals the model encodes."
    ),
    "WEB_ATTACK": (
        "Web-layer intrusion attempts: injections, malicious uploads, exploitation-shaped HTTP(S) "
        "dialogs when visible in flow aggregates."
    ),
}


def _canonical_class(name: str | None) -> str:
    if not name:
        return "BENIGN"
    key = str(name).strip().upper()
    return key if key in _STATIC_ATTACK_KNOWLEDGE else key


def static_attack_paragraph(predicted_class: str | None) -> str:
    """One short paragraph (no vector DB) — used when RAG is off or errors."""
    canon = _canonical_class(predicted_class)
    return _STATIC_ATTACK_KNOWLEDGE.get(canon, _STATIC_ATTACK_KNOWLEDGE["BENIGN"])


def rag_header() -> str:
    return (
        "The following REFERENCE KNOWLEDGE chunks were retrieved from a local vector database "
        "(embeddings over an attack-family corpus). "
        "Use them for terminology and typical patterns; prioritize agreement with SHAP feature names "
        "and model probabilities. "
        "Do not invent packet-level details or attributions not supported by SHAP or the cited chunks. "
        "If chunks conflict with the window, prefer conservative wording."
    )


def get_attack_context(predicted_class: str, event: dict[str, Any] | None = None) -> str:
    """
    Retrieve top-k corpus chunks for `predicted_class`, optionally query-expanded with
    `event` (top-3 string + SHAP feature names), format for the LLM prompt slot.
    """
    off = os.environ.get("RAG_DISABLE", "").strip().lower() in ("1", "true", "yes")
    if off:
        return static_attack_paragraph(predicted_class)

    try:
        from nids_explain.llm import rag_engine

        chunks = rag_engine.retrieve_for_incident(predicted_class, event)
        text = rag_engine.format_chunks_for_prompt(chunks)
        if RAG_PROMPT_MAX_CHARS > 0 and len(text) > RAG_PROMPT_MAX_CHARS:
            text = (
                text[: RAG_PROMPT_MAX_CHARS].rstrip()
                + "\n\n[Retrieved context truncated to RAG_PROMPT_MAX_CHARS for prompt budget.]"
            )
        return text
    except Exception:
        return static_attack_paragraph(predicted_class)


def format_rag_footer_note() -> str:
    """Optional status line for logs or PDF footers."""
    if os.environ.get("RAG_DISABLE", "").strip().lower() in ("1", "true", "yes"):
        return "Reference knowledge: static fallback (RAG_DISABLE)."
    return "Reference knowledge: vector retrieval (Chroma)."
