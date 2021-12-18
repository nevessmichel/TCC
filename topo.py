from mininet.topo import Topo

from mininet.cli import CLI
from mininet.net import Mininet
from mininet.util import dumpNodeConnections
from mininet.log import setLogLevel

from mininet.node import RemoteController

# Traffic Control
from mininet.link import TCLink

REMOTE_CONTROLLER_IP = "127.0.0.1"


def simpleTest():
    # Create and test a simple network
    topo = SingleSwitchTopo(n=4)

    net = Mininet(topo=topo, controller=RemoteController, autoStaticArp=True)
    net.addController("c0", controller=RemoteController,
                      ip=REMOTE_CONTROLLER_IP, port=6633)

    net.start()
    print("Dumping host connections")
    dumpNodeConnections(net.hosts)
    print("Testing network connectivity")
    net.pingAll()
    net.stop()


def perfTest():
    # Create network and run simple performance test
    topo = SingleSwitchTopo(n=4)

    net = Mininet(topo=topo, link=TCLink,
                  controller=RemoteController,
                  autoStaticArp=True)
    net.addController("c0",
                      controller=RemoteController,
                      ip=REMOTE_CONTROLLER_IP,
                      port=6633)

    net.start()
    print("Dumping host connections")
    dumpNodeConnections(net.hosts)
    print("Testing network connectivity")
    # net.pingAll()
    print("Testing bandwidth between h1 and h4")
    h1, h4 = net.get('h1', 'h4')
    net.iperf((h1, h4), l4Type='UDP')
    net.stop()


class SingleSwitchTopo(Topo):
    # Single switch connected to n hosts
    def __init__(self, n=2, **opts):
        # Initialize topology and default options
        Topo.__init__(self, **opts)
        switch = self.addSwitch('s1', protocols='OpenFlow13')
        # Python's range(N) generates 0..N-1
        for h in range(n):
            host = self.addHost('h%s' % (h + 1))
            # self.addLink(host, switch, bw=10, delay='5ms', loss=10)
            self.addLink(host, switch, bw=10)


# topos = {'singleswitchtopo': (lambda: SingleSwitchTopo(n=4))}

class TwoSwitchTopo(Topo):
    def __init__(self, n=2, **opts):
        # Initialize topology and default options
        Topo.__init__(self, **opts)
        switch = self.addSwitch('s1', protocols='OpenFlow13')
        switch2 = self.addSwitch('s2', protocols='OpenFlow13')
        self.addLink(switch, switch2, bw=10)
        # Python's range(N) generates 0..N-1
        for h in range(n):
            host = self.addHost('h%s' % (h + 1))
            # self.addLink(host, switch, bw=10, delay='5ms', loss=10)
            self.addLink(host, switch, bw=10)
        for h in range(n):
            host = self.addHost('h%s' % (h + n + 1))
            # self.addLink(host, switch, bw=10, delay='5ms', loss=10)
            self.addLink(host, switch2, bw=10)
            


if __name__ == '__main__':
    # Tell mininet to print useful information
    setLogLevel('info')
    # simpleTest()
    # perfTest()
    topo = TwoSwitchTopo(n=2)

    net = Mininet(topo=topo, link=TCLink,
                  controller=None,
                  autoStaticArp=True)
    net.addController("c0",
                      controller=RemoteController,
                      ip=REMOTE_CONTROLLER_IP,
                      port=6633)
    net.start()
    print("Dumping host connections")
    dumpNodeConnections(net.hosts)
    CLI(net)
    net.stop()

# sudo mn --custom ./single_switch.py --topo singleswitchtopo --controller=remote,ip=127.0.0.1