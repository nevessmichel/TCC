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

import time

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
        self.log = Arquive("Log/{}/{}_{}.csv".format(self.model,time.time(),self.model))
        self.predictor = Predictor(self.callbackFunction, self.models[self.model], 10)
        self.predictor.setStart(10)
        

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
    
    def callbackFunction(self, packages, predicted):
        print("Packages:", packages)
        print("Predicted:", predicted)
        self.log.append("{},{},{}\n".format(time.time(),packages, predicted))

    def _monitor(self):
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

    def addFlow(self, datapath_id, package_count):
        if(datapath_id not in self.switchesCount):
            self.switchesCount[datapath_id] = package_count
        else:
            self.switchesCount[datapath_id] += package_count

    @set_ev_cls(ofp_event.EventOFPFlowStatsReply, MAIN_DISPATCHER)
    def _flow_stats_reply_handler(self, ev):
        body = ev.msg.body

        """
        self.logger.info('datapath         '
                         'in-port  eth-dst           '
                         'out-port packets  bytes')
        self.logger.info('---------------- '
                         '-------- ----------------- '
                         '-------- -------- --------')
        """
        switch = None
        for stat in sorted([flow for flow in body if flow.priority == 1],
                           key=lambda flow: (flow.match['in_port'],
                                             flow.match['eth_dst'])):
            
            in_port = stat.match['in_port']
            out_port = stat.instructions[0].actions[0].port
            switch = ev.msg.datapath.id
            self.addFlow(ev.msg.datapath.id, stat.packet_count)

            """self.logger.info('%016x %8x %17s %8x %8d %8d',
                             ev.msg.datapath.id,
                             stat.match['in_port'], stat.match['eth_dst'],
                             stat.instructions[0].actions[0].port,
                             stat.packet_count, stat.byte_count)
            """
        #print(switch)
        print(self.switchesCount_old)
        if(switch):
            if(switch in self.switchesCount_old):
                delta = self.switchesCount[switch] - self.switchesCount_old[switch]
            else:
                delta = self.switchesCount[switch]
            #print("________________________")
            self.predictor.packageIn(delta, time.time())

    @set_ev_cls(ofp_event.EventOFPPortStatsReply, MAIN_DISPATCHER)
    def _port_stats_reply_handler(self, ev):
        body = ev.msg.body

        self.logger.info('datapath         port     '
                         'rx-pkts  rx-bytes rx-error '
                         'tx-pkts  tx-bytes tx-error')
        self.logger.info('---------------- -------- '
                         '-------- -------- -------- '
                         '-------- -------- --------')
        for stat in sorted(body, key=attrgetter('port_no')):
            self.logger.info('%016x %8x %8d %8d %8d %8d %8d %8d',
                             ev.msg.datapath.id, stat.port_no,
                             stat.rx_packets, stat.rx_bytes, stat.rx_errors,
                             stat.tx_packets, stat.tx_bytes, stat.tx_errors)