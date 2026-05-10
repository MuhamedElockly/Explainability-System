# DDOS — distributed denial-of-service

## Operational overview

Distributed denial-of-service leverages many geographically spread sources—botnets, open resolvers being abused, spoofed amplifiers, hacked IoT fleets, bribery-as-a-service stressers—to exhaust bandwidth, per-flow state tables, CPU on middleboxes, or application threads. Targets can be IPs, subnets, DNS names/CDN fronts, TLS handshakes, HTTP endpoints, QUIC, SCTP, GRE tunnels, VoIP gateways, gaming servers, APIs, caches, NAT pools, GRE/VXLAN underlays inside DC fabric.

## Common volumetric mechanics

UDP floods saturate links and NICs without reliable backpressure at IP layer unless ECN/policing is present. Amplification abuses small queries → large UDP replies (historically DNS/NTP/SSDPr…—network operators harden protocols over time). TCP SYN floods hoard half-open conversations; RST/FIN anomalies can churn state. Fragmentation-heavy attacks chew reassembly buffers. ACK and PSH floods pressure middle-state machines and offload engines. HTTP floods look like browsers but swarm cache-miss URLs or expensive POST endpoints.

## Application-layer floods

HTTP(S) floods mimic clients with realistic headers (“low and slow”, cache busting); models may hinge on concurrency, UA diversity, referrer entropy, JA3/TLS fingerprints (if folded into features indirectly), repetition of rare paths, disproportionate TLS handshakes, or asymmetric header/body sizing—depending on exported flow statistics.

## Distinguishing DDoS from DoS vs benign flash crowds

Single-source bursts lean DoS-like; massively parallel sources imply DDoS. Benign spikes (viral launches, patching, TV events) correlate with identifiable content or marketing signals if available; volumetric anomalies without business context merit escalation. Attack traffic often concentrates on choke points (upstream links, authoritative DNS, authoritative auth edges).

## SHAP-aligned cautions for explainable IDS

Elevated packets-per-second-like summaries, unusually many low-duration flows toward one target IP, fragmented packet counters, disproportionate RST/SYN proportions, spikes in entropy on certain aggregates—might appear as modeled features correlated with volumetric floods. Always pair model scores with BGP/netflow vantage and operator baselines—local SHAP explanations are contingent on encoder background distributions.
