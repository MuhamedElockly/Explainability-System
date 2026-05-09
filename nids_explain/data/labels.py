"""Map raw dataset labels to coarse 8-class groups."""


def group_labels_to_8_classes(label):
    label = str(label).strip()
    mapping = {
        "SqlInjection": "WEB_ATTACK",
        "CommandInjection": "WEB_ATTACK",
        "Backdoor_Malware": "WEB_ATTACK",
        "Uploading_Attack": "WEB_ATTACK",
        "XSS": "WEB_ATTACK",
        "Recon-PingSweep": "RECON",
        "Recon-OSScan": "RECON",
        "VulnerabilityScan": "RECON",
        "Recon-PortScan": "RECON",
        "Recon-HostDiscovery": "RECON",
        "DictionaryBruteForce": "BRUTE_FORCE",
        "BrowserHijacking": "BRUTE_FORCE",
        "MITM-ArpSpoofing": "SPOOFING",
        "DNS_Spoofing": "SPOOFING",
        "DDoS-ACK_Fragmentation": "DDOS",
        "DDoS-UDP_Flood": "DDOS",
        "DDoS-SlowLoris": "DDOS",
        "DDoS-ICMP_Flood": "DDOS",
        "DDoS-RSTFINFlood": "DDOS",
        "DDoS-PSHACK_Flood": "DDOS",
        "DDoS-HTTP_Flood": "DDOS",
        "DDoS-UDP_Fragmentation": "DDOS",
        "DDoS-ICMP_Fragmentation": "DDOS",
        "DDoS-TCP_Flood": "DDOS",
        "DDoS-SYN_Flood": "DDOS",
        "DDoS-SynonymousIP_Flood": "DDOS",
        "DoS-HTTP_Flood": "DOS",
        "DoS-TCP_Flood": "DOS",
        "DoS-SYN_Flood": "DOS",
        "DoS-UDP_Flood": "DOS",
        "Mirai-greip_flood": "MIRAI",
        "Mirai-greeth_flood": "MIRAI",
        "Mirai-udpplain": "MIRAI",
        "BenignTraffic": "BENIGN",
    }
    return mapping.get(label, "BENIGN")
