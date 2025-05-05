import os
from traffic_taffy.dissection import PCAPDissectorLevel
from traffic_taffy.dissector_engine.dpkt import DissectionEngineDpkt

def test_dpkt_engine():
    test_pcap = "dns.pcap"
    test_pcap = "port53-2023-30-31_20.pcap"
    test_pcap = "airplane-wireless.pcap"
    if not os.path.exists(test_pcap):
        return

    engine = DissectionEngineDpkt(test_pcap,
                                  dissector_level = PCAPDissectorLevel.COMMON_LAYERS)
    dissection = engine.load()

