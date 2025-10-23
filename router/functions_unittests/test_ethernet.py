import pytest

from params import (
    arp_ethernet_headers,
    ipv4_ethernet_headers,
    arp_ethernet_headers_bytes,
    ipv4_ethernet_headers_bytes,
)
from test_header import TestHeader


ethernet_headers = arp_ethernet_headers + ipv4_ethernet_headers
ethernet_headers_bytes = arp_ethernet_headers_bytes + ipv4_ethernet_headers_bytes
ethernet_scenarios = zip(ethernet_headers, ethernet_headers_bytes, strict=False)


class TestEthernet(TestHeader):
    @pytest.fixture(params=ethernet_scenarios)
    def scenario(self, request):
        return request.param
