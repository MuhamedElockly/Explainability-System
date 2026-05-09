"""
IDS explainability: blind random windows → inference (features only) → SHAP → Gemini → PDF per attack.

Environment:
  BLIND_SAMPLE_COUNT   — random windows per run (default 8); change EXPLAIN_SEED for different windows
  EXPLAIN_SEED         — RNG seed for reproducibility / variation
  CLEAN_REPORTS=1      — with fix_assets.py: remove legacy ids_inference_report.pdf + incident_reports/*.pdf
  GEMINI_API_KEY       — .env or environment
  INCIDENT_REPORTS_DIR — output folder (default incident_reports)

Example:
  CLEAN_REPORTS=1 python fix_assets.py
  EXPLAIN_SEED=99 python test_model.py
"""

from nids_explain.pipeline import main

if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"Error during test execution: {exc}")
