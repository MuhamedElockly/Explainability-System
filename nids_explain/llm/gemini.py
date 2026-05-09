"""Gemini API initialization and blind-incident narrative generation."""

import json
import os

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
            return ("generativeai", genai.GenerativeModel("gemini-2.5-flash")), ""
        except Exception as exc:
            return None, f"Gemini skipped: SDK init failed ({exc})."


def generate_blind_incident_report(gemini_bundle, event: dict, rag_context: str) -> str:
    """
    Narrative for blind (unlabeled) windows: SHAP + probabilities + static attack-type reference (pseudo-RAG).
    """
    if not gemini_bundle:
        return (
            "LLM narrative skipped (no API key). Use the SHAP JSON and reference knowledge block in the PDF."
        )
    provider, client = gemini_bundle
    shap_payload = json.dumps(event["shap_top_features"], indent=2)
    prompt = (
        "You are a SOC analyst writing a short incident explanation for operators.\n"
        "Inference used ONLY flow features; no dataset label was supplied to the model.\n\n"
        f"{rag_header()}\n\n"
        "REFERENCE KNOWLEDGE (attack family background — use for terminology and typical patterns):\n"
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
    try:
        if provider == "genai":
            response = client.models.generate_content(model="gemini-2.5-flash", contents=prompt)
            text = (response.text or "").strip()
        else:
            response = client.generate_content(prompt)
            text = (response.text or "").strip()
        return text if text else "Gemini returned an empty response."
    except Exception as exc:
        return f"Gemini generation failed: {exc}"
