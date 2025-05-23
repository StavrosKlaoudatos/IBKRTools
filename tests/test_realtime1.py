# tests/test_realtime.py
"""
Unit-tests for the RealTimeData wrapper in ibkrtools.IBKR_Realitime_Data.

Goal
----
Verify that BID / ASK price- and size-ticks correctly update the internal
best-bid-offer (bbo) cache and that a LAST price tick triggers the on_price
callback exactly once.

The test is **pure-python**: it never connects to TWS.
"""

from unittest.mock import patch
import pytest

import src.ibkrtools.IBKR_Realitime_Data as rt


@pytest.fixture(autouse=True)
def stub_contract_builders(monkeypatch):
    """
    Replace the create_*_contract helpers with no-op lambdas so we don't need a
    running IB Gateway or a real `ibapi.contract.Contract` instance.
    """
    monkeypatch.setattr(rt, "create_stock_contract", lambda sym: object())
    monkeypatch.setattr(rt, "create_forex_contract", lambda sym: object())
    monkeypatch.setattr(rt, "create_continuous_future", lambda sym: object())


def test_bbo_updates_and_last_tick_triggers_on_price(monkeypatch, tmp_path):
    # ── 1. redirect the data-folder so the test doesn't litter the repo ──
    monkeypatch.setattr(rt, "path", tmp_path.as_posix())

    # ── 2. create a minimal RealTimeData instance with one symbol ──
    app = rt.RealTimeData(stocks=["AAPL"], forex=[], futures=[])

    # reqId 0 is the only contract we asked for
    bid_ask = app.bbo[0]
    assert bid_ask == {"bid": None, "ask": None, "bidsize": None, "asksize": None}

    # ── 3. feed a BID price tick and check cache ──
    app.tickPrice(0, rt.TickTypeEnum.BID, 100.50, attrib=None)
    assert bid_ask["bid"] == 100.50 and bid_ask["ask"] is None

    # ── 4. feed an ASK price tick ──
    app.tickPrice(0, rt.TickTypeEnum.ASK, 101.00, attrib=None)
    assert bid_ask["ask"] == 101.00

    # ── 5. feed size ticks ──
    app.tickSize(0, rt.TickTypeEnum.BID_SIZE, 200)
    app.tickSize(0, rt.TickTypeEnum.ASK_SIZE, 250)
    assert bid_ask["bidsize"] == 200 and bid_ask["asksize"] == 250

    # ── 6. LAST price should call on_price once ──
    with patch.object(app, "on_price") as mock_on_price:
        app.tickPrice(0, rt.TickTypeEnum.LAST, 100.75, attrib=None)
        mock_on_price.assert_called_once()

    # ── 7. latest price cache updated ──
    assert app.latest["AAPL"] == 100.75
