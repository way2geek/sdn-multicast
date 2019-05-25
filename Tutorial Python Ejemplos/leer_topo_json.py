from mininet.net import Mininet
from mininet.cli import CLI
from mininet.node import OVSSwitch, RemoteController
import json
import sys

def net():
    net = Mininet()
    filejson = open(NOMBRE_TOPO_JSON)
    topojson = json.load(filejson)
    link_exists = {}

    for switch_name in topojson['switches']:
        net.addSwitch(switch_name, cls=OVSSwitch, protocols="OpenFlow13")
        link_exists[switch_name] = {}

    for host_name in topojson['hosts']:
        net.addHost(host_name, ip=topojson['hosts'][host_name]['ip'])

    #conexion entre switches
    for swname in topojson['switches']:
        adjsw = topojson['switches'][swname]
        for adjswname in adjsw:
            # control de error por si se agrego un enlace repetido
            if adjswname not in link_exists[swname]:
                local_if = adjsw[adjswname]
                remote_if = topojson['switches'][adjswname][swname]
                net.addLink(swname, adjswname, port1=local_if, port2=remote_if)
                # marcar como enlaces creados
                link_exists[swname][adjswname] = True
                link_exists[adjswname][swname] = True

     # conectar hosts a switches
    for host_name in topojson['hosts']:
         hostdata = topojson['hosts'][host_name]
         net.addLink(host_name, hostdata['switch'], port2=hostdata['port'])

    # add controller and start network
    net.addController(controller=RemoteController, port=6633)
    net.start()

    for aux in topojson['hosts']:
        host = net.get(aux)
        host.cmd('echo 2 > /proc/sys/net/ipv4/conf/{}-eth0/force_igmp_version'.format(aux))
        host.cmd('ip route add default via 10.0.0.250')

    for aux in topojson['switches']:
        switch = net.get(aux)
        switch.cmd('ovs-vsctl set Bridge {} protocols=OpenFlow13'.format(aux))

    CLI(net)
    net.stop()

if __name__ == '__main__':
    if(len(sys.argv)==2):
        NOMBRE_TOPO_JSON = sys.argv[1]
        print(NOMBRE_TOPO_JSON)
        net()
    else:
        print("ERROR: no se ingreso path para topologia.")
        print("Cerrando...")
