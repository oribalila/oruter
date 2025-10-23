import pytest

from params import arp_headers, arp_headers_bytes
from test_header import TestHeader


scenarios = zip(arp_headers, arp_headers_bytes, strict=False)


class TestArp(TestHeader):
    @pytest.fixture(params=scenarios)
    def scenario(self, request):
        return request.param
