from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
import threading
import time
import datetime
import pandas as pd



# 6.5 hours = 390 minutes in a Trading Day
# 21 trading days in a month
# 252 trading days in a year


# 6.741896867752075 seconds for 1 Month, every 30 Mins -> 273/6.741896867752075 seconds = 40.5 data points per second

# 12.92949390411377 seconds for 672 data points -> 52 data points per second

# 212.9389100074768 seconds for 7982 data points ->  37.5 data points per second

dp_p_s = 37.5

s_p_dp = 1/37.5
dur =1
bs = 1

duration = '1 M'
bar_size = '15 secs'






mult =int(duration.split(' ')[0])
denom = duration.split(' ')[1]

if denom == 'W':
    dur =5
elif denom == 'M':
    dur = 21
elif denom == 'Y':
    dur = 252

b_mult = int(bar_size.split(' ')[0])
b_denom = bar_size.split(' ')[1]

if b_denom == 'hour' or b_denom == 'hours':
    bs = 6.5
elif b_denom == 'min' or b_denom == 'mins':
    bs = 390
elif b_denom == 'sec' or b_denom == 'secs':
    bs = 390*60



estimated_time = dur * mult * bs/b_mult  * s_p_dp





class IBapi(EWrapper, EClient):
    def __init__(self):
        EClient.__init__(self, self)
        self.historical_data = []
        self.data_ready = threading.Event()

    def historicalData(self, reqId, bar):
        # Append each bar as it arrives
        self.historical_data.append({
            'reqId': reqId,
            'time': bar.date,
            'bid': bar.close,
            'volume': bar.volume
        })


    def historicalDataEnd(self, reqId, start, end):
        # Signal that full data for this reqId has been received
        print(f"Finished receiving data for Request ID: {reqId}")
        self.data_ready.set()

def run_loop():
    app.run()

def create_stock_contract(symbol: str) -> Contract:
    c = Contract()
    c.symbol = symbol
    c.secType = 'STK'
    c.exchange = 'SMART'
    #c.currency = 'EUR'
    c.currency = 'USD'
    #c.primaryExchange = 'VSE'
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
    # Example: symbol="ES" for E-mini S&P; you must supply lastTradeDateOrContractMonth
    c = Contract()
    c.symbol = symbol
    c.secType = 'FUT'
    c.exchange = 'CME'
    c.currency = 'USD'
    # For a continuous front-month contract, use the nearest valid month code, e.g. "202506"
    c.lastTradeDateOrContractMonth = (datetime.datetime.today() + 
                                      datetime.timedelta(days=30)).strftime("%Y%m")
    return c

# --- Main ---
app = IBapi()
app.connect('127.0.0.1', 7497, clientId=123)

api_thread = threading.Thread(target=run_loop, daemon=True)
api_thread.start()
time.sleep(1)  # Allow connection to establish

symbols = ["NVDA","TSM"]  # Add more symbols as needed
all_data = []

req_id = 1



estimated_time = estimated_time*len(symbols)

print("Estimated Time: ",estimated_time," seconds or ",estimated_time/60," minutes or ",estimated_time/60 //60," hours and ",estimated_time/60 % 60," minutes")

for sym in symbols:
    # Prepare for new request
    app.data_ready.clear()
    app.historical_data.clear()

    # Build contract
    contract = create_stock_contract(sym)
    
    # Format endDateTime as 'YYYYMMDD HH:MM:SS'

    endTime = datetime.datetime.utcnow().strftime("%Y%m%d-%H:%M:%S")


    
    # Request 1 year of daily trade bars
    print(f"Requesting data for {sym} (ReqId={req_id})")
    print("Estimated Time: ",estimated_time," seconds or ",estimated_time/60," minutes or ",estimated_time/60 //60," hours and ",estimated_time/60 % 60," minutes")
    start_time = time.time()
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

    full_time = time.time() - start_time

    # Collect and tag data
    df = pd.DataFrame(app.historical_data)

    df['symbol'] = sym
    all_data.append(df)



    print(full_time)

    df.to_csv('US_Stocks/{}_bid.csv'.format(sym), index=False)

    req_id += 1


# Clean up
app.disconnect()

# Combine all into one DataFrame
historical_df = pd.concat(all_data, ignore_index=True)


#historical_df.to_csv('NVDA_3Y_1min.csv', index=False)

