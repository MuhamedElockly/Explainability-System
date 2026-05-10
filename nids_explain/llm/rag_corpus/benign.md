# BENIGN (reference for contrast)

## Operational meaning in IDS pipelines

Benign flows represent legitimate user sessions, automation, telemetry, backups, patches, APIs, VoIP/video, browsing, SSH admin work, downloads, IoT chatter, DNS resolution, DHCP, NTP, and similar expected traffic. The absence of an attack does not mean “empty network”—it means no decision rule or model has enough evidence to label the window as an attack family.

## Flow-feature patterns that often look “normal”

Benign traffic usually shows protocol mixes that match the segment (e.g., HTTP/S for web servers, SSH for admin hosts), relatively stable inter-arrival times at the flow level, packet sizes that follow application MTU and TCP windowing, and bi-directional conversations with sensible endpoint roles. Bursts can still appear (downloads, streaming, scans from misconfigured clients) so models should not equate “spiky” with malicious by default.

## Common confusions with attacks

Short high-rate episodes can resemble early DDoS; failed logins can resemble brute force; wide port contact lists can resemble reconnaissance; inconsistent addresses can resemble spoofing. Contextual baselines, asset roles, and multi-feature agreement matter. SHAP on a single window is a local explanation: it says which features moved this prediction, not that the remote host is “known bad.”

## Analyst checklist

Validate against inventory and expected services, check time-of-day and business patterns, correlate with auth logs and WAF if web, and prefer sustained behavioral signals over one-off flow oddities before blocking.
