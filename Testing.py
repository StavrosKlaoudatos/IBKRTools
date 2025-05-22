from src.IBKR_Hist import *
from src.utils import *



what_to_show = "BID_ASK"
duration = "1 D"
bar_size = "15 mins"



STOCK_SYMBOLS = ["NVDA", "TSM"]             # Stocks
FOREX_PAIRS   = ["EUR/USD", "GBP/USD"]      # Forex pairs
FUTURE_SYMBOLS = ["ES", "NQ"]               # Futures symbols (continuous front-month)




HistoricalData(STOCK_SYMBOLS, FOREX_PAIRS, FUTURE_SYMBOLS,what_to_show,duration,bar_size)


