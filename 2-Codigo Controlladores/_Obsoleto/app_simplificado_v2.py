
import json

switches = {}	# switches
hosts = {}		# all hosts, including low-capacity hosts but not transcoders
dpids = {}		# datapath id for each switch
sp = {}			#shortest paths
ports = {}


def load_json_topology ():

	global switches
	global hosts
	global dpids

	filejson = open("../topologias/topoTree.json")
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
				# print "estan directamente conectado"
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
			# print "entre al while "
			nuevo_destino = sp[dpid_origen][dpid_destino]
			# print "nuevo destino = "
			# print nuevo_destino
			puerto_salida = determinar_puerto_salida(dpid_origen, nuevo_destino)
	# print ("fin de la funcion. El puerto de salida es {}").format(puerto_salida)
	return puerto_salida


def camino_por_puertos_switches():
	puertos_entre_switches = {}
	for sw_aux in switches:
		puertos_entre_switches.setdefault(sw_aux,{})
		for sw_aux2 in switches:
			if (sw_aux == sw_aux2):
					puertos_entre_switches[sw_aux][sw_aux2]=None
			else:
				puerto_dic = determinar_puerto_salida(sw_aux, sw_aux2)
				puertos_entre_switches[sw_aux][sw_aux2]=puerto_dic
	return puertos_entre_switches


def camino_entre_hosts ():
	puertos_entre_hosts = {}
	for host_aux_1 in hosts:
		puertos_entre_hosts.setdefault(host_aux_1,{})
		for host_aux_2 in hosts:
			sw_host_aux_1 = hosts[host_aux_1]["switch"]
			sw_host_aux_2 = hosts[host_aux_2]["switch"]
			#host conectados al mismo switch
			if (sw_host_aux_1 == sw_host_aux_2):
				#tomo valor textual del json
				puertos_entre_hosts[host_aux_1][host_aux_2] = hosts[host_aux_2]["port"]
			#host conectados a diferentes switches
			else:
				# tomo valor igual al puerto de conexion entre esos switches
				puertos_entre_hosts[host_aux_1][host_aux_2] = camino_por_puertos_switches()[sw_host_aux_1][sw_host_aux_2]
	return puertos_entre_hosts
