
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

	filejson = open("topo/topo1.json")
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
	# print(tree_ports)


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

def swiches_conectados_directamente(dpid_origen, dpid_destino):
	estan_directamente_conectados = False
	for switch_aux in switches:
		if(switch_aux == dpid_origen):
			if (dpid_origen == sp[switch_aux][dpid_destino]):
				print "estan directamente conectado"
				estan_directamente_conectados = True
	return estan_directamente_conectados

def determinar_puerto_salida(dpid_origen, dpid_destino):
	puerto_salida = -1
	# Caso switches contiguos
	if(swiches_conectados_directamente(dpid_origen, dpid_destino)):
		puerto_salida = switches[dpid_origen][dpid_destino]
	# Caso mismo switch
	elif(sp[dpid_origen][dpid_destino] == None):
		print "Son el mismo switch"
	# Caso switches separados
	else:
		while (puerto_salida == -1):
			print "entre al while "
			nuevo_destino = sp[dpid_origen][dpid_destino]
			print "nuevo destino = "
			print nuevo_destino
			puerto_salida = determinar_puerto_salida(dpid_origen, nuevo_destino)
	print ("fin de la funcion. El puerto de salida es {}").format(puerto_salida)
	return puerto_salida

def inicializar_diccionario_switches:
	

load_json_topology()
shortest_paths_all()
tree_ports_all()
print('\n')
dump_sp()

print ("hola:")
determinar_puerto_salida("s8","s1")
