from ibapi.contract import Contract
from datetime import datetime, timedelta, time
import pytz, holidays








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
    c.lastTradeDateOrContractMonth = (datetime.today() + timedelta(days=30)).strftime("%Y%m")
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