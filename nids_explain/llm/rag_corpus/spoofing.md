# SPOOFING — identity and path manipulation archetypes

## Scope reminder

Modern IDS coarse classes often lump ARP spoofing/MITM motifs, rogue DHCP/DNS answers, BGP prefix hijacking effects at vantage edges (if surfaced via derived stats), VLAN hopping precursors reflected indirectly, SSTP/MITM downgrade attempts—as well as spoofed IPs in amplification reflection paths if visible as asymmetries—not all are equally visible in aggregated flow tuples.

## Local link behaviors (conceptual ARP/MITM motifs)

Poisoned ARP answers create MAC rewrites → frames misdirected; operators may correlate via duplicate IP/MAC inconsistencies, gratuitous bursts, gratuitous unsolicited ARPs. Flow stats alone may omit L2 anomalies—confidence language must acknowledge sensor blind spots unless features encode proxy signals.

## Network-layer spoof motifs

Ingress filtering failures allow forged source IPs; reflection attacks display reply asymmetry disproportionate between src/dst cardinality. IDS flow windows labeling spoofing emphasize inconsistent addressing patterns, asymmetric conversation roles, anomalies in TTL/directionality—only if mirrored in engineered features actually trained.

## Vs web attacks vs recon

Unlike injection attempts spoofing seldom carries large payloads in early phases; unlike recon breadth it may converge on subnets or gateways with repeated mid-session inconsistencies (if modeled). Correlate PCAP if available—not always with blind flow-only pipelines.
