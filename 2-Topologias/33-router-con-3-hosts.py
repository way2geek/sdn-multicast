from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import Node
from mininet.log import setLogLevel, info
from mininet.cli import CLI
from mininet.node import Controller, RemoteController, OVSController

class LinuxRouter( Node ):
    "A Node with IP forwarding enabled."

    def config( self, **params ):
        super( LinuxRouter, self).config( **params )
        # Enable forwarding on the router
        self.cmd( 'sysctl net.ipv4.ip_forward=1' )

    def terminate( self ):
        self.cmd( 'sysctl net.ipv4.ip_forward=0' )
        super( LinuxRouter, self ).terminate()


class NetworkTopo( Topo ):
    "A LinuxRouter connecting three IP subnets"

    def build( self, **_opts ):

        defaultIP = '192.168.1.1/24'  # IP address for r0-eth1
        router = self.addNode( 'r0', cls=LinuxRouter, ip=defaultIP )

        # s1, s2, s3 = [ self.addSwitch( s ) for s in ( 's1', 's2', 's3' ) ]

        h1 = self.addHost( 'h1', ip='192.168.1.100/24', defaultRoute='via 192.168.1.1' )
        h2 = self.addHost( 'h2', ip='192.168.2.100/24', defaultRoute='via 192.168.2.1' )
        h3 = self.addHost( 'h3', ip='192.168.3.100/24', defaultRoute='via 192.168.3.1' )

        # self.addLink( s1, router, intfName2='r0-eth1', params2={ 'ip' : defaultIP } )
        # self.addLink( s2, router, intfName2='r0-eth2', params2={ 'ip' : '192.168.2.1/24' } )
        # self.addLink( s3, router, intfName2='r0-eth3', params2={ 'ip' : '192.168.3.1/24' } )

        self.addLink( h1, router, intfName2='r0-eth1', params2={ 'ip' : defaultIP } )
        self.addLink( h2, router, intfName2='r0-eth2', params2={ 'ip' : '192.168.2.1/24' } )
        self.addLink( h3, router, intfName2='r0-eth3', params2={ 'ip' : '192.168.3.1/24' } )


        # for h, s in [ (h1, s1), (h2, s2), (h3, s3) ]:
        #     self.addLink( h, s )

def run():
    "Test linux router"
    topo = NetworkTopo()
    c1 = RemoteController('c1', ip='127.0.0.1')
    net = Mininet(topo=topo, controller=c1)
    # net = Mininet(topo=topo)
    net.start()
    info( '\n*** Routing Table on Router:\n' )
    info( net[ 'r0' ].cmd( 'route' ) )
    CLI( net )
    net.stop()

if __name__ == '__main__':
    setLogLevel( 'info' )
    run()