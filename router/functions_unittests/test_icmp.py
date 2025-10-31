import copy

import pytest

from params import (
    icmp_reply_headers,
    icmp_request_headers,
    icmp_reply_headers_bytes,
    icmp_request_headers_bytes,
)
from test_header import TestHeader


scenarios = zip(
    icmp_request_headers + icmp_reply_headers,
    icmp_request_headers_bytes + icmp_reply_headers_bytes,
    strict=False,
)
setattr_scenarios = zip(icmp_request_headers, icmp_reply_headers, strict=False)
build_icmp_reply_scenarios = setattr_scenarios


class TestICMP(TestHeader):
    @pytest.fixture(params=scenarios)
    def scenario(self, request):
        return request.param

    @pytest.fixture(params=setattr_scenarios)
    def setattr_scenario(self, request):
        return request.param

    def test_setattr(self, setattr_scenario):
        copied_header = copy.copy(setattr_scenario[0])
        copied_header.icmp_type = copy.copy(setattr_scenario[1].icmp_type)
        assert copied_header == setattr_scenario[1], (
            f"setting: {setattr_scenario[0]}.icmp_type = {copy.copy(setattr_scenario[1].icmp_type)} yielded {copied_header}; Expected value: {setattr_scenario[1]}"
        )

    @pytest.fixture(params=build_icmp_reply_scenarios)
    def build_icmp_reply_scenario(self, request):
        return request.param

    def test_build_icmp_reply(self, build_icmp_reply_scenario):
        assert build_icmp_reply_scenario[0].build_icmp_reply() == build_icmp_reply_scenario[1], (
            f"{build_icmp_reply_scenario[0]}.build_icmp_reply() returned {build_icmp_reply_scenario[0].build_icmp_reply()}; Expected value is: {build_icmp_reply_scenario[1]}"
        )
