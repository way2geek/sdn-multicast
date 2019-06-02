#!/usr/bin/python

from mininet.net import Mininet
from mininet.node import Controller, RemoteController, OVSController
from mininet.node import CPULimitedHost, Host, Node
from mininet.node import OVSKernelSwitch, UserSwitch
from mininet.node import IVSSwitch
from mininet.cli import CLI
from mininet.log import setLogLevel, info
from mininet.link import TCLink, Intf
from subprocess import call

def myNetwork():

    net = Mininet( topo=None,
                   build=False,
                   ipBase='192.168.1.0/24')

    info( '*** Adding controller\n' )
    info( '*** Add switches\n')
    s3 = net.addSwitch('s3', cls=OVSKernelSwitch, failMode='standalone')
    s2 = net.addSwitch('s2', cls=OVSKernelSwitch, failMode='standalone')
    #root
    s1 = net.addSwitch('s1', cls=OVSKernelSwitch, failMode='standalone')

    info( '*** Add hosts\n')
    h1 = net.addHost('h1', mac="00:00:00:00:11:11", cls=Host, ip='192.168.1.11', defaultRoute='192.168.1.1')
    h2 = net.addHost('h2', mac="00:00:00:00:11:12", cls=Host, ip='192.168.1.12', defaultRoute='192.168.1.1')
    h3 = net.addHost('h3', mac="00:00:00:00:11:13", cls=Host, ip='192.168.1.13', defaultRoute='192.168.1.1')
    h4 = net.addHost('h4', mac="00:00:00:00:11:14", cls=Host, ip='192.168.1.14', defaultRoute='192.168.1.1')
    h5 = net.addHost('h5', mac="00:00:00:00:11:15", cls=Host, ip='192.168.1.15', defaultRoute='192.168.1.1')
    h6 = net.addHost('h6', mac="00:00:00:00:11:16", cls=Host, ip='192.168.1.16', defaultRoute='192.168.1.1')
    h7 = net.addHost('h7', mac="00:00:00:00:11:17", cls=Host, ip='192.168.1.17', defaultRoute='192.168.1.1')
    h8 = net.addHost('h8', mac="00:00:00:00:11:18", cls=Host, ip='192.168.1.18', defaultRoute='192.168.1.1')

    info( '*** Add links\n')

    net.addLink(s2, s1)
    net.addLink(s3, s1)

    net.addLink(h1, s2)
    net.addLink(h2, s2)
    net.addLink(h3, s2)
    net.addLink(h4, s2)

    net.addLink(h5, s3)
    net.addLink(h6, s3)
    net.addLink(h7, s3)
    net.addLink(h8, s3)

    info( '*** Starting network\n')
    net.build()
    info( '*** Starting controllers\n')
    for controller in net.controllers:
        controller.start()

    info( '*** Starting switches\n')
    net.get('s3').start([])
    net.get('s2').start([])
    net.get('s1').start([])

    info( '*** Post configure switches and hosts\n')

    CLI(net)
    net.stop()

if __name__ == '__main__':
    setLogLevel( 'info' )
    myNetwork()
