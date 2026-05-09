"""
Static attack-type reference text for LLM prompts (pseudo-RAG).

Swap this module later for vector DB / retrieval without changing the rest of the pipeline.
"""

# Short operational descriptions per coarse class (IDS context).
ATTACK_KNOWLEDGE: dict[str, str] = {
    "BENIGN": (
        "Benign traffic: normal user or device behavior without attack signatures. "
        "Typical flows show stable rates, expected protocols, and no coordinated anomalies."
    ),
    "BRUTE_FORCE": (
        "Brute-force attacks: many authentication attempts (e.g., SSH, HTTP login, Telnet) "
        "often from one or few sources. Indicators can include high connection churn, repeated failures, "
        "and protocol-specific burst patterns vs. baseline."
    ),
    "DDOS": (
        "Distributed denial-of-service: high-volume, multi-source flooding aimed at exhausting bandwidth, "
        "state tables, or application resources. Often shows abnormal packet rates, many flows, and skewed "
        "feature distributions vs. normal traffic."
    ),
    "DOS": (
        "Denial-of-service (single-source or localized flood): sustained abusive traffic toward a target "
        "to degrade availability; may resemble DDoS but with fewer apparent sources."
    ),
    "MIRAI": (
        "Mirai-class IoT botnet activity: malware-driven scanning, credential stuffing, and coordinated floods "
        "often involving IoT protocols and characteristic scanning/flood signatures."
    ),
    "RECON": (
        "Reconnaissance: probing and mapping (e.g., port scans, ping sweeps, OS fingerprinting) preceding exploitation. "
        "Often lower volume than floods but with distinctive scan patterns."
    ),
    "SPOOFING": (
        "Spoofing / MITM-style manipulation: forged identities or redirection (e.g., ARP/DNS abuse). "
        "May show inconsistencies in addressing or protocol anomalies tied to impersonation."
    ),
    "WEB_ATTACK": (
        "Web-layer attacks: injections, XSS, malicious uploads, or web exploitation attempts. "
        "Often correlated with abnormal HTTP/TLS feature statistics vs. benign browsing."
    ),
}


def get_attack_context(predicted_class: str) -> str:
    """Return reference paragraph for the predicted label (RAG-style context)."""
    if not predicted_class:
        return ATTACK_KNOWLEDGE["BENIGN"]
    name = str(predicted_class).strip()
    if name in ATTACK_KNOWLEDGE:
        return ATTACK_KNOWLEDGE[name]
    return ATTACK_KNOWLEDGE.get(name.upper(), ATTACK_KNOWLEDGE["BENIGN"])


def rag_header() -> str:
    return (
        "The following REFERENCE KNOWLEDGE describes typical behavior of the predicted attack family. "
        "Use it to clarify terminology and expected indicators; tie conclusions to SHAP features and probabilities."
    )
