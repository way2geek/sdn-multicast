
from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import Controller, RemoteController, OVSController
from mininet.node import Host, Node
from mininet.node import OVSKernelSwitch, UserSwitch
from mininet.node import IVSSwitch
from mininet.cli import CLI
from mininet.log import setLogLevel, info
from mininet.link import TCLink, Intf
from subprocess import call


class Topologia(Topo):

    def build(self):

        info( '*** Adding switches\n')
        s1 = self.addSwitch('s1')
        s2 = self.addSwitch('s2')

        info( '*** Adding hosts\n')
        h1 = self.addHost('h1', mac="00:00:00:00:11:11", ip="192.168.1.11/24")
        h2 = self.addHost('h2', mac="00:00:00:00:11:12", ip="192.168.1.12/24")

        info( '*** Adding links\n')
        self.addLink(s1, s2)
        self.addLink(s2, s1)

        self.addLink(h1, s1)
        self.addLink(h2, s2)net

if __name__ == '__main__':
    setLogLevel('info')
    topo = Topologia()
    c1 = RemoteController('c1', ip='127.0.0.1')
    net = Mininet(topo=topo, controller=c1)
    net.start()

    #COMANDOS A LOS HOSTS
    h1 = net.get('h1')
    h2 = net.get('h2')

    #Establezco la puerta de enlace predeterminada para los paquetes IGMP
    h1.cmd('ip route add default via 192.168.1.1')
    h2.cmd('ip route add default via 192.168.1.1')

    #COMANDOS A SWITCHES
    s1 = net.get('s1')
    s2 = net.get('s2')

    #Establezco la version OPenFlow1.3 en los switches
    s1.cmd('ovs-vsctl set Bridge s1 protocols=OpenFlow13')
    s2.cmd('ovs-vsctl set Bridge s2 protocols=OpenFlow13')

    CLI(net)
