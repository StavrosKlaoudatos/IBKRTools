"""
Pairs-trading engine for EBS–BG on VSE via the IB TWS API
Author: <your name>
"""

from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract, ComboLeg
from ibapi.order import Order
from ibapi.tag_value import TagValue

import pandas as pd
from decimal import Decimal
import threading
import datetime as dt
import time

# ---------- strategy parameters ------------------------------------------------
BAR_SIZE           = '1 min'   # size of the bar we request
WINDOW             = 50        # rolling window length
A                  = 1.6       # entry threshold |z| > A
BETA               = 1         # hedge ratio, BG units per EBS
Q                  = 1         # combo quantity
EXCHANGE           = 'VSE'
CURRENCY           = 'EUR'
DATA_FILE          = 'ebs_bg_data.csv'
# -------------------------------------------------------------------------------


def stock_contract(symbol: str) -> Contract:
    """Return a fully-specified stock contract on VSE (SMART routed)."""
    c = Contract()
    c.symbol   = symbol
    c.secType  = 'STK'
    c.currency = CURRENCY
    c.exchange = 'SMART'
    c.primaryExchange = EXCHANGE   # resolves the exact listing
    return c


def combo_contract(beta: int = 1) -> Contract:
    """Build the BAG contract: +1 EBS, −beta BG."""
    c = Contract()
    c.symbol   = 'BG,EBS'        # label not critical
    c.secType  = 'BAG'
    c.currency = CURRENCY
    c.exchange = 'SMART'
    c.primaryExchange = EXCHANGE

    # ---- leg 1: LONG EBS ------------------------------------------------------
    leg1          = ComboLeg()
    leg1.conId    = 3306538      # conId for EBS on VSE
    leg1.ratio    = 1
    leg1.action   = 'BUY'
    leg1.exchange = 'SMART'

    # ---- leg 2: SHORT BG ------------------------------------------------------
    leg2          = ComboLeg()
    leg2.conId    = 294207034    # conId for BG on VSE
    leg2.ratio    = beta
    leg2.action   = 'SELL'
    leg2.exchange = 'SMART'

    c.comboLegs = [leg1, leg2]
    return c


class PairsTrader(EWrapper, EClient):
    def __init__(self):
        EClient.__init__(self, self)

        # --- bookkeeping ------------------------------------------------------
        self.nextOrderId   = None
        self.reqIdSymbol   = {}             # map reqId → symbol
        self.data          = { 'EBS': [], 'BG': [] }   # raw closes
        self.df            = pd.DataFrame(
            columns=['time','EBS','BG','spread','mean','std','z'])
        self.position      = 0              # +1 long combo, −1 short combo, 0 flat

        # --- static contracts -------------------------------------------------
        self.contract_EBS  = stock_contract('EBS')
        self.contract_BG   = stock_contract('BG')
        self.contract_BAG  = combo_contract(BETA)

    # -------------------------------------------------------------------------
    # API callbacks
    # -------------------------------------------------------------------------
    def nextValidId(self, orderId: int):
        """First callback: we now have a valid order id → start data streams."""
        print(f'Next valid order id is {orderId}')
        self.nextOrderId = orderId
        self.start_data_streams()

    def historicalData(self, reqId, bar):
        """Initial snapshot bars (TWS dumps the past WINDOW bars)."""
        self._on_bar(reqId, bar)

    def historicalDataUpdate(self, reqId, bar):
        """Live streaming bar every minute (keepUpToDate=True)."""
        self._on_bar(reqId, bar)

    def _on_bar(self, reqId, bar):
        """Store incoming bar and invoke trading logic."""
        symbol = self.reqIdSymbol[reqId]
        ts     = bar.date   # bar.date already a ‘yyyyMMdd  HH:mm’ str
        close  = float(bar.close)

        # Append only if this timestamp is new
        if not self.data[symbol] or ts > self.data[symbol][-1][0]:
            self.data[symbol].append((ts, close))
            self.check_and_trade()          # run signal after *each* new bar

    # -------------------------------------------------------------------------
    # trading logic
    # -------------------------------------------------------------------------
    def check_and_trade(self):
        """Compute z-score and (i) update CSV (ii) enter/exit positions."""
        # Need at least one bar for both legs
        if not self.data['EBS'] or not self.data['BG']:
            return

        # Latest aligned prices (use last bar of each list)
        t_e, p_ebs = self.data['EBS'][-1]
        t_b, p_bg  = self.data['BG'][-1]

        # Guard against clock skew: require timestamps to match to the minute
        if t_e != t_b:
            return

        spread = p_ebs - BETA * p_bg

        print(spread)
        # Append to DataFrame
        row    = {'time': t_e, 'EBS': p_ebs, 'BG': p_bg, 'spread': spread}
        self.df = pd.concat([self.df, pd.DataFrame([row])], ignore_index=True)

        # Rolling stats need >= WINDOW observations
        if len(self.df) >= WINDOW:
            roll = self.df['spread'].tail(WINDOW)
            mu   = roll.mean()
            sig  = roll.std(ddof=0)
            z    = (spread - mu) / sig if sig > 0 else 0.0
            self.df.loc[self.df.index[-1], ['mean','std','z']] = mu, sig, z

            # Write every bar (cheap for small file)
            self.df.to_csv(DATA_FILE, index=False)

            # ---------- trading decisions ------------------------------------
            if self.position == 0:
                # Enter trade
                if z >  A:
                    self.send_combo_order('SELL')   # short spread
                    self.position = -1
                elif z < -A:
                    self.send_combo_order('BUY')    # long spread
                    self.position = +1
            elif self.position == +1 and z >= 0:     # long → flat
                self.send_combo_order('SELL')
                self.position = 0
            elif self.position == -1 and z <= 0:     # short → flat
                self.send_combo_order('BUY')
                self.position = 0
            
            print(f'Position: {self.position} | Z-score: {z}')

    # -------------------------------------------------------------------------
    # utility
    # -------------------------------------------------------------------------
    def start_data_streams(self):
        """Request 1-minute bars with keepUpToDate=True for both legs."""
        for reqId, contract, sym in [
            (1, self.contract_EBS, 'EBS'),
            (2, self.contract_BG , 'BG')
        ]:
            self.reqIdSymbol[reqId] = sym
            # endDateTime='', durationStr arbitrary (1 D), keepUpToDate=True
            self.reqHistoricalData(
                reqId=reqId,
                contract=contract,
                endDateTime='',
                durationStr='1 D',
                barSizeSetting=BAR_SIZE,
                whatToShow='MIDPOINT',     # or 'TRADES' if you prefer
                useRTH=0,
                formatDate=1,
                keepUpToDate=True,
                chartOptions=[]
            )

        

    def send_combo_order(self, action: str):
        """Place market BAG order with direction given by `action` ('BUY'/'SELL')."""
        order            = Order()
        order.orderId    = self.nextOrderId
        order.action     = action               # BUY = long spread, SELL = short
        order.orderType  = 'MKT'
        order.totalQuantity = Q
        order.tif        = 'GTC'
        # Ensure non-guaranteed smart routing (required for BAG MKT)
        order.smartComboRoutingParams = [TagValue('NonGuaranteed','1')]

        print(f'► Placing {action} combo order id {self.nextOrderId} @ qty={Q}')
        self.placeOrder(self.nextOrderId, self.contract_BAG, order)
        self.nextOrderId += 1                   # keep order ids unique


# -------------------------------------------------------------------------------
# main thread
# -------------------------------------------------------------------------------
if __name__ == '__main__':
    app = PairsTrader()
    app.connect('127.0.0.1', 7497, clientId=123)

    # Run the client in a secondary thread so that this script can terminate
    # gracefully (Ctrl-C) without hanging.
    api_thread = threading.Thread(target=app.run, daemon=True)
    api_thread.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print('\nStopping…')
        app.disconnect()
