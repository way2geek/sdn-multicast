
from mininet.topo import Topo
from mininet.net import Mininet
from mininet.cli import CLI
from mininet.node import OVSSwitch, RemoteController
from mininet.log import setLogLevel, info
import json


def topoBuild():

    net = Mininet()

    filejson = open("/home/bruno/Escritorio/sdn-multicast-version2/Topologias/json/topoLinear.json")
    topojson = json.load(filejson)

    existe_link = {}

    #cargo HOSTS
    for host in topojson['hosts']:
        net.addHost(host, ip = topojson['hosts'][host]['ip'])


    #cargo SWITCHES
    for switch in topojson['switches']:
        net.addSwitch(switch, cls=OVSSwitch, protocols="OpenFlow13")
        existe_link[switch] = {}


    #cargo SERVIDORES
    for servidor in topojson['servidores']:
        net.addHost(servidor, ip=topojson['servidores'][servidor]['ip'])


    #Creo links entre SWITCHES
    for swname in topojson['switches']:
        switch_ad = topojson['switches'][swname] #obtengo switches que se encuentran conectados con el swname del primer for
        for swname_ad in switch_ad:
            if swname_ad not in existe_link[swname]: #si el switch no se encuentra en los conectados con swname agrega link
                local_port = switch_ad[swname_ad]
                remote_port = topojson['switches'][swname_ad][swname]
                net.addLink(swname, swname_ad, port1 = local_port, port2 = remote_port)
                #marco los links creados
                existe_link[swname][swname_ad] = True
                existe_link[swname_ad][swname] = True

    #Creo links entre HOSTS y SERVIDORES con SWITCHES
    for host in topojson['hosts']:
        host_dic = topojson['hosts'][host]
        net.addLink(host, host_dic['switch'], port2 = host_dic['port'])


    for servidor in topojson['servidores']:
        servidor_dic = topojson['servidores'][servidor]
        net.addLink(servidor, servidor_dic['switch'], port2 = servidor_dic['port'])


    # add controller and start network
    setLogLevel('info')
    net.addController(controller=RemoteController, port=6633)
    net.start()

    for host in topojson['hosts']:
        h = net.get(host)
        h.cmd('echo 2 > /proc/sys/net/ipv4/conf/{}-eth0/force_igmp_version'.format(host))
        h.cmd('ip route add default via 10.0.0.254')

    #cargo SWITCHES
    for switch in topojson['switches']:
        s = net.get(switch)
        s.cmd('ovs-vsctl set Bridge s1 protocol=OpenFlow13')

    #cargo SERVIDORES
    for servidor in topojson['servidores']:
        s = net.get(servidor)
        s.cmd('echo 2 > /proc/sys/net/ipv4/conf/{}-eth0/force_igmp_version'.format(servidor))
        s.cmd('ip route add default via 10.0.0.254')

    # start CLI
    CLI(net)


if __name__ == '__main__':
    topoBuild()
