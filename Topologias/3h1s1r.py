from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import Node
from mininet.node import Controller, RemoteController, OVSController
from mininet.node import CPULimitedHost, Host, Node
from mininet.node import OVSKernelSwitch, UserSwitch
from mininet.node import IVSSwitch
from mininet.cli import CLI
from mininet.log import setLogLevel, info
from mininet.link import TCLink, Intf
from subprocess import call

class LinuxRouter( Node ):
    "A Node with IP forwarding enabled."

    def config( self, **params ):
        super( LinuxRouter, self).config( **params )
        # Enable forwarding on the router
        self.cmd( 'sysctl net.ipv4.ip_forward=1' )

    def terminate( self ):
        self.cmd( 'sysctl net.ipv4.ip_forward=0' )
        super( LinuxRouter, self ).terminate()

class Topologia(Topo):

    def build( self, **_opts ):

        defaultIP = '192.168.1.1/24'  # IP address for r0-eth1
        r0 = self.addNode( 'r0', cls=LinuxRouter, ip=defaultIP )

        s1, s2 = [ self.addSwitch( s ) for s in ( 's1', 's2',) ]

        self.addLink( s1, r0, intfName2='r0-eth1', params2={ 'ip' : defaultIP } )  # for clarity
        self.addLink( s2, r0, intfName2='r0-eth2', params2={ 'ip' : '172.16.0.1/12' } )

        h1 = self.addHost( 'h1', mac='00:00:00:00:11:11', ip='192.168.1.101/24', defaultRoute='via 192.168.1.1' )
        h2 = self.addHost( 'h2', mac='00:00:00:00:11:12', ip='192.168.1.102/24',  defaultRoute='via 192.168.1.1' )
        h3 = self.addHost( 'h3', mac='00:00:00:00:11:13', ip='192.168.2.103/24', defaultRoute='via 192.168.2.1' )

        self.addLink(h1, s1)
        self.addLink(h2, s1)
        self.addLink(h3, r0)
        self.addLink(s1, r0)

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

    #Fuerzo version de IGMP
    h1.cmd('echo 2 > /proc/sys/net/ipv4/conf/h1-eth0/force_igmp_version')
    h2.cmd('echo 2 > /proc/sys/net/ipv4/conf/h2-eth0/force_igmp_version')
    h3.cmd('echo 2 > /proc/sys/net/ipv4/conf/h3-eth0/force_igmp_version')

    h3.cmd ('vlc videoplayback.mp4 udp224.1.2.3 &')
    h1.cmd ('vlc upd://@224.1.2.3 &')
    h2.cmd ('vlc upd://@224.1.2.3 &')

    #COMANDOS A SWITCHES
    s1 = net.get('s1')
    s1.cmd('ovs-vsctl set Bridge s1 protocol=OpenFlow13')

    CLI(net)
