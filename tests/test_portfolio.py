import pytest
from src.backtesting.portfolio import Portfolio


def test_position_size_calculation():
    p = Portfolio(capital=1000.0, max_drawdown=0.1)
    size = p.position_size(price=50.0, risk_pct=0.01)
    # risk_amount = 1% of 1000 = 10; size = 10 / 50 = 0.2
    assert pytest.approx(size, rel=1e-6) == 0.2


def test_update_and_max_drawdown():
    p = Portfolio(capital=1000.0, max_drawdown=0.1)
    # gain first
    p.update(+100.0)
    assert pytest.approx(p.capital, rel=1e-6) == 1100.0
    # big loss but above drawdown floor (1000*(1-0.1)=900)
    p.update(-100.0)
    assert pytest.approx(p.capital, rel=1e-6) == 1000.0
    # loss breaching drawdown
    with pytest.raises(RuntimeError):
        p.update(-200.0)  # would drop to 800 < 900


def test_invalid_inputs():
    with pytest.raises(ValueError):
        Portfolio(capital=0, max_drawdown=0.1)
    with pytest.raises(ValueError):
        Portfolio(capital=1000, max_drawdown=1.5)
    p = Portfolio(capital=1000, max_drawdown=0.1)
    with pytest.raises(ValueError):
        p.position_size(price=0, risk_pct=0.01)
    with pytest.raises(ValueError):
        p.position_size(price=50, risk_pct=0)
