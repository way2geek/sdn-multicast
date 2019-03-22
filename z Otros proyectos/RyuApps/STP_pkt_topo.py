__author__ = 'Ehsan'
from mininet.node import CPULimitedHost
from mininet.topo import Topo
from mininet.link import Link
from mininet.net import Mininet
from mininet.log import setLogLevel, info
from mininet.node import RemoteController
from mininet.cli import CLI
from mininet.link import TCLink
"""
Instructions to run the topo:
    1. Go to directory where this filw is.
    2. run: sudo -E python STP_topo.py

This file is used in STP.md tutorial
"""


class ThreeSWloop(Topo):
    """Simple topology example."""

    def __init__(self, **opts):
        """Create custom topo."""

        # Initialize topology
        super(ThreeSWloop, self).__init__(**opts)
        #Topo.__init__(self)

        # Add hosts and switches
        h1 = self.addHost('h1')
        h2 = self.addHost('h2')
        h3 = self.addHost('h3')

        opts = dict(protocols='OpenFlow13')

        # Adding switches
        s1 = self.addSwitch('s1', dpid="0000000000000001")
        s2 = self.addSwitch('s2', dpid="0000000000000002")
        s3 = self.addSwitch('s3', dpid="0000000000000003")

        # Add links
        self.addLink(h1, s1)
        self.addLink(h2, s2)
        self.addLink(h3, s3)

        self.addLink(s2, s3)
        self.addLink(s1, s2)
        self.addLink(s1, s3)

def run():
    c = RemoteController('c', '0.0.0.0', 6633)
    net = Mininet(topo=ThreeSWloop(), host=CPULimitedHost, controller=None)
    net.addController(c)
    net.start()

    # installStaticFlows( net )
    CLI(net)
    net.stop()

# if the script is run directly (sudo custom/optical.py):
if __name__ == '__main__':
    setLogLevel('info')
    run()
