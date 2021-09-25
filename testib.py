import sys
sys.path.append('C:/TWS API/source/pythonclient')

from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
from threading import Timer

class TestIB(EWrapper, EClient):
    def __init__(self):
        EClient.__init__(self, self)

    def error(self, reqId, errorCode, errorString):
        print("Error: ", reqId, " ", errorCode, " ", errorString)

    def contractDetails(self, reqId, contractDetails):
        print("contractDetails: ", reqId, " ", contractDetails, "\n")
        print(type(contractDetails))

    def contractDetailsEnd(self, reqId):
        print("\ncontractDetails End\n")

    def nextValidId(self, orderId):
        self.start()

    def start(self):
        contract = Contract()
        contract.symbol = "SPX"
        contract.secType = "OPT"
        contract.exchange = "CBOE"
        contract.currency = "USD"
        contract.lastTradeDateOrContractMonth = "202202"  # Feb 2022
        self.reqContractDetails(1, contract)

    def stop(self):
        self.done = True
        self.disconnect()

def runib():
    app = TestIB()
    app.nextOrderId = 0
    app.connect("127.0.0.1", 7497, 0)
    Timer(4, app.stop).start()
    app.run()

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    runib()
