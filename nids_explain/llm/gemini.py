"""Gemini API initialization and blind-incident narrative generation (retries on 429 / quota)."""

import json
import os
import random
import re
import time

from nids_explain.config import GEMINI_MAX_RETRIES, GEMINI_MODEL
from nids_explain.llm.attack_kb import rag_header


def init_gemini():
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    if not api_key:
        return None, "Gemini skipped: GEMINI_API_KEY is not set."
    try:
        from google import genai  # type: ignore

        return ("genai", genai.Client(api_key=api_key)), ""
    except Exception:
        try:
            import google.generativeai as genai  # type: ignore

            genai.configure(api_key=api_key)
            return ("generativeai", genai.GenerativeModel(GEMINI_MODEL)), ""
        except Exception as exc:
            return None, f"Gemini skipped: SDK init failed ({exc})."


def _is_resource_exhausted(exc: BaseException) -> bool:
    msg = str(exc).lower()
    if "429" in msg or "resource exhausted" in msg:
        return True
    if "quota" in msg and ("exceed" in msg or "exceeded" in msg):
        return True
    if "rate limit" in msg or "too many requests" in msg:
        return True
    code = getattr(exc, "code", None)
    return code == 429


def _retry_sleep_seconds(exc: BaseException, attempt: int) -> float:
    """Prefer server hint 'retry in Xs'; else exponential backoff with jitter."""
    msg = str(exc)
    for pattern in (
        r"retry in ([\d.]+)\s*s",
        r"retry in\s+([\d.]+)",
        r"retry_delay\s*\{\s*seconds:\s*(\d+)",
    ):
        m = re.search(pattern, msg, re.I)
        if m:
            try:
                return min(max(float(m.group(1)), 1.0), 120.0)
            except ValueError:
                break
    base = min(2**attempt, 60)
    jitter = random.uniform(0.5, 2.0)
    return base + jitter


def _call_gemini_once(provider: str, client, prompt: str) -> str:
    if provider == "genai":
        response = client.models.generate_content(model=GEMINI_MODEL, contents=prompt)
        return (response.text or "").strip()
    response = client.generate_content(prompt)
    return (response.text or "").strip()


def _fallback_narrative(event: dict, rag_context: str, reason: str) -> str:
    feats = event.get("shap_top_features") or []
    top = feats[:4]
    lines = [
        "Automated Gemini narrative unavailable (API quota, rate limit, or network).",
        f"Reason: {reason[:500]}",
        "",
        f"Model prediction: {event.get('predicted_class')} at {float(event.get('confidence', 0)):.2f}% confidence.",
        f"Top probabilities: {event.get('top3_str', '')}",
        "",
        "Strongest SHAP attributions (mean signed — positive pushes predicted-class probability up):",
    ]
    for row in top:
        lines.append(
            f"  • {row.get('feature')}: |SHAP|={row.get('mean_abs_shap', 0):.6f}, signed={row.get('mean_signed_shap', 0):.6f}"
        )
    lines.extend(
        [
            "",
            "Use the Reference knowledge page in this PDF for typical indicators of this attack family.",
            "",
            "Tips: set GEMINI_MODEL, increase GEMINI_INTER_REQUEST_DELAY_SEC, reduce BLIND_SAMPLE_COUNT,",
            "or upgrade billing / wait for daily free-tier reset.",
        ]
    )
    return "\n".join(lines)


def generate_blind_incident_report(gemini_bundle, event: dict, rag_context: str) -> str:
    """
    Narrative for blind (unlabeled) windows: SHAP + probabilities + vector-retrieved attack knowledge (RAG).
    Retries on 429 / quota with server-suggested or exponential backoff.
    """
    disable = os.environ.get("GEMINI_DISABLE", "").strip().lower()
    if disable in ("1", "true", "yes"):
        return _fallback_narrative(event, rag_context, "GEMINI_DISABLE is set — skipping Gemini calls.")

    if not gemini_bundle:
        return _fallback_narrative(event, rag_context, "No API key configured.")

    provider, client = gemini_bundle
    shap_payload = json.dumps(event["shap_top_features"], indent=2)
    prompt = (
        "You are a SOC analyst writing a short incident explanation for operators.\n"
        "Inference used ONLY flow features; no dataset label was supplied to the model.\n\n"
        f"{rag_header()}\n\n"
        "REFERENCE KNOWLEDGE (retrieved attack-family corpus chunks — cite themes, not chunk IDs verbatim):\n"
        f"{rag_context}\n\n"
        "MODEL OUTPUT:\n"
        f"- Predicted class: {event['predicted_class']}\n"
        f"- Argmax confidence: {event['confidence']:.4f}%\n"
        f"- Top-3 probabilities: {event.get('top3_str', '')}\n"
        f"- Window row start index (dataset order): {event.get('row_start', 'n/a')}\n\n"
        "SHAP (Kernel SHAP on predicted-class probability; JSON):\n"
        f"{shap_payload}\n\n"
        "Write clearly for non-research readers:\n"
        "1) Verdict (3–4 sentences): why the model likely flagged this window as the predicted class.\n"
        "2) Feature links: mention the top 2–3 SHAP features by name and direction (pushing toward attack vs not).\n"
        "3) One line: how REFERENCE KNOWLEDGE aligns (or not) with those features — stay conservative.\n"
        "4) One line: SHAP is approximate and background-dependent.\n"
        "Use plain English. No markdown headings."
    )

    last_err: BaseException | None = None
    for attempt in range(GEMINI_MAX_RETRIES):
        try:
            text = _call_gemini_once(provider, client, prompt)
            return text if text else "Gemini returned an empty response."
        except Exception as exc:
            last_err = exc
            if _is_resource_exhausted(exc) and attempt + 1 < GEMINI_MAX_RETRIES:
                wait_s = _retry_sleep_seconds(exc, attempt)
                print(f"    Gemini rate limited — sleeping {wait_s:.1f}s then retry ({attempt + 1}/{GEMINI_MAX_RETRIES})...")
                time.sleep(wait_s)
                continue
            break

    reason = str(last_err) if last_err else "unknown error"
    print(f"    Gemini failed after retries; PDF will use SHAP-only fallback narrative.")
    return _fallback_narrative(event, rag_context, reason)
