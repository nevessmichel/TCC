from curses import window
import time
from operator import attrgetter

from ryu.app import simple_switch_13
from ryu.controller import ofp_event
from ryu.controller.handler import MAIN_DISPATCHER, DEAD_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.lib import hub

from predictor import Predictor

from Models.sma import SMA
from Models.wma import WMA
from Models.ema import EMA
from Models.pma import PMA

from arquive import Arquive

class SimpleMonitor13(simple_switch_13.SimpleSwitch13):

    def __init__(self, *args, **kwargs):
        super(SimpleMonitor13, self).__init__(*args, **kwargs)
        self.datapaths = {}
        self.monitor_thread = hub.spawn(self._monitor)
        
        #module variables
        self.switchesCount = {}
        self.switchesCount_old = {}
        
        self.model = "SMA"
        self.models = {"SMA": SMA, "WMA": WMA, "EMA": EMA,"PMA":PMA}
        self.__log = None

        

    @set_ev_cls(ofp_event.EventOFPStateChange,
                [MAIN_DISPATCHER, DEAD_DISPATCHER])
    def _state_change_handler(self, ev):
        datapath = ev.datapath
        if ev.state == MAIN_DISPATCHER:
            if datapath.id not in self.datapaths:
                self.logger.debug('register datapath: %016x', datapath.id)
                self.datapaths[datapath.id] = datapath
        elif ev.state == DEAD_DISPATCHER:
            if datapath.id in self.datapaths:
                self.logger.debug('unregister datapath: %016x', datapath.id)
                del self.datapaths[datapath.id]
    
    def callbackFunction(self,log, window, packages, predicted):
        self.logger.info("Packages:", packages)
        self.logger.info("Predicted:", predicted)
        self.__log.append("{},{},{},{}\n".format(time.time(), window,packages, predicted))

    def _monitor(self):
        fileName = "Log/{}/{}_{}.csv".format(self.models[self.model]().getName(),time.time(), self.models[self.model]().getName())
        self.__log = Arquive(fileName)
        #write log header
        self.__log.append("timestamp,window,packages,predicted\n")
        self.predictor = Predictor(self.callbackFunction, self.models[self.model], 10)
        self.predictor.setStart()
        while True:
            for dp in self.datapaths.values():
                self._request_stats(dp)
            hub.sleep(10)
            self.switchesCount_old = self.switchesCount.copy()
            self.switchesCount = {}

    def _request_stats(self, datapath):
        self.logger.debug('send stats request: %016x', datapath.id)
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        
        req = parser.OFPFlowStatsRequest(datapath)
        datapath.send_msg(req)

        #req = parser.OFPPortStatsRequest(datapath, 0, ofproto.OFPP_ANY)
        #datapath.send_msg(req)

    @set_ev_cls(ofp_event.EventOFPFlowStatsReply, MAIN_DISPATCHER)
    def _flow_stats_reply_handler(self, ev):
        flow = ev.msg.to_jsondict()["OFPFlowStatsReply"]["body"][0]["OFPFlowStats"]["packet_count"]
        switch = ev.msg.datapath.id
        self.logger.info("datapath: {}     n_packets: {}".format(ev.msg.datapath.id,count))
        #self.logger.info('%s', json.dumps(ev.msg.to_jsondict(), ensure_ascii=True, indent=3, sort_keys=True))

        self.logger.info(self.switchesCount_old)
        
        delta = flow
        if(switch in self.switchesCount):
            delta = flow - self.switchesCount[switch]
        else:
            delta = self.switchesCount[switch]
        self.switchesCount[switch] = flow
        #print("________________________")
        self.predictor.packageIn(delta, time.time())