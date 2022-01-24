from mininet.topo import Topo

from mininet.cli import CLI
from mininet.net import Mininet
from mininet.util import dumpNodeConnections
from mininet.log import setLogLevel

from mininet.node import RemoteController

# Traffic Control
from mininet.link import TCLink

REMOTE_CONTROLLER_IP = "127.0.0.1"

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
    #print("Dumping host connections")
    #dumpNodeConnections(net.hosts)
    CLI(net)
    net.stop()

topos = { 'TST': ( lambda: TwoSwitchTopo() ) }
# sudo mn --custom ./topo.py --topo TST --controller=remote,ip=127.0.0.1,port=6633