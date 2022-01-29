
#system functions
import os, sys, time
from statistics import mode
#seconds to datetime lib
from datetime import datetime
# import lib to process tcpdump
from scapy.utils import RawPcapReader
# import scapy parser for ethernet protocol
from scapy.layers.l2 import Ether
# import scapy parser for IPV4 protocol
from scapy.layers.inet import IP

from predictor import Predictor

from Models.sma import SMA
from Models.wma import WMA
from Models.ema import EMA
from Models.pma import PMA

from Flows.genFlow import genFlow

from arquive import Arquive

def test():
    genFlow(["10.0.0.1","10.0.0.2","10.0.0.3"],40)
    
class Test:
    def __init__(self):
        self.log = None
        self.frames = 0

    def doFlow(ip,packetIn):
        flow = Arquive("Flows/{}.csv".format(ip)).readAllLines()
        flow.pop()
        for f in flow:
            [origin, destination, entries] = f.split(",")
            entries = int(entries)
            while(entries != 0):
                packetIn()
                entries -= 1
                time.sleep(0.5)
            time.sleep(2)

    def pcap(self, file_name):
        print('Opening {}...'.format(file_name))
        #models = {"SMA": SMA, "WMA": WMA, "EMA": EMA,"PMA":PMA}
        models = [SMA]
        # size of window
        size = 10
        #interval in secs
        interval = 60
        
        # package counter
        count = 0
        for model in models:
            fileName = "Log/{}/{}_{}.csv".format(model.getName(),time.time(), model.getName())
            self.log = Arquive(fileName)
            #write log header
            self.log.append("timestamp,window,packages,predicted\n")
            predictor = Predictor(self.callbackFunction, model, size)
            predictor.setInterval(interval)
            predictor.setOffline()
            # iterate in all packages as a vector of classes
            for (pkt_data, pkt_metadata,) in RawPcapReader(file_name):
                #Ethernet parser
                ether_pkt = Ether(pkt_data)
                #check if it's LLC protocol
                if 'type' not in ether_pkt.fields:
                    #skip package
                    continue
                # ignore non-IPv4 packets
                if ether_pkt.type != 0x0800:
                    #skip package
                    continue
                #parse IPV4 package
                ip_pkt = ether_pkt[IP]
                # Ignore non-UDP packet
                if ip_pkt.proto != 17:
                    # skip package
                    continue
                # increment counter
                count += 1
                # verify if is first iteration
                if count == 1:
                    # set model start time
                    predictor.setStart(pkt_metadata.sec)
                # send package time to model
                predictor.packetInOffline(pkt_metadata.sec)
            print(model.getName(),"number of packets:",count)

            # end model
            predictor.stop()
            time.sleep(5)
            print("frames:",self.frames)
        
    def callbackFunction(self,window, packages, predicted):
        #print("Packages: {}     Predicted: {}".format(packages, predicted))
        #print("Window: {}".format(window))
        self.frames+=1
        self.log.append("{},{},{},{}\n".format(time.time(),window,packages, predicted))

if(__name__ == "__main__"):
    Test().pcap("Data/1999/week3/monday.tcpdump")
