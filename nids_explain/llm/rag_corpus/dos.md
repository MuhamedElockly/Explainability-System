# DOS — denial-of-service (often fewer apparent sources)

## Conceptual framing

Classic DoS originates from constrained coordinated capacity—one host, LAN segment, VPS, rogue lab device, hacked internal machine, insider script, amplifier misconfiguration—not global bot dispersion. Operational impact parallels DDoS (availability loss) while telemetry may show narrower fan-in (few src IPs rotating through NAT notwithstanding).

## Mechanics mirroring volumetric subclasses

SYN floods from one powerful uplink suffice to exhaust state boxes. Repeated HTTP OPTIONS/GET bursts from a scripted client saturate app servers. Repeated TLS handshakes from the same offender starve cryptographic offload. Amplification may still manifest if the offending host abuses resolvers knowingly or via malware.

## Distinguishing from DDoS and benign stress tests

Synthetic load tests originate from predictable maintenance windows—and should be correlated with calendars. WAN micro-outages mimic loss but not abusive rates. IDS flow windows labeling “DoS-like” emphasize concentrated abusive volume without wide fan-in fingerprints.

## Model explanation narrative hooks

Indicators might include asymmetric byte counts reflecting single-direction floods, unusually regular timing from scripted tools vs organic human variance, unusually large counts of RST/FIN anomalies if features encode TCP flag mixes, bursts of ICMP echo if reflected in aggregates. Confidence should be moderated if multi-path routing balances sources—aggregated vantage matters.
