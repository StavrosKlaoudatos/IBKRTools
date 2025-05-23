# tests/test_hist.py
from src.ibkrtools import IBKR_Hist as hist
from src.ibkrtools.truths import SCHEMA
import pandas as pd, types

def make_bar(o, h, l, c, v=0):
    return types.SimpleNamespace(open=o, high=h, low=l, close=c,
                                 volume=v, date="20250522 23:59:59")

def test_bar_parsing_trades():
    app = hist.IBapi("TRADES")
    fake_bar = make_bar(100, 110, 95, 105, 1_234)

    app.historicalData(1, fake_bar)
    app.historicalDataEnd(1, "", "")

    headers = SCHEMA["TRADES"]
    df = pd.DataFrame(app.historical_data)

    assert df.columns.tolist() == headers
    assert df.iloc[0].to_dict() == {
        headers[0]: 100,
        headers[1]: 110,
        headers[2]: 95,
        headers[3]: 105,
        headers[4]: 1_234,
    }

def test_bar_parsing_bid_ask():
    app = hist.IBapi("BID_ASK")
    fake_bar = make_bar(100, 110, 95, 105, 1_234)

    app.historicalData(1, fake_bar)
    app.historicalDataEnd(1, "", "")

    headers = SCHEMA["BID_ASK"]
    df = pd.DataFrame(app.historical_data)

    assert df.columns.tolist() == headers
    assert df.iloc[0].to_dict() == {
        headers[0]: 100,
        headers[1]: 110,
        headers[2]: 95,
        headers[3]: 105,
        headers[4]: 1_234,
    }
