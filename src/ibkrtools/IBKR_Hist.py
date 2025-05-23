# ibkr_hist.py  ───────────────────────────────────────────
from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from src.ibkrtools.utils import *
from src.ibkrtools.truths import *
import threading, datetime as dt, time, os, pandas as pd


"""
Historical Data Fetching Script for IBKR
────────────────────────────────────────────────────────────────
Adjust the Duration and Bar Size according to your needs.
Author  : Stavros Klaoudatos
Created : 2025-05-21
MIT LICENSE
"""




# ---------------------------------------------------------


class IBapi(EWrapper, EClient):
    def __init__(self, what_to_show):
        EClient.__init__(self, self)
        self.what_to_show = what_to_show if what_to_show else 'TRADES'
        self.historical_data = []
        self.data_ready = threading.Event()

    def historicalData(self, reqId, bar):
        
        headers = SCHEMA[self.what_to_show]

        self.historical_data.append({
            headers[0]: bar.open,
            headers[1]: bar.high,
            headers[2]: bar.low,
            headers[3]: bar.close,
            headers[4]: bar.volume
        })

    def historicalDataEnd(self, reqId, start, end):
        print(f"Finished receiving data for Request ID: {reqId}")
        self.data_ready.set()



    




def fetch_data(req_id, contract, duration:str, bar_size: str, what_to_show: str,app:IBapi,end_time=None,v:bool=True)->pd.DataFrame:
    app.data_ready.clear()
    app.historical_data.clear()
    end_time = datetime.utcnow().strftime("%Y%m%d-%H:%M:%S") if not end_time else end_time
    print(f"Requesting {what_to_show} data (ReqId={req_id})...") if v else None
    app.reqHistoricalData(
        reqId=req_id,
        contract=contract,
        endDateTime=end_time,
        durationStr=duration,
        barSizeSetting=bar_size,
        whatToShow=what_to_show,
        useRTH=USE_RTH,
        formatDate=1,
        keepUpToDate=False,
        chartOptions=[]
    )
    app.data_ready.wait()
    return pd.DataFrame(app.historical_data)


  

def HistoricalData(STOCK_SYMBOLS: list, FOREX_PAIRS: list, FUTURE_SYMBOLS: list,what_to_show:str,duration:str,bar_size:str,path:str="Historical_Data",save:bool=True,v:bool=False)->pd.DataFrame:
    req_id = 1
    full_data = {}

    print("Connecting to IBKR TWS...") if v else None
    app = IBapi(what_to_show)
    app.connect('127.0.0.1', 7497, clientId=123)

    print(f"Connected with ID {123} on port 7497 from 127.0.0.1") if v else None
    api_thread = threading.Thread(target=app.run, daemon=True)
    api_thread.start()
    time.sleep(1)
    if v:
        print(f"Requesting {what_to_show} data...")
        print(f"Duration: {duration}")
        print(f"Bar Size: {bar_size}")
        print(f"Output Path: {path}")
        print("=====================\n\n")


        print(f"Requested Data: {STOCK_SYMBOLS} \n {FOREX_PAIRS} \n {FUTURE_SYMBOLS}")
        print("\n=====================\n\n")


    asset_configs = [
        (STOCK_SYMBOLS, create_stock_contract, f"{path}/Stocks"),
        (FOREX_PAIRS,   create_forex_contract, f"{path}/Forex"),
        (FUTURE_SYMBOLS, create_continuous_future, f"{path}/Futures"),
    ]

    for assets, create_contract, folder in asset_configs:
        
        for asset in assets:
            contract = create_contract(asset)
            df= fetch_data(req_id, contract, duration, bar_size, what_to_show,app,v=v);      req_id += 1 
            full_data.update({asset:df})

            if save:
                os.makedirs(folder, exist_ok=True)
                csv_path = f"{folder}/{asset.replace('/', '_')}_{bar_size.replace(' ', '')}_{duration.replace(' ', '')}.csv"
                df.to_csv(csv_path, index=False)
                print(f"Saved data for {asset} → {csv_path}") if v else None
    
    print("Task Successfuly Completed") if v else None
    
    print("Disconnected from IBKR TWS") if v else None
    print("\n\n\n")
    app.disconnect()
    return full_data