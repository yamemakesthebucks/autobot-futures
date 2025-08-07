import pytest
from src.paper_trading.simulator import PaperExchangeSimulator
from src.paper_trading.failure_drills import drill_exchange_down, drill_partial_fill_analysis

class StubSimulator:
    def __init__(self, responses):
        """
        responses: list of either Exception or dict results
        """
        self._responses = responses.copy()
    def create_order(self, **order):
        resp = self._responses.pop(0)
        if isinstance(resp, Exception):
            raise resp
        return resp

def test_drill_exchange_down_success():
    # First two attempts fail, third succeeds
    responses = [Exception("err1"), Exception("err2"), {"filled":1,"amount":1,"price":100,"status":"closed"}]
    sim = StubSimulator(responses)
    order = {"symbol":"BTC/USDT","type":"MARKET","side":"buy","amount":1.0,"price":100.0}
    assert drill_exchange_down(sim, order, attempts=3) is True

def test_drill_exchange_down_fail():
    # All attempts fail
    responses = [Exception("err")] * 3
    sim = StubSimulator(responses)
    order = {"symbol":"BTC/USDT","type":"LIMIT","side":"sell","amount":2.0,"price":50.0}
    assert drill_exchange_down(sim, order, attempts=3) is False

def test_drill_partial_fill_analysis():
    # Mix of successful fills and errors
    responses = [
        {"filled": 1.0, "amount": 2.0, "price":100, "status":"partial"},
        {"filled": 2.0, "amount": 2.0, "price":100, "status":"closed"},
        Exception("sim error")
    ]
    sim = StubSimulator(responses)
    orders = [
        {"symbol":"","type":"","side":"","amount":2.0,"price":0.0},
        {"symbol":"","type":"","side":"","amount":2.0,"price":0.0},
        {"symbol":"","type":"","side":"","amount":2.0,"price":0.0}
    ]
    results = drill_partial_fill_analysis(sim, orders)
    assert pytest.approx(results[0]["filled_ratio"]) == 0.5
    assert pytest.approx(results[1]["filled_ratio"]) == 1.0
    assert "error" in results[2]
