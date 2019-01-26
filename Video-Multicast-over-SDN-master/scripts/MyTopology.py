from mininet.topo import Topo
from mininet.topolib import TreeTopo
from mininet.topolib import TorusTopo
from mininet.net import Mininet
from mininet.node import CPULimitedHost, RemoteController, OVSSwitch
from mininet.link import TCLink
from mininet.util import dumpNodeConnections
from mininet.cli  import CLI

def main():
    #Tree topology with 7 switches with a depth of 3 and fanout of 2
    topo = TreeTopo(3,2)
    #topo = TorusTopo(3,3)
    #controller=RemoteController('c0', ip='10.10.10.10', port=6633)
    net = Mininet(topo=topo, controller=RemoteController, switch=OVSSwitch)
    net.start()
    print "Dumping host connections"
    dumpNodeConnections(net.switches)
    dumpNodeConnections(net.hosts)
    net.pingAll()
    CLI(net)
    net.stop()

if __name__ == '__main__':
    main()
