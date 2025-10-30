import sys
import copy

from pathlib import Path

import pytest

from params import (
    ipv4_headers,
    ipv4_headers_bytes,
    ipv4_altered_headers,
    ipv4_original_headers,
)
from test_header import TestHeader


sys.path.append(str(Path(__file__).resolve().parent.parent))
from protocols.ipv4 import IPv4


ipv4_scenarios = zip(ipv4_headers, ipv4_headers_bytes, strict=False)
setattr_scenarios = zip(ipv4_original_headers, ipv4_altered_headers, strict=False)


class TestIPv4(TestHeader):
    @pytest.fixture(params=ipv4_scenarios)
    def scenario(self, request):
        return request.param

    @pytest.fixture(params=setattr_scenarios)
    def setattr_scenario(self, request):
        return request.param

    def test_get_ipv4_header_length(self, scenario):
        returned_header_length = IPv4.get_header_length(scenario[1])
        assert returned_header_length == scenario[0].header_length, (
            f"get_header_length({scenario[1]}) returned {returned_header_length}; Expected value is: {scenario[0].header_length}"
        )

    def test_get_flags(self, scenario):
        returned_flags = IPv4.get_flags(scenario[1])
        assert returned_flags == scenario[0].flags, (
            f"get_flags({scenario[1]}) returned {returned_flags}; Expected value is: {scenario[0].flags}"
        )

    def test_get_fragment_offset(self, scenario):
        returned_fragment_offset = IPv4.get_fragment_offset(scenario[1])
        assert returned_fragment_offset == scenario[0].fragment_offset, (
            f"get_fragment_offset({scenario[1]}) returned {returned_fragment_offset}; Expected value is: {scenario[0].fragment_offset}"
        )

    def test_calculate_internet_checksum(self, scenario):
        reset_checksum_header = copy.copy(scenario[0])
        object.__setattr__(reset_checksum_header, "checksum", 0)
        returned_checksum = IPv4.calculate_internet_checksum(bytes(reset_checksum_header))
        assert returned_checksum == scenario[0].checksum, (
            f"calculate_internet_checksum({scenario[1]}) returned {returned_checksum}; Expected value is: {scenario[0].checksum}"
        )

    def test_setattr(self, setattr_scenario):
        copied_header = copy.copy(setattr_scenario[0])
        copied_expected_header = copy.copy(setattr_scenario[1])
        copied_header.source, copied_header.destination = (
            copied_expected_header.source,
            copied_expected_header.destination,
        )
        copied_header.ttl -= 1
        copied_header.flags = 0b000
        copied_header.identification = copied_expected_header.identification
        assert copied_header == setattr_scenario[1], (
            f"setting {setattr_scenario[0]}.destination = {copy.copy(setattr_scenario[1].destination)} yielded {copied_header}; Expected value: {setattr_scenario[1]}"
        )
