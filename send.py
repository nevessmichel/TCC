#!/usr/bin/env python3
import argparse
import sys
import socket
import random
import struct
from time import sleep

from scapy.all import sendp, send, get_if_list, get_if_hwaddr
from scapy.all import Packet
from scapy.all import Ether, IP, UDP, TCP, get_if_addr, conf

from arquive import Arquive

def get_if():
    ifs=get_if_list()
    iface=None # "h1-eth0"
    for i in get_if_list():
        if "eth0" in i:
            iface=i
            break;
    if not iface:
        print("Cannot find eth0 interface")
        exit(1)
    return iface

def sendMessage(destination, message):
    addr = socket.gethostbyname(destination)
    iface = get_if()

    print(("sending on interface %s to %s" % (iface, str(addr))))
    pkt =  Ether(src=get_if_hwaddr(iface), dst='ff:ff:ff:ff:ff:ff')
    pkt = pkt /IP(dst=addr) / TCP(dport=1234, sport=random.randint(49152,65535)) / message
    #pkt.show2()
    sendp(pkt, iface=iface, verbose=False)

def doFlow():
    ip = get_if_addr(conf.iface)
    flow = Arquive("Flows/{}.csv".format(ip)).readAllLines()
    flow.pop()
    for f in flow:
        [origin, destination, entries] = f.split(",")
        entries = int(entries)
        while(entries != 0):
            sendMessage(destination,"message")
            entries -= 1

def main():
    if len(sys.argv)<3:
        print('pass 2 arguments: <destination> "<message>"')
        exit(1)

    sendMessage(sys.argv[1], sys.argv[2])


if __name__ == '__main__':
    doFlow()