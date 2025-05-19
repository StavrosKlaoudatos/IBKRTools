from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
import threading
import time
import datetime
import pandas as pd

duration = '1 M'
bar_size = '15 secs'


class IBapi(EWrapper, EClient):
    def __init__(self):
        EClient.__init__(self, self)
        self.historical_data = []
        self.data_ready = threading.Event()

    def historicalData(self, reqId, bar):
        self.historical_data.append({
            'reqId': reqId,
            'time': bar.date,
            'bid': bar.close,
            'volume': bar.volume
        })

    def historicalDataEnd(self, reqId, start, end):
        print(f"Finished receiving data for Request ID: {reqId}")
        self.data_ready.set()

def run_loop():
    app.run()

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

    c.lastTradeDateOrContractMonth = (datetime.datetime.today() + 
                                      datetime.timedelta(days=30)).strftime("%Y%m")
    return c


app = IBapi()
app.connect('127.0.0.1', 7497, clientId=123)

api_thread = threading.Thread(target=run_loop, daemon=True)
api_thread.start()
time.sleep(1)  

symbols = ["NVDA","TSM"]  
all_data = []

req_id = 1



for sym in symbols:

    app.data_ready.clear()
    app.historical_data.clear()
    
    contract = create_stock_contract(sym)


    print(f"Requesting data for {sym} (ReqId={req_id})")

    app.reqHistoricalData(
        reqId=req_id,
        contract=contract,
        endDateTime=endTime,
        durationStr=duration,
        barSizeSetting=bar_size,
        whatToShow="BID",
        useRTH=0,
        formatDate=1,
        keepUpToDate=False,
        chartOptions=[]
    )

    print(f"Requested data for {sym} (ReqId={req_id})")
    app.data_ready.wait()  # Block until data is fully received
    
    df = pd.DataFrame(app.historical_data)
    df['symbol'] = sym
    all_data.append(df)
    df.to_csv(f'{sym}_bid.csv'), index=False)

    req_id += 1


app.disconnect()
historical_df = pd.concat(all_data, ignore_index=True)
