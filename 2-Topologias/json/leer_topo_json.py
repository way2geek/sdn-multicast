#idem archivo net.py Noruegos pero ajustado a lo nuestro

from mininet.net import Mininet
from mininet.cli import CLI
from mininet.node import OVSSwitch, RemoteController
import json

def net():
    net = Mininet()

    # read topology file
    #TODO: este campo podria pasarse como parametro al ejecutar el script
    filejson = open("topologia_topo_learner1.json")
    topojson = json.load(filejson)

    # create topology
    link_exists = {}

    for switch_name in topojson['switches']:
        net.addSwitch(switch_name, cls=OVSSwitch, protocols="OpenFlow13")
        link_exists[switch_name] = {}

    for host_name in topojson['hosts']:
        net.addHost(host_name, ip=topojson['hosts'][host_name]['ip'])

    # connect switches
    for swname in topojson['switches']:
        adjsw = topojson['switches'][swname]
        for adjswname in adjsw:
            # links are bidirectional, error if added twice
            if adjswname not in link_exists[swname]:
                local_if = adjsw[adjswname]
                remote_if = topojson['switches'][adjswname][swname]
                net.addLink(swname, adjswname, port1=local_if, port2=remote_if)
                # mark both as created
                link_exists[swname][adjswname] = True
                link_exists[adjswname][swname] = True

     # connect hosts and transcoders to switches
    for host_name in topojson['hosts']:
         hostdata = topojson['hosts'][host_name]
         net.addLink(host_name, hostdata['switch'], port2=hostdata['port'])


    # add controller and start network
    net.addController(controller=RemoteController, port=6633)
    net.start()
    CLI(net)
    net.stop()

if __name__ == '__main__':
    net()
