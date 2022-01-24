
import time
from predictor import Predictor

from Models.sma import SMA
from Models.wma import WMA
from Models.ema import EMA
from Models.pma import PMA

from Flows.genFlow import genFlow
from arquive import Arquive

def generateFlow():
    genFlow(["10.0.0.1","10.0.0.2","10.0.0.3"],40)
    
def doFlow(ip,packetIn):
    
    flow = Arquive("Flows/{}.csv".format(ip)).readAllLines()
    flow.pop()
    for f in flow:
        [origin, destination, entries] = f.split(",")
        entries = int(entries)
        while(entries != 0):
            packetIn()
            entries -= 1
        time.sleep(5)

def testModels():
    #models = {"SMA": SMA, "WMA": WMA, "EMA": EMA,"PMA":PMA}
    models = [SMA, WMA, EMA, PMA]
    #ipList = ["10.0.0.1","10.0.0.2","10.0.0.3"]
    ipList = ["10.0.0.1"]
    for model in models:
        predictor = Predictor(callbackFunction, model, 5)
        for ip in ipList:
            print("simulation for model={}, ip={}".format(model().getName(), ip))
            doFlow(ip,predictor.packetIn)
        predictor.stop()
        
def callbackFunction(log, window, packages, predicted):
    print("Packages: {}     Predicted: {}".format(packages, predicted))
    log.append("{},{},{},{}\n".format(time.time(),window,packages, predicted))

if(__name__ == "__main__"):
    testModels()