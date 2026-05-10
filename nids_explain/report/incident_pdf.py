"""One PDF per incident: large type, high-contrast layout for operator-facing reports."""

import json
import re
import textwrap
from datetime import datetime
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.patches import FancyBboxPatch

from nids_explain.config import RAG_PDF_CONTEXT_MAX_CHARS


def _safe_filename_token(name: str) -> str:
    s = re.sub(r"[^\w\-]+", "_", str(name).strip())
    return s[:64] or "class"


def write_incident_pdf(
    output_path: Path,
    predicted_class: str,
    confidence_pct: float,
    top3_str: str,
    shap_features: list,
    llm_narrative: str,
    rag_context: str,
    meta: dict,
):
    """
    Single-incident report: page 1 headline verdict + SHAP table + reference knowledge + LLM text.
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y-%m-%d %H:%M")

    with PdfPages(output_path) as pdf:
        fig = plt.figure(figsize=(8.27, 11.69))
        fig.patch.set_facecolor("#0c4a6e")
        fig.text(0.5, 0.92, "Incident explainability", ha="center", va="top", fontsize=26, color="#e0f2fe", weight="bold")
        fig.text(
            0.5,
            0.84,
            "Blind inference · features only · no label fed to model",
            ha="center",
            va="top",
            fontsize=14,
            color="#bae6fd",
        )

        banner = FancyBboxPatch(
            (0.06, 0.58),
            0.88,
            0.20,
            boxstyle="round,pad=0.02",
            transform=fig.transFigure,
            facecolor="#fef3c7",
            edgecolor="#f59e0b",
            linewidth=2,
        )
        fig.patches.append(banner)
        attack_font = 42 if len(predicted_class) <= 12 else 32
        fig.text(
            0.5,
            0.72,
            f"Model:  {predicted_class}",
            ha="center",
            va="center",
            fontsize=attack_font,
            color="#78350f",
            weight="bold",
        )
        fig.text(
            0.5,
            0.62,
            f"Confidence: {confidence_pct:.2f}%",
            ha="center",
            va="center",
            fontsize=20,
            color="#92400e",
            weight="bold",
        )

        fig.text(0.08, 0.48, f"Generated: {ts}", ha="left", va="top", fontsize=12, color="#e0f2fe")
        fig.text(0.08, 0.44, f"Top-3: {top3_str}", ha="left", va="top", fontsize=12, color="#e0f2fe", wrap=True)

        detail = (
            f"Row window start: {meta.get('row_start', 'n/a')} · "
            f"SHAP nsamples: {meta.get('shap_nsamples', '—')} · "
            f"BG pool size: {meta.get('background_pool', '—')}"
        )
        fig.text(0.08, 0.38, detail, ha="left", va="top", fontsize=11, color="#bae6fd")

        footer = (
            "Interpretation combines model scores, SHAP attributions, retrieved reference knowledge (vector RAG), "
            "and optional LLM wording — validate operationally before blocking traffic."
        )
        fig.text(0.5, 0.06, textwrap.fill(footer, 78), ha="center", va="bottom", fontsize=10, color="#93c5fd")
        pdf.savefig(fig, bbox_inches="tight")
        plt.close(fig)

        fig = plt.figure(figsize=(8.27, 11.69))
        fig.patch.set_facecolor("white")
        fig.suptitle("SHAP — numeric contributions", fontsize=20, weight="bold", color="#0c4a6e", y=0.97)
        ax = fig.add_axes([0.08, 0.33, 0.84, 0.50])
        ax.axis("off")
        df = pd.DataFrame(shap_features)
        table = ax.table(
            cellText=df.values,
            colLabels=list(df.columns),
            loc="center",
            cellLoc="center",
        )
        table.auto_set_font_size(False)
        table.set_fontsize(11)
        table.scale(1, 1.8)
        for j in range(len(df.columns)):
            table[(0, j)].set_facecolor("#0d9488")
            table[(0, j)].get_text().set_color("white")
            table[(0, j)].get_text().set_weight("bold")
        cap = (
            "Mean |SHAP| and mean signed SHAP per feature (aggregated over time steps). "
            "Positive signed values push the predicted-class probability up."
        )
        fig.text(0.5, 0.28, textwrap.fill(cap, 88), ha="center", fontsize=12, color="#334155")
        ax_json = fig.add_axes([0.08, 0.02, 0.84, 0.22])
        ax_json.axis("off")
        ax_json.set_title("SHAP JSON (primary numbers)", loc="left", fontsize=12, weight="bold", color="#0f172a", pad=8)
        ax_json.text(
            0.0,
            1.0,
            json.dumps(shap_features, indent=2),
            ha="left",
            va="top",
            fontsize=7,
            family="monospace",
            color="#1e293b",
            transform=ax_json.transAxes,
            wrap=False,
        )
        pdf.savefig(fig, bbox_inches="tight")
        plt.close(fig)

        fig = plt.figure(figsize=(8.27, 11.69))
        fig.patch.set_facecolor("white")
        fig.suptitle("Reference knowledge (vector RAG)", fontsize=20, weight="bold", color="#0c4a6e", y=0.96)
        rag_display = rag_context
        if RAG_PDF_CONTEXT_MAX_CHARS > 0 and len(rag_display) > RAG_PDF_CONTEXT_MAX_CHARS:
            rag_display = (
                rag_display[: RAG_PDF_CONTEXT_MAX_CHARS].rstrip()
                + "\n\n… (truncated for PDF layout; full text sent to LLM prompt.) …"
            )
        fig.text(
            0.08,
            0.88,
            textwrap.fill(rag_display, 86),
            ha="left",
            va="top",
            fontsize=14,
            linespacing=1.5,
            color="#1e293b",
        )
        fig.text(
            0.08,
            0.42,
            "Chunks are retrieved with Chroma embeddings from nids_explain/llm/rag_corpus/ "
            "(set RAG_DISABLE=1 for a short static fallback).",
            ha="left",
            va="top",
            fontsize=12,
            style="italic",
            color="#64748b",
        )
        pdf.savefig(fig, bbox_inches="tight")
        plt.close(fig)

        fig = plt.figure(figsize=(8.27, 11.69))
        fig.patch.set_facecolor("white")
        fig.suptitle("LLM narrative (Gemini)", fontsize=22, weight="bold", color="#0c4a6e", y=0.96)
        wrapped = textwrap.fill(llm_narrative, 82) if llm_narrative else "(No narrative.)"
        fig.text(
            0.08,
            0.88,
            wrapped,
            ha="left",
            va="top",
            fontsize=15,
            linespacing=1.55,
            color="#0f172a",
        )
        pdf.savefig(fig, bbox_inches="tight")
        plt.close(fig)


def incident_pdf_path(out_dir: Path, incident_idx: int, predicted_class: str) -> Path:
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe = _safe_filename_token(predicted_class)
    return out_dir / f"incident_{incident_idx:03d}_{safe}_{stamp}.pdf"
