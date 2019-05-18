
import json

switches = {}	# switches
hosts = {}		# all hosts, including low-capacity hosts but not transcoders
dpids = {}		# datapath id for each switch
shortest_path = {}			#shortest paths
caminos_completos1 = {}
camino_entre_hosts1 = {}


def load_json_topology ():

	global switches
	global hosts
	global dpids

	filejson = open("../2-Topologias/json/3-topo_tree_3_ramas.json")
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
	global shortest_path

	for switch in switches:
		shortest_path[switch] = shortest_paths(switch)
	print "\t CAMINOS + CORTOS: \n"
	print(shortest_path)


# def dump_shortest_path():
# 	for switch in shortest_path:
# 		# print "shortest_path[%s]:" % (s, shortest_path[s])
# 		#print "shortest_path[%s]: %s " % (switch, shortest_path[switch])
# 	#print #newline

# Funcion que determina si un par de swiches
# estan conectados entre ellos o no
# Devuelve True si estan conectados o False
# en caso contrario.
def swiches_conectados_directamente(dpid_origen, dpid_destino):
	estan_directamente_conectados = False
	for switch_aux in switches:
		if(switch_aux == dpid_origen):
			if (dpid_origen == shortest_path[switch_aux][dpid_destino]):
				# print "estan directamente conectado"
				estan_directamente_conectados = True
			# elif (shortest_path[switch_aux][dpid_destino]==None):
			# 	estan_directamente_conectados = True
				# print "puse true porque eran el mismo switch"
	return estan_directamente_conectados

def switches_son_iguales(sw1, sw2):
	retorno = False
	if (sw1 == sw2):
		retorno = True
	else:
		retorno = False
	return retorno



# Funcion que determina el puerto por el cual se debe
# sacar el trafico si se quiere ir de un switch
# hacia otro.
# Devuelve el puerto del switch origen por el cual debe
# sacarse el trafico.
def determinar_puerto_salida(dpid_origen, dpid_destino):
	puerto_salida = -1
	# Caso switches contiguos
	if(swiches_conectados_directamente(dpid_origen, dpid_destino)):
		puerto_salida = switches[dpid_origen][dpid_destino]
	# Caso mismo switch
	elif(shortest_path[dpid_origen][dpid_destino] == None):
		print "Son el mismo switch"
	# Caso switches separados
	else:
		while (puerto_salida == -1):
			# print "entre al while "
			nuevo_destino = shortest_path[dpid_origen][dpid_destino]
			# print "nuevo destino = "
			# print nuevo_destino
			puerto_salida = determinar_puerto_salida(dpid_origen, nuevo_destino)
	# print ("fin de la funcion. El puerto de salida es {}").format(puerto_salida)
	return puerto_salida

# Funcion que carga un diccionario que resulta
# en una "matriz" que permite decidir que puerto
# utilizar como salida dependiendo el destino.
# Utiliza la funcion determinar_puerto_salida
def camino_entre_switches():
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

# Funcion que carga una matriz similar al de la funcion
# camino_por_puerto.
# Permite decidir que puerto utilizar (del switch del host origen)
# para llegar de un HOST origen hacia el HOST destino
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
				puertos_entre_hosts[host_aux_1][host_aux_2] = camino_entre_switches()[sw_host_aux_1][sw_host_aux_2]
	return puertos_entre_hosts


# Funcion que retorna un diccionario que muestra
# la lista de switches y puertos que debe atravesar
# un paquete dados un switch origen y un switch de destino
def caminos_completos():
	caminos_completos = {}

	#carga de la estructura vacia del diccionario
	for sw1 in switches:
		caminos_completos.setdefault(sw1,{})
		for sw2 in switches:
			caminos_completos[sw1].setdefault(sw2,{})
	#carga de switches a atravesar
	for sw1 in switches:
		for sw2 in switches:
			if (switches_son_iguales(sw1, sw2)):
				#Son el mismo switch
				caminos_completos[sw1][sw2].update({sw2:None})
			else:
				if(swiches_conectados_directamente(sw1, sw2)):
					# print ("Switch {} y {} estan conecta directamente".format(sw1,sw2))
					# el puerto de salida viene directamente de dijkstra
					puerto_aux=camino_entre_switches()[sw1][sw2]
					caminos_completos[sw1][sw2].update({sw1:puerto_aux})

				else:
					#determino el camino switch por switch iterando
					#print ("Switch {} y {} NO estan conectados directamente".format(sw1,sw2))
					#print ("Para conectar {} con {} el swich mas cercano al destino es {}".format(sw1, sw2, shortest_path[sw1][sw2]))

					# tomo nodo anterior mas cerano al destino
					nuevo_sw2=shortest_path[sw1][sw2]
					while(switches_son_iguales(sw1,nuevo_sw2)==False):
						puerto_aux=camino_entre_switches()[nuevo_sw2][sw2]
						caminos_completos[sw1][sw2].update({nuevo_sw2:puerto_aux})
						nuevo_sw2=shortest_path[sw1][nuevo_sw2]

					puerto_aux=camino_entre_switches()[nuevo_sw2][sw2]
					caminos_completos[sw1][sw2].update({nuevo_sw2:puerto_aux})

				# Se agrega paso final para agregar destino como valor
				# de la key de destino
				puerto_aux=camino_entre_switches()[sw1][sw2]
				caminos_completos[sw1][sw2].update({sw2:puerto_aux})

	#print caminos_completos
	return caminos_completos

def orden_caminos_completos():
	caminos_completos_ordenado = {}
	cami_compl = caminos_completos()
	dict_ord ={}
	dict_aux={}
	lista=[]
	switch_inicial="lucas"
	for sw_ori in cami_compl:
		for sw_dst in cami_compl:
			# Guardo destino del path
			lista.append(sw_dst)
			# Tomo penultimo salto para ese destino
			dst_aux = shortest_path[sw_ori][sw_dst]

			# Diccionario para ordenar
			dict_aux = cami_compl[sw_ori][sw_dst]

			for sw_dic in dict_aux:
				if(sw_dic == dst_aux):
					print"sw_dic y dst_aux me dieron igual"
					# Guardo valor del swich origen
					switch_inicial = dst_aux
				else:
					# Guardo penultimo salto
					lista.append(dst_aux)
			lista.append(switch_inicial)



				# print ("\tCAMINO desde {} hacia {}".format(sw_ori,sw_dst))
				# # Tomo el camino para ese path en particular
				# dict_aux = cami_compl[sw_ori][sw_dst]
				# print "dict aux !!!!!!!!!!!!!"
				# print dict_aux
				# for sw_aux in dict_aux:
				# 	print ("agarre {}".format(sw_aux))
				#
				# 	if(shortest_path[sw_ori][sw_aux]==None):
				# 		print "fue None - coincidieron los switches"
				# 		sw_inicio = sw_ori
				# 	else:
				# 		print("No dio none, dio {}".format(shortest_path[sw_ori][sw_aux]))
				# 		# almacenar para ordenar
				# 		# lista.append(shortest_path[sw_ori][sw_aux])
	print "\t\tlista :"
	print lista


	return caminos_completos_ordenado


def generar_json():

	filename = 'salida_topo.json'
	load_json_topology()
	shortest_paths_all()

	#shortest_path = {}			#shortest paths
	camino_entre_hosts1 = camino_entre_hosts()
	caminos_completos1 = caminos_completos()

	with open(filename, 'w') as fd:
	    fd.write(json.dumps([switches, hosts, dpids, camino_entre_hosts1, caminos_completos1]))    # both dicts in a list here

	#with open(filename, 'r') as fd:
	#    print(json.load(fd))


# LLAMADO A FUNCIONES:

generar_json()

print "\tcaminos completos"
orden_caminos_completos()
