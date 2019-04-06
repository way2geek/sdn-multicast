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
import time

TIEMPO_COMIENZO_STREAMING = 3
TIEMPO_FIN_STREAMING = 5

TIEMPO_PRIMERA_SUSCRIPCION = 10
TIEMPO_ENTRE_SUSCRIPCIONES = 0.5

TIEMPO_REPODUCCION = 45

TIEMPO_PRIMERA_DESUSCRIPCION = TIEMPO_REPODUCCION*1.5
TIEMPO_ENTRE_DESUSCRIPCIONES = 1

class Topologia(Topo):

    def build(self):
        info( '*** Adding switches\n')
        s1 = self.addSwitch('s1')
        s2 = self.addSwitch('s2')

        info( '*** Adding hosts\n')
        h1 = self.addHost('h1', mac="00:00:00:00:11:11", ip="192.168.1.11/24")
        h2 = self.addHost('h2', mac="00:00:00:00:11:12", ip="192.168.1.12/24")
        h3 = self.addHost('h3', mac="00:00:00:00:11:13", ip="192.168.1.13/24")
        h4 = self.addHost('h4', mac="00:00:00:00:11:14", ip="192.168.1.14/24")
        h5 = self.addHost('h5', mac="00:00:00:00:11:15", ip="192.168.1.15/24")
        h6 = self.addHost('h6', mac="00:00:00:00:11:16", ip="192.168.1.16/24")
        h7 = self.addHost('h7', mac="00:00:00:00:11:17", ip="192.168.1.17/24")
        h8 = self.addHost('h8', mac="00:00:00:00:11:18", ip="192.168.1.18/24")
        h9 = self.addHost('h9', mac="00:00:00:00:11:19", ip="192.168.1.19/24")
        h10 = self.addHost('h10', mac="00:00:00:00:11:20", ip="192.168.1.20/24")

        info( '*** Adding links\n')
        self.addLink(s1, s2, 1, 1)
        self.addLink(h1, s1, 1, 11)
        self.addLink(h2, s1, 1, 2)
        self.addLink(h3, s1, 1, 3)
        self.addLink(h4, s1, 1, 4)
        self.addLink(h5, s1, 1, 5)
        self.addLink(h6, s1, 1, 6)
        self.addLink(h7, s1, 1, 7)
        self.addLink(h8, s1, 1, 8)
        self.addLink(h9, s1, 1, 9)
        self.addLink(h10, s1, 1, 10)

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
    h7 = net.get('h7')
    h8 = net.get('h8')
    h9 = net.get('h9')
    h10 = net.get('h10')

    #Fuerzo version de IGMP
    h1.cmd('echo 2 > /proc/sys/net/ipv4/conf/h1-eth0/force_igmp_version')
    h2.cmd('echo 2 > /proc/sys/net/ipv4/conf/h2-eth0/force_igmp_version')
    h3.cmd('echo 2 > /proc/sys/net/ipv4/conf/h3-eth0/force_igmp_version')
    h4.cmd('echo 2 > /proc/sys/net/ipv4/conf/h4-eth0/force_igmp_version')
    h5.cmd('echo 2 > /proc/sys/net/ipv4/conf/h5-eth0/force_igmp_version')
    h6.cmd('echo 2 > /proc/sys/net/ipv4/conf/h6-eth0/force_igmp_version')
    h7.cmd('echo 2 > /proc/sys/net/ipv4/conf/h7-eth0/force_igmp_version')
    h8.cmd('echo 2 > /proc/sys/net/ipv4/conf/h8-eth0/force_igmp_version')
    h9.cmd('echo 2 > /proc/sys/net/ipv4/conf/h9-eth0/force_igmp_version')
    h10.cmd('echo 2 > /proc/sys/net/ipv4/conf/h10-eth0/force_igmp_version')

    #Establezco la puerta de enlace predeterminada para los paquetes IGMP
    h1.cmd('ip route add default via 192.168.1.1')
    h2.cmd('ip route add default via 192.168.1.1')
    h3.cmd('ip route add default via 192.168.1.1')
    h4.cmd('ip route add default via 192.168.1.1')
    h5.cmd('ip route add default via 192.168.1.1')
    h6.cmd('ip route add default via 192.168.1.1')
    h7.cmd('ip route add default via 192.168.1.1')
    h8.cmd('ip route add default via 192.168.1.1')
    h9.cmd('ip route add default via 192.168.1.1')
    h10.cmd('ip route add default via 192.168.1.1')

    #COMANDOS A SWITCHES
    s1 = net.get('s1')
    s2 = net.get('s2')

    #Establezco la version OPenFlow1.3 en los switches
    s1.cmd('ovs-vsctl set Bridge s1 protocols=OpenFlow13')
    s2.cmd('ovs-vsctl set Bridge s2 protocols=OpenFlow13')

    #Ejecuto escucha
    time.sleep(TIEMPO_PRIMERA_SUSCRIPCION)
    print "empieza a escuchar..."
    local_time = time.ctime(time.time())
    print ("Local time:", local_time)

    h1.cmd('vlc udp://@225.0.0.1 &')
    time.sleep(TIEMPO_ENTRE_SUSCRIPCIONES)
    h2.cmd('vlc udp://@225.0.0.1 &')
    time.sleep(TIEMPO_ENTRE_SUSCRIPCIONES)
    h3.cmd('vlc udp://@225.0.0.1 &')
    time.sleep(TIEMPO_ENTRE_SUSCRIPCIONES)
    h4.cmd('vlc udp://@225.0.0.1 &')
    time.sleep(TIEMPO_ENTRE_SUSCRIPCIONES)
    h5.cmd('vlc udp://@225.0.0.1 &')
    time.sleep(TIEMPO_ENTRE_SUSCRIPCIONES)
    h6.cmd('vlc udp://@225.0.0.1 &')
    time.sleep(TIEMPO_ENTRE_SUSCRIPCIONES)
    h7.cmd('vlc udp://@225.0.0.1 &')
    time.sleep(TIEMPO_ENTRE_SUSCRIPCIONES)
    h8.cmd('vlc udp://@225.0.0.1 &')
    time.sleep(TIEMPO_ENTRE_SUSCRIPCIONES)
    h9.cmd('vlc udp://@225.0.0.1 &')

    print "fin escuchas..."
    local_time = time.ctime(time.time())
    print ("Local time:", local_time)

    # Ejecuto streaming
    time.sleep(TIEMPO_COMIENZO_STREAMING)
    print "Voy a hacer streaming"
    local_time = time.ctime(time.time())
    print ("Local time:", local_time)

    h10.cmd('vlc videoplayback.mp4 --sout udp:225.0.0.1 --loop &')

    #Desuscripciones
    time.sleep(TIEMPO_PRIMERA_DESUSCRIPCION)
    print "Voy a desuscribirme"
    local_time = time.ctime(time.time())
    print ("Local time:", local_time)

    h1.cmd('pkill vlc')
    time.sleep(TIEMPO_ENTRE_DESUSCRIPCIONES)
    h2.cmd('pkill vlc')
    time.sleep(TIEMPO_ENTRE_DESUSCRIPCIONES)
    h3.cmd('pkill vlc')
    time.sleep(TIEMPO_ENTRE_DESUSCRIPCIONES)
    h4.cmd('pkill vlc')
    time.sleep(TIEMPO_ENTRE_DESUSCRIPCIONES)
    h5.cmd('pkill vlc')
    time.sleep(TIEMPO_ENTRE_DESUSCRIPCIONES)
    h6.cmd('pkill vlc')
    time.sleep(TIEMPO_ENTRE_DESUSCRIPCIONES)
    h7.cmd('pkill vlc')
    time.sleep(TIEMPO_ENTRE_DESUSCRIPCIONES)
    h8.cmd('pkill vlc')
    time.sleep(TIEMPO_ENTRE_DESUSCRIPCIONES)
    h9.cmd('pkill vlc')

    print "Fin desuscripciones..."
    local_time = time.ctime(time.time())
    print ("Local time:", local_time)

    time.sleep(TIEMPO_FIN_STREAMING)
    print "fin streaming"
    local_time = time.ctime(time.time())
    print ("Local time:", local_time)
    h10.cmd('pkill vlc')

    CLI(net)
