from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
import threading
import time
import datetime
import os
import pandas as pd

"""
Basic 15s Data Fetching Script for IBKR
────────────────────────────────────────────────────────────────
Adjust the Duration and Bar Size according to your needs.
Author  : Stavros Klaoudatos
Created : 2025-04-05
All Rights Reserved
"""












DURATION = '1 D'
BAR_SIZE = '15 secs'
USE_RTH = 0



#Add The Assets
STOCK_SYMBOLS = ["NVDA", "TSM"]             # Stocks
FOREX_PAIRS   = ["EUR/USD", "GBP/USD"]      # Forex pairs
FUTURE_SYMBOLS = ["ES", "NQ"]               # Futures symbols (continuous front-month)

class IBapi(EWrapper, EClient):
    def __init__(self):
        EClient.__init__(self, self)
        self.historical_data = []
        self.data_ready = threading.Event()

    def historicalData(self, reqId, bar):
        self.historical_data.append({
            'bid': bar.open,                #Time Averaged Bid
            'ask': bar.close                #Time Averaged Bid
        })

    def historicalDataEnd(self, reqId, start, end):
        print(f"Finished receiving data for Request ID: {reqId}")
        self.data_ready.set()


def run_loop():
    app.run()


# Contract factory functions

def create_stock_contract(symbol: str) -> Contract:
    c = Contract()
    c.symbol = symbol
    c.secType = 'STK'
    c.exchange = 'SMART'
    c.currency = 'USD'
    return c


def create_forex_contract(pair: str) -> Contract:
    base, quote = pair.split('/')
    c = Contract()
    c.symbol = base
    c.secType = 'CASH'
    c.exchange = 'IDEALPRO'
    c.currency = quote
    return c


def create_continuous_future(symbol: str) -> Contract:
    c = Contract()
    c.symbol = symbol
    c.secType = 'FUT'
    c.exchange = 'CME'
    c.currency = 'USD'
    # Front-month (approx. 30 days ahead)
    c.lastTradeDateOrContractMonth = (datetime.datetime.today() + datetime.timedelta(days=30)).strftime("%Y%m")
    return c



def fetch_data(req_id, contract, what_to_show):
    app.data_ready.clear()
    app.historical_data.clear()
    end_time = datetime.datetime.utcnow().strftime("%Y%m%d-%H:%M:%S")
    print(f"Requesting {what_to_show} data (ReqId={req_id})...")
    app.reqHistoricalData(
        reqId=req_id,
        contract=contract,
        endDateTime=end_time,
        durationStr=DURATION,
        barSizeSetting=BAR_SIZE,
        whatToShow=what_to_show,
        useRTH=USE_RTH,
        formatDate=1,
        keepUpToDate=False,
        chartOptions=[]
    )
    app.data_ready.wait()
    return pd.DataFrame(app.historical_data)


app = IBapi()
app.connect('127.0.0.1', 7497, clientId=123)
api_thread = threading.Thread(target=run_loop, daemon=True)
api_thread.start()
time.sleep(1)  

req_id = 1

asset_configs = [
    ("stock", STOCK_SYMBOLS, create_stock_contract, "Stocks"),
    ("forex", FOREX_PAIRS,   create_forex_contract, "Forex"),
    ("future", FUTURE_SYMBOLS, create_continuous_future, "Futures"),
]

for asset_type, assets, create_contract, folder in asset_configs:
    os.makedirs(folder, exist_ok=True)
    for asset in assets:
        contract = create_contract(asset)

        df_bid_ask= fetch_data(req_id, contract, "BID_ASK");      req_id += 1 #Time Averaged Bid and Ask
        df_bid_ask['asset'] = asset
        df_bid_ask['asset_type'] = asset_type

        csv_path = f"{folder}/{asset}_15sec.csv"
        df_bid_ask.to_csv(csv_path, index=False)
        print(f"Saved {asset_type} data for {asset} → {csv_path}")

app.disconnect()
