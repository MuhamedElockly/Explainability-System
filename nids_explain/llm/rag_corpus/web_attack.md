# WEB_ATTACK — application-layer intrusion attempts (coarse IDS bucket)

## What tends to collapse into “web_attack” labeling

Trainer labels often unify SQL/command injection payloads, deserialization gadget abuse, SSRF chaining, XSS delivery attempts when visible at edge flow encoding, malicious file uploads, webshell probing, probing for admin panels (/wp-login.php brute patterns blurring toward brute-force), API abuse—all depending on datasets. Operational translation: HTTP(S) dialogs showing exploit-shaped request entropy, oddly repeated parameter mutations, elongated suspicious strings in URL or body proxies (if distilled into aggregates), chunked POST anomalies vs baseline browsing ratios.

## Distinguishable statistical intuitions versus benign browsing

Harmless scraping can inflate rates but often targets stable catalogs; exploits often spray rare edge-case paths repeatedly. Burst sizes may differ depending on chunked encodings. Mixed status codes—not always modeled—might appear indirectly via timing and bytes if errors short-circuit replies. Automated exploit tools produce rhythmic patterns vs human stochastic scroll sequences when observed at aggregated flow windows **if features capture them**.

## Interactions with WAF/CDN vantage

Upstream models may observe scrubbed anomalies (features dampened)—downstream origin sensors see raw attempts. Explanation text should avoid claiming “blocked at WAF” unless telemetry supports it—SHAP cites feature channels only.

## Calibrated narrative guidance

Treat classification as probabilistic anomaly on engineered flow statistics; recommend payload review in reverse proxies, sanitized logs correlation, parameterized query audits, patching cadence—not automatic blocking narratives without policy.
