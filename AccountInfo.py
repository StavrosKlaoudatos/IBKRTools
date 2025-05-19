from ibapi.client     import *
from ibapi.wrapper    import *
from ibapi.contract   import *
from ibapi.order      import *
from ibapi.common     import *
import numpy as np
import pandas as pd, logging, threading, time, uuid


DATA_FILE  = "AccountInfo.csv"
LOG_FILE   = "AccountInfo.log"






logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.FileHandler(LOG_FILE), logging.StreamHandler()],
)
log = logging.getLogger(__name__)

# ── contract helpers ────────────────────────────────────────────────────



def stock_contract(con_id: int) -> Contract:
        """Create a minimal STK contract for the Vienna Stock Exchange (VSE)."""
        c = Contract()
        c.conId    = con_id
        c.secType  = "STK"
        c.exchange = "VSE"
        c.currency = "EUR"
        return c



# ── app ──────────────────────────────────────────────────────────────────
class AccountInfo(EWrapper, EClient):
    def __init__(self):
        EClient.__init__(self, self)

        self.nextId      = None
        self.data        = {'NetLiquidity': [],'PnL': []}
        self.df          = pd.DataFrame(
            columns=['time','NetLiquidity',]
        )
        self.PnL  = 0   
        self.NetLiquidity = 0
        self.Sharpe = 0                       

        self.data_file = DATA_FILE
        with open(self.data_file, 'w') as f:
            f.write('time,NetLiquidity,PnL,Sharpe\n')

    # ── lifecycle ────────────────────────────────────────────────────────


    def error(self, reqId: TickerId, errorCode: int, errorString: str, b):
        log.error(f"{reqId} {errorCode} {errorString}")


    def nextValidId(self, orderId: int):
        self.start()

    def updatePortfolio(self, contract, position, marketPrice, marketValue, averageCost, unrealizedPNL, realizedPNL, accountName):
        print("Contract: ",contract,"Position: ",position,"Market Price: ",marketPrice,"Market Value: ",marketValue,"Average Cost: ",averageCost,"Unrealized PnL: ",unrealizedPNL,"Realized PnL: ",realizedPNL,"Account Name: ",accountName)
        """
        self.NetLiquidity = position
        self.Sharpe = (self.df["NetLiquidity"][len(self.df["NetLiquidity"])] - self.df["NetLiquidity"][0])/np.std(self.df["NetLiquidity"])
        
        
        self.df["time"] = pd.Timestamp.utcnow()
        self.df["NetLiquidity"] = self.NetLiquidity
        self.df["PnL"] = marketValue-averageCost
        self.df["Sharpe"] = self.Sharpe
        self.df["Unrealised PnL"] = unrealizedPNL
        self.df["Realised PnL"] = realizedPNL"""


    def updateAccountValue(self, key, val, currency, accountName):


        K = key.replace(" ","")






        if K in ["NetLiquidation","AccountCode","AccruedCash","AvailableFunds","BuyingPower","CashBalance","RealizedPnL","TotalCashBalance","UnrealizedPnL"]:
            




            #log.info(f"{key} {val} {currency} {accountName}")
            print("Key: ",key,"Value: ",val,"Currency: ",currency,"Account Name: ",accountName)
        

        


            

    def updateAccountTime(self, timeStamp):
        print("Timestamp: ",timeStamp)

    
    def accountDownloadEnd(self, accountName):
        print("Account Name: ",accountName)
        



    def start(self):
        self.reqAccountUpdates(True, "")
    
    def stop(self):
        self.reqAccountUpdates(False, "")


# ── run ──────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app = AccountInfo()
    app.connect("127.0.0.1", 7497, clientId=111)
    threading.Thread(target=app.run, daemon=True).start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        log.info("Stopping …")
        app.disconnect()
