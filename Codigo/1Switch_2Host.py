
from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import Controller, RemoteController, OVSController
from mininet.node import CPULimitedHost, Host, Node
from mininet.node import OVSKernelSwitch, UserSwitch
from mininet.node import IVSSwitch
from mininet.cli import CLI
from mininet.log import setLogLevel, info
from mininet.link import TCLink, Intf
from subprocess import call

class Topologia(Topo):

    def build(self):

        s1 = self.addSwitch('s1')

        h1 = self.addHost('h1', mac="00:00:00:00:11:11", ip="192.168.1.1/24")
        h2 = self.addHost('h2', mac="00:00:00:00:11:12", ip="192.168.1.2/24")

        self.addLink(s1,h1)
        self.addLink(s1,h2)

if __name__ == '__main__':
    setLogLevel('info')
    topo = Topologia()
    c1 = RemoteController('c1', ip='127.0.0.1')
    net = Mininet(topo=topo, controller=c1)

    h1 = net.get('h1')
    h2 = net.get('h2')
    s1 = net.get('s1')


    h1.cmd('echo 2 > /proc/sys/net/ipv4/conf/h1s1-eth0/force_igmp_version')
    h1.cmd('ip route add default via 191.168.1.254')


    h2.cmd('echo 2 > /proc/sys/net/ipv4/conf/h1s1-eth0/force_igmp_version')
    h2.cmd('ip route add default via 191.168.1.254')

    s1.cmd('ovs-vsctl set Bridge s2 protocols=OpenFlow13')

    net.start()
    CLI(net)
