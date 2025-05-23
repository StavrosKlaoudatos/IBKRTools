
from src.ibkrtools.utils import *
import time as TIME
import threading
import os
import logging
from collections import deque
import pandas as pd
from ibapi.ticktype import TickTypeEnum
from ibapi.client   import EClient
from ibapi.wrapper  import EWrapper



"""
Realtime Data Fetching Script for IBKR
────────────────────────────────────────────────────────────────
Author  : Stavros Klaoudatos
Created : 2025-05-21
MIT LICENSE
"""

path ="RealTimeData"
types = ["Stocks", "Forex", "Futures"]




class RealTimeData(EWrapper, EClient):
    def __init__(self,stocks:list,forex:list,futures:list):
        EClient.__init__(self, self)

        os.makedirs(path, exist_ok=True)
        for type in types:
            os.makedirs(f"{path}/{type}", exist_ok=True)
        self.assets = {"Stocks":stocks,"Forex":forex,"Futures":futures}
        self.symbols = stocks + forex + futures
        self.nextId = None
        self.latest = {symbol:None for symbol in self.symbols}
      
        self.stock_order = {stock:0 for stock in stocks}
        self.forex_order = {forex:0 for forex in forex}
        self.future_order = {future:0 for future in futures}
        
       
        for type in types:
            for asset in self.assets[type]:
                with open(f"{path}/{type}/{asset.replace('/', '_')}.csv", 'w') as f:
                    f.write(f'time,{asset},Bid,Ask,BidSize,AskSize\n')
                
            

        self.contracts = [create_stock_contract(asset) for asset in self.assets["Stocks"]]
        self.contracts += [create_forex_contract(asset) for asset in self.assets["Forex"]]
        self.contracts += [create_continuous_future(asset) for asset in self.assets["Futures"]]

        self.bbo = {}
        for reqId in range(len(self.contracts)):
            self.bbo.update({reqId:{'bid':None,'ask':None,'bidsize':None,'asksize':None}})
        
        self.Symbol_Path = {symbol:"Stocks" for symbol in stocks}
        self.Symbol_Path.update({symbol:"Forex" for symbol in forex})
        self.Symbol_Path.update({symbol:"Futures" for symbol in futures})
        
        self.map = {reqId:[symbol,contract] for reqId,(symbol,contract) in enumerate(zip(self.symbols,self.contracts))}
        self.latest = {symbol:None for symbol in self.symbols}







    def nextValidId(self, orderId: int):
        """
        while not market_is_open():
            
            print(f"Market is closed - {time_until_open()} until open")
            TIME.sleep(time_until_open().total_seconds()/3)
            pass
        """
        self.nextId = orderId
        self.reqMarketDataType(3)

        
        
        for reqId,contract in enumerate(self.contracts):
            self.reqMktData(reqId, contract, "", False, False, [])



    def tickPrice(self, reqId: int, tickType: int, price: float, attrib):

        if tickType == TickTypeEnum.LAST:
            ts = pd.Timestamp.utcnow()
            self.on_price(self.map[reqId][0], ts, price)
            return

        if tickType == TickTypeEnum.BID:
            self.bbo[reqId]['bid'] = price
        elif tickType == TickTypeEnum.ASK:
            self.bbo[reqId]['ask'] = price
        else:
            return

        bid = self.bbo[reqId]['bid']
        ask = self.bbo[reqId]['ask']
        if bid is not None and ask is not None:
            mid = (bid + ask) / 2
            ts = pd.Timestamp.utcnow()
            self.on_price(self.map[reqId][0], ts, mid)

    def tickSize(self, reqId: int, tickType: int, size: int):
        
        if tickType == TickTypeEnum.BID_SIZE:
            self.bbo[reqId]['bidsize'] = size
            
        elif tickType == TickTypeEnum.ASK_SIZE:
            self.bbo[reqId]['asksize'] = size


    def tickString(self, reqId: int, tickType: int, value: str):
        pass

    def on_price(self, sym: str, ts: pd.Timestamp, price: float):
        self.latest[sym] = price
        if None in self.latest.values():
            return
          
        print(f'Time: {ts}')
        for Id in range(len(self.symbols)):
            DATA_FILE = f"{path}/{self.Symbol_Path[self.symbols[Id]]}/{self.symbols[Id].replace('/', '_')}.csv"
            
            print(f"{self.symbols[Id]}       Bid: ", self.bbo[Id]['bid'],"Ask: ", self.bbo[Id]['ask'], f"Bid Size: ", self.bbo[Id]['bidsize'], "Ask Size: ", self.bbo[Id]['asksize'])
            with open(DATA_FILE, 'a') as f:
                f.write(f"{ts},{self.bbo[Id]['bid']},{self.bbo[Id]['ask']},{self.bbo[Id]['bidsize']},{self.bbo[Id]['asksize']}\n")
       
        



def Save_Realtime_Data(STOCK_SYMBOLS: list =[], FOREX_PAIRS: list=[], FUTURE_SYMBOLS: list=[]):
  


    app = RealTimeData(STOCK_SYMBOLS, FOREX_PAIRS, FUTURE_SYMBOLS)
    app.connect("127.0.0.1", 7497, clientId=122)
    threading.Thread(target=app.run, daemon=True).start()
    try:
        while True:
            TIME.sleep(0.1)
    except KeyboardInterrupt:
        app.disconnect()
