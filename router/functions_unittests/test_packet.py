import pytest

from params import (
    arp_packets,
    arp_packets_bytes,
    icmp_reply_packets,
    icmp_request_packets,
    icmp_reply_packets_bytes,
    icmp_request_packets_bytes,
)
from test_header import TestHeader


icmp_packets = icmp_request_packets + icmp_reply_packets
icmp_packets_bytes = icmp_request_packets_bytes + icmp_reply_packets_bytes
scenarios = zip(arp_packets + icmp_packets, arp_packets_bytes + icmp_packets_bytes, strict=False)
build_icmp_reply_scenarios = zip(icmp_request_packets, icmp_reply_packets, strict=False)


class TestPacket(TestHeader):
    @pytest.fixture(params=scenarios)
    def scenario(self, request):
        return request.param

    def test_len(self, scenario):
        packet, packet_bytes = scenario
        assert bytes(packet) == packet_bytes
        assert len(packet) == len(packet_bytes)
