from ibapi.contract import Contract
import datetime




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