# BRUTE_FORCE

## Plain-language overview

Credential brute-force attempts repeatedly try passwords, SSH keys guesses, Kerberos guesses, SMB logins, RDP guesses, SIP registrations, FTP/ Telnet prompts, VPN portals, OAuth password grants, HTTP form posts, SMTP AUTH, SNMP community strings—anywhere secrets are checked centrally. Automated campaigns run credential lists (“combo lists”), password rules, spraying (many users, few guesses), and credential stuffing (known leaked passwords).

## Typical network-flow signals (feature-space intuition)

Flows may exhibit many parallel or serial connections toward an authentication sink, unusually high SYN or TCP session establishment counts to a single listener, short payloads with frequent 401/403 (web) equivalents at the backbone (length/packet patterns may imply small request/reply churn), asymmetric bytes if responses are terse “failure” banners, reused source IPs rotating through SOCKS/VPN egress, uneven inter-arrival times when tools throttle to evade lockout. Bot-driven attempts often converge on default ports unless proxied.

## MITRE-aligned framing (conceptual)

This activity maps intuitively to techniques like brute force (example ATT&CK ID T1110) and valid accounts (T1078) post-compromise. Use MITRE for reporting language, not as ground truth for a single flow window.

## Differentiation from other families

Vs DDoS: brute force targets authentication semantics; flooding often targets resource exhaustion without completing meaningful auth handshakes at application layer. Vs recon: recon maps and probes; brute force focuses on repeated identity trials on services that answer. Vs web attacks: injection attempts carry exploit-shaped payloads; brute force carries many similar auth trials.

## Defensive posture (fact-oriented)

Implement lockouts and exponential backoff thoughtfully, MFA where feasible, disallow password-only remote admin from the internet, tarpitting and progressive delays on edge auth, IDS rate rules per source and per target principal, deception accounts, and correlate successful logins shortly after bursts.
