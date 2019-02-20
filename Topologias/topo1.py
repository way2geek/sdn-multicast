
from mininet.topo import Topo
from mininet.net import Mininet
from mininet.cli import CLI
from mininet.node import OVSSwitch, RemoteController
from mininet.log import setLogLevel, info
import json


def topoBuild():

    net = Mininet()

    topojson = {}
    with open('topo1.json') as json_file:
        print('HOLAAAAAAAA')
        topojson = json.load(json_file)
        
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
    net.addController(controller=RemoteController, port=6633)
    net.start()

    # start CLI
    CLI(net)


if __name__ == '__main__':
    topoBuild()
