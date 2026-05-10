# MIRAI — IoT botnet archetype (and cousins)

## What “Mirai-class” evokes for analysts

Mirai and derivative IoT malware families brute default credentials via Telnet/TR-069-ish vectors, BusyBox scanning, IRC/C2 ladders, scripted wget/curl drop stages, simplistic DDoS cannons (UDP/TCP GRE variants), churning heterogeneous device ASNs—cameras, DVRs, gateways, routers, printers—with limited RAM and asymmetric uplinks feeding attack traffic.

## Flow-level intuition

Outbound scanning shows many ephemeral connections to disparate destination :23 / :2323-like services (depending on vantage), asymmetric packet sizes (small exploits + larger binary pulls), geographically scattered targets, bursty parallelism from bot coordination windows, TTL/TOS quirks (less reliable at flow stats), cyclic attack participation vs idle scanning sleep patterns.

## Distinguishing from generic DDoS and benign IoT chatter

Misconfigured multicast/SSDP chatter can amplify noise benignly vs malicious amplification abuse. Telemetry-only IoT can be volumetric toward cloud brokers—inventory roles matter. Attribution to “Mirai” in IDS labels reflects training dataset taxonomy; treat wording as heuristic class naming, not binary forensics attribution.

## Defensive correlations

Isolate IoT VLANs without inbound reachability except via broker, forbid default passwords, firmware lifecycle, egress filtering limiting unnecessary TCP fan-out toward internet telnet-era ports where applicable without breaking ops, anomaly detection inside IoT subnets with east-west vantage.
