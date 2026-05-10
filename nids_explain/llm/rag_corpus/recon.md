# RECON — network reconnaissance and mapping

## Intent

Attackers—or red teams map external or internal footprints before exploitation: ICMP sweeps (“ping”), ARP probing on LAN segments, SNMP walks, SYN or connect() port scans across broad destination sets, traceroute TTL tricks, randomized IP bucket sampling, CDN origin discovery scans, SMB null session probing, fingerprinting probes (SYN with odd options mixes), QUIC initial probes depending on vantage.

## Flow-feature manifestations

Flows may exhibit many short-lived probes to disparate destination ports/IP ranges, asymmetric bytes (tiny probes vs terse ICMP/TCP RST replies), clustered timing from scan tools versus bursty parallelism if parallel threads, repeated patterns if rotating source ports with stable IP, comparatively low payloads per handshake vs volumetric floods, DNS PTR/SRV recon if encoded as modeled stats.

## Recon versus benign discovery

CDN health checks and monitoring platforms also generate wide sweeps—but usually stable source lists and dashboards. Operational mapping from IT asset scanners should be allowlisted temporally/geographically—correlate inventories and CMDB-derived expectations.

## Analytic tempering

Seeing recon does not imply imminent breach—it elevates preparedness. Sequential recon + brute force spikes + exploitation-shaped web flows may escalate composite risk in SOCs. Explainability narratives should emphasize “mapping behavior” wording rather than asserting breach.
