
import json

switches = {}	# switches
hosts = {}		# all hosts, including low-capacity hosts but not transcoders
dpids = {}		# datapath id for each switch
sp = {}			#shortest paths
sp_tree = {}	#short path tree'
ports = {}


def load_json_topology ():

	global switches
	global hosts
	global dpids

	filejson = open("/home/bruno/Escritorio/sdn-multicast-version2/2-Topologias/json/topoTree_profundo_todos_acceso.json")
	topojson = json.load(filejson)

	switches = topojson['switches']
	hosts = topojson['hosts']
	dpids = topojson['dpids']


def shortest_paths(origen):

	distancia = {}
	switch_anterior = {}

	switches_to_go = switches.keys()
	#print(switches_to_go)
	for node in switches_to_go:

		distancia[node] = float('inf')
		switch_anterior[node] = None

	distancia[origen] = 0

	while len(switches_to_go) > 0:

		switches_to_go.sort(key = lambda x: distancia[x])
		#print(switches_to_go)
		switch_mas_cercano = switches_to_go.pop(0)

		for switch_aux in switches[switch_mas_cercano]:
			if switch_aux in switches_to_go:
				aux = distancia[switch_mas_cercano] + 1
				if aux < distancia[switch_aux]:
					distancia[switch_aux] = aux
					switch_anterior[switch_aux] = switch_mas_cercano

	return switch_anterior


def build_sp_tree(source_host):
	tree_ports = {}
	done = set()
	source_switch = hosts[source_host]['switch']

	for destinated_host in hosts:

		if destinated_host != source_host:
			destinated_switch = hosts[destinated_host]['switch']
			current = destinated_switch
			parent = sp[source_switch][current]

			while parent is not None and current not in done:
				port = switches[parent][current]
				if parent not in tree_ports:
					tree_ports[parent] = set()
					print(tree_ports)
				tree_ports[parent].add(port)
				done.add(current)
				current = parent
				parent = sp[source_switch][current]

			if destinated_switch not in tree_ports:
				tree_ports[destinated_switch] = set()
			tree_ports[destinated_switch].add(hosts[destinated_host]['port'])
	print(tree_ports)


def tree_ports_all():
	for sh in hosts: # source host
		ports[sh] = build_sp_tree(sh)


def shortest_paths_all():
	global sp

	for switch in switches:
		sp[switch] = shortest_paths(switch)
	#print(sp)


def dump_sp():
	for switch in sp:
		# print "sp[%s]:" % (s, sp[s])
		print "sp[%s]: %s " % (switch, sp[switch])
	print #newline


load_json_topology()
shortest_paths_all()
tree_ports_all()
print('\n')
dump_sp()
