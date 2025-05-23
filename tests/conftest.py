# tests/conftest.py
import pytest, types
from src.ibkrtools import IBKR_Hist as hist

@pytest.fixture
def fake_bar():
    def _make(open_, high, low, close, volume=0):
        return types.SimpleNamespace(open=open_, high=high, low=low, close=close,
                                     volume=volume, date="20250101 00:00:00")
    return _make

@pytest.fixture
def stub_app():
    return hist.IBapi("TRADES")
