from mininet.topo import Topo
from mininet.net import Mininet
from mininet.log import setLogLevel
from mininet.cli import CLI
from mininet.node import OVSSwitch, Controller, RemoteController


class SingleSwitchTopo(Topo):

    def build(self):
        s1 = self.addSwitch('s1')
        s2 = self.addSwitch('s2')
        s3 = self.addSwitch('s3_root')

        h1 = self.addHost('h1', mac="00:00:00:00:11:11", ip="192.168.1.11/24")
        h2 = self.addHost('h2', mac="00:00:00:00:11:12", ip="192.168.1.12/24")
        h3 = self.addHost('h3', mac="00:00:00:00:11:13", ip="192.168.1.13/24")
        h4 = self.addHost('h4', mac="00:00:00:00:11:14", ip="192.168.1.14/24")
        h5 = self.addHost('h5', mac="00:00:00:00:11:15", ip="192.168.1.15/24")
        h6 = self.addHost('h6', mac="00:00:00:00:11:16", ip="192.168.1.16/24")

        self.addLink(s1, s3)
        self.addLink(s2, s3)
        # self.addLink(s1, s2)
        self.addLink(h1, s1)
        self.addLink(h2, s1)
        self.addLink(h3, s1)
        self.addLink(h4, s2)
        self.addLink(h5, s2)
        self.addLink(h6, s2)

if __name__ == '__main__':
    setLogLevel('info')
    topo = SingleSwitchTopo()
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

    #Force IGMP version
    #h1.cmd('echo 2 > /proc/sys/net/ipv4/conf/h1-eth0/force_igmp_version')
    #h2.cmd('echo 2 > /proc/sys/net/ipv4/conf/h2-eth0/force_igmp_version')
    #h3.cmd('echo 2 > /proc/sys/net/ipv4/conf/h3-eth0/force_igmp_version')
    #h4.cmd('echo 2 > /proc/sys/net/ipv4/conf/h4-eth0/force_igmp_version')
    #h5.cmd('echo 2 > /proc/sys/net/ipv4/conf/h5-eth0/force_igmp_version')
    #h6.cmd('echo 2 > /proc/sys/net/ipv4/conf/h6-eth0/force_igmp_version')

    #Default gateway
    h1.cmd('ip route add default via 192.168.1.1')
    h2.cmd('ip route add default via 192.168.1.1')
    h3.cmd('ip route add default via 192.168.1.1')
    h4.cmd('ip route add default via 192.168.1.1')
    h5.cmd('ip route add default via 192.168.1.1')
    h6.cmd('ip route add default via 192.168.1.1')

    #streaming
    #h1.cmd('vlc videoplayback.mp4 --sout udp:225.0.0.1 --loop &')
    #h2.cmd('vlc videoplayback.mp4 --sout udp:225.0.0.2 --loop &')

    #receiving
    #h3.cmd('vlc udp://@225.0.0.1 &')
    #h3.cmd('vlc udp://@225.0.0.2 &')
    #h4.cmd('vlc udp://@225.0.0.1 &')
    #h5.cmd('vlc udp://@225.0.0.2 &')
    #h6.cmd('vlc udp://@225.0.0.1 &')

    #Switches
    s1 = net.get('s1')
    s2 = net.get('s1')

    #OpenFlow 1.3 version for swtiches
    s1.cmd('ovs-vsctl set Bridge s1 protocol=OpenFlow13')
    s2.cmd('ovs-vsctl set Bridge s2 protocol=OpenFlow13')

    CLI(net)
