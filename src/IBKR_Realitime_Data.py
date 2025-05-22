import threading
import time as TIME
import logging
import pandas as pd
from collections import deque

from ibapi.client   import EClient
from ibapi.wrapper  import EWrapper
from ibapi.contract import Contract
from ibapi.order    import Order
from ibapi.ticktype import TickTypeEnum


from datetime import datetime, time, timedelta
import pytz, holidays


DATA_FILE    = "Data.csv"


def stock_contract(con_id: int) -> Contract:

    c = Contract()
    c.conId    = con_id
    c.secType  = "STK"
    c.exchange = "SMART"
    c.currency = "USD"
    return c


def market_is_open():
    try:
        eastern_tz = pytz.timezone('US/Eastern')
        current_time_eastern = datetime.now(eastern_tz)

        nyse_holidays = holidays.NYSE()
        today_date_str = current_time_eastern.strftime('%Y-%m-%d')
        is_holiday = nyse_holidays.get(today_date_str)
        if is_holiday:
            return False

        day_of_week = current_time_eastern.weekday()
        if day_of_week == 5 or day_of_week == 6:
            print(f"Weekend - {current_time_eastern}")
            return False

        market_open_time = time(9, 30)
        market_close_time = time(16, 30)

        if market_open_time <= current_time_eastern.time() <= market_close_time:


            return True
        else:
            print(f"Market is closed - {current_time_eastern}")

            print(f"Time until market open: {market_open_time - current_time_eastern.time()}")
            return False
    except Exception as e:
        print( "Market check error: {e}")
        return False
    




def time_until_open() -> timedelta:
    eastern      = pytz.timezone("US/Eastern")
    now          = datetime.now(eastern)
    nyse_holidays = holidays.NYSE()
  
    open_t  = time(9, 30)
    close_t = time(16, 0)

    today_is_holiday = now.date() in nyse_holidays
    today_is_weekend = now.weekday() >= 5        
    trading_day      = (not today_is_weekend) and (not today_is_holiday)

    if trading_day and open_t <= now.time() <= close_t:
        return timedelta(0)                       

    if trading_day and now.time() < open_t:
        next_open_date = now.date()
    else:

        next_open_date = now.date()
        while True:
            next_open_date += timedelta(days=1)
            if (next_open_date.weekday() < 5) and (next_open_date not in nyse_holidays):
                break

    next_open_naive = datetime.combine(next_open_date, open_t)   
    next_open_dt    = eastern.localize(next_open_naive)         

    delta = next_open_dt - now
    return delta



class RealTimeData(EWrapper, EClient):
    def __init__(self):
        EClient.__init__(self, self)
        self.nextId = None
        self.latest = {'S1': None, 'S2': None}
      
        self.book = {
            'S1': {'pos': 0, 'avg': 0.0},
            'S2':  {'pos': 0, 'avg': 0.0}
        }


        with open(DATA_FILE, 'w') as f:
            f.write('time,S1,S2,S1_bid,S1_ask,S2_bid,S2_ask,S1_bidsize,S2_bidsize,S1_asksize,S2_asksize\n')



        self.bbo = {1:{'bid':None,'ask':None,'bidsize':None,'asksize':None}, 2:{'bid':None,'ask':None,'bidsize':None,'asksize':None}}
        self.conId = {
            'S1': 4815747, #Test Contract Ids for NVDA and TSM
            'S2':  6223250
        }
        self.SID = {1:"S1", 2:"S2"}



    



    def nextValidId(self, orderId: int):

        while not market_is_open():
            
            print(f"Market is closed - {time_until_open()} until open")
            TIME.sleep(time_until_open().total_seconds()/3)
            pass

        self.nextId = orderId
        log.info(f"Next valid ID = {orderId}")
        self.reqMarketDataType(3)

        for reqId, sym, cid in [(1, 'S1', self.conId['S1']), (2, 'S2', self.conId['S2'])]:
            self.reqMktData(reqId, stock_contract(cid), "", False, False, [])




    def tickPrice(self, reqId: int, tickType: int, price: float, attrib):

        if tickType == TickTypeEnum.LAST:
            ts = pd.Timestamp.utcnow()
            self.on_price('S1' if reqId == 1 else 'S2', ts, price)
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
            self.on_price('S1' if reqId == 1 else 'S2', ts, mid)

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
        for Id in [1,2]:
            
            print(f"{self.SID[Id]}       Bid: ", self.bbo[Id]['bid'],"Ask: ", self.bbo[Id]['ask'], f"Bid Size: ", self.bbo[Id]['bidsize'], "Ask Size: ", self.bbo[Id]['asksize'])
        with open(DATA_FILE, 'a') as f:
            f.write(f"{ts},{self.latest['S1']},{self.latest['S2']},{self.bbo[1]['bid']},{self.bbo[1]['ask']},{self.bbo[2]['bid']},{self.bbo[2]['ask']},{self.bbo[1]['bidsize']},{self.bbo[2]['bidsize']},{self.bbo[1]['asksize']},{self.bbo[2]['asksize']}\n")
       
        print("Bid 1: ", self.bbo[1]['bid'],"Ask 1: ", self.bbo[1]['ask'], f"Bid Size: ", self.bbo[1]['bidsize'], "Ask Size: ", self.bbo[1]['asksize'])
        print("Bid 2: ", self.bbo[2]['bid'],"Ask 2: ", self.bbo[2]['ask'], f"Bid Size: ", self.bbo[2]['bidsize'], "Ask Size: ", self.bbo[2]['asksize'])
        

  
if __name__ == "__main__":
    app = RealTimeData()
    app.connect("127.0.0.1", 7497, clientId=77)
    threading.Thread(target=app.run, daemon=True).start()
    try:
        while True:
            TIME.sleep(0.1)
    except KeyboardInterrupt:
        log.info("Stopping …")
        app.disconnect()
