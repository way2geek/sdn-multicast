from mininet.topo import Topo
from mininet.net import Mininet
from mininet.log import setLogLevel
from mininet.cli import CLI
from mininet.node import OVSSwitch, Controller, RemoteController


class SingleSwitchTopo(Topo):

    def build(self):
        s1 = self.addSwitch('s1')
        s2 = self.addSwitch('s2')

        h1 = self.addHost('h1', mac="00:00:00:00:11:11", ip="192.168.1.1/24")
        h2 = self.addHost('h2', mac="00:00:00:00:11:12", ip="192.168.1.2/24")
        h3 = self.addHost('h3', mac="00:00:00:00:11:13", ip="192.168.1.3/24")
        h4 = self.addHost('h4', mac="00:00:00:00:11:14", ip="172.16.10.10/24")
        h5 = self.addHost('h5', mac="00:00:00:00:11:14", ip="172.16.20.20/24")
        h6 = self.addHost('h6', mac="00:00:00:00:11:14", ip="172.16.30.30/24")

        self.addLink(h1, s1)
        self.addLink(h2, s1)
        self.addLink(h3, s1)
        self.addLink(h4, s2)
        self.addLink(h5, s2)
        self.addLink(h6, s2)

        self.addLink(s1, s2)


if __name__ == '__main__':
    setLogLevel('info')
    topo = SingleSwitchTopo()
    c1 = RemoteController('c1', ip='127.0.0.1')
    net = Mininet(topo=topo, controller=c1)
    net.start()

    CLI(net)
#net.stop()
