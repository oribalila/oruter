import pytest


class TestHeader:
    @pytest.fixture(params=[])
    def scenario(self, request):
        return request.param

    def test_bytes_constructor(self, scenario):
        class_type = type(scenario[0])
        bytes_constructed = class_type.bytes_constructor(scenario[1])
        assert scenario[0] == bytes_constructed, (
            f"bytes_constructor({scenario[1]}) returned {bytes_constructed}; Expected value is: {scenario[0]}"
        )

    def test_bytes(self, scenario):
        assert bytes(scenario[0]) == scenario[1], (
            f"bytes({scenario[0]}) returned {bytes(scenario[0])}; Expected value is: {scenario[1]}"
        )
