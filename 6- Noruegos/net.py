from mininet.net import Mininet
from mininet.cli import CLI
from mininet.node import OVSSwitch, RemoteController
import json


def net():

	net = Mininet()

	# read topology file
	filejson = open("topo/topo1.json")
	topojson = json.load(filejson)

	# create topology
	link_exists = {}

	for name in topojson['switches']:
		net.addSwitch(name, cls=OVSSwitch, protocols="OpenFlow13")
		link_exists[name] = {}

	for name in topojson['hosts']:
		net.addHost(name, ip=topojson['hosts'][name]['ip'])

	for name in topojson['tees']:
		net.addHost(name, ip=topojson['tees'][name]['ip'])

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
	for name in topojson['hosts']:
		hostdata = topojson['hosts'][name]
		net.addLink(name, hostdata['switch'], port2=hostdata['port'])

	for name in topojson['tees']:
		hostdata = topojson['tees'][name]
		net.addLink(name, hostdata['switch'], port2=hostdata['port'])

	# add controller and start network
	net.addController(controller=RemoteController, port=6633)
	net.start()

	# start CLI
	CLI(net)

	# done
	net.stop()


if __name__ == '__main__':
	net()
