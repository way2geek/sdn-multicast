
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

        info( '*** Adding switches\n')
        s1 = self.addSwitch('s1')
        s2 = self.addSwitch('s2')
        s3 = self.addSwitch('s3')

        info( '*** Adding hosts\n')
        h1 = self.addHost('h1', mac="00:00:00:00:11:11", ip="192.168.1.1/24", defaultRoute='192.168.1.254')
        h2 = self.addHost('h2', mac="00:00:00:00:11:12", ip="192.168.1.2/24", defaultRoute='192.168.1.254')
        h3 = self.addHost('h3', mac="00:00:00:00:11:13", ip="192.168.1.3/24", defaultRoute='192.168.1.254')
        h4 = self.addHost('h4', mac="00:00:00:00:11:14", ip="192.168.1.4/24", defaultRoute='192.168.1.254')
        h5 = self.addHost('h5', mac="00:00:00:00:11:15", ip="192.168.1.5/24", defaultRoute='192.168.1.254')
        h6 = self.addHost('h6', mac="00:00:00:00:11:16", ip="192.168.1.6/24", defaultRoute='192.168.1.254')

        info( '*** Adding links\n')
        self.addLink(s1, s3)
        self.addLink(s2, s3)
        self.addLink(h1, s1)
        self.addLink(h2, s1)
        self.addLink(h3, s1)
        self.addLink(h4, s2)
        self.addLink(h5, s2)
        self.addLink(h6, s2)

if __name__ == '__main__':
    setLogLevel('info')
    topo = Topologia()
    c1 = RemoteController('c1', ip='127.0.0.1')
    net = Mininet(topo=topo, controller=c1)
    net.start()

    #COMANDOS A LOS HOSTS
    h1 = net.get('h1')
    h2 = net.get('h2')
    h3 = net.get('h3')
    h4 = net.get('h4')
    h5 = net.get('h5')
    h6 = net.get('h6')
    #Fuerzo version de IGMP
    h1.cmd('echo 2 > /proc/sys/net/ipv4/conf/h1-eth0/force_igmp_version')
    h2.cmd('echo 2 > /proc/sys/net/ipv4/conf/h2-eth0/force_igmp_version')
    h3.cmd('echo 2 > /proc/sys/net/ipv4/conf/h3-eth0/force_igmp_version')
    h4.cmd('echo 2 > /proc/sys/net/ipv4/conf/h4-eth0/force_igmp_version')
    h5.cmd('echo 2 > /proc/sys/net/ipv4/conf/h5-eth0/force_igmp_version')
    h6.cmd('echo 2 > /proc/sys/net/ipv4/conf/h6-eth0/force_igmp_version')
    #Establezco la puerta de enlace predeterminada para los paquetes IGMP
    #h1.cmd('ip route add default via 172.16.10.254')
    #h2.cmd('ip route add default via 172.16.20.254')
    #h3.cmd('ip route add default via 172.16.30.254')
    #h4.cmd('ip route add default via 192.168.1.254')
    #h5.cmd('ip route add default via 192.168.1.254')
    #h6.cmd('ip route add default via 192.168.1.254')

    #h3.cmd('vlc udp://@225.0.0.1 &')
    #h3.cmd('vlc udp://@225.0.0.2 &')
    #h1.cmd('vlc videoplayback.mp4 --sout udp:225.0.0.1 --loop &')
    #h2.cmd('vlc videoplayback.mp4 --sout udp:225.0.0.2 --loop &')
    #h6.cmd('vlc udp://@225.0.0.1 &')
    #h4.cmd('vlc udp://@225.0.0.1 &')
    #h5.cmd('vlc udp://@225.0.0.2 &')

    #COMANDOS A SWITCHES
    s1 = net.get('s1')
    s2 = net.get('s2')
    s3 = net.get('s3')
    #Establezco la version OPenFlow1.3 en los switches
    s1.cmd('ovs-vsctl set Bridge s1 protocol=OpenFlow13')
    s2.cmd('ovs-vsctl set Bridge s2 protocol=OpenFlow13')
    s3.cmd('ovs-vsctl set Bridge s3 protocol=OpenFlow13')

    CLI(net)
