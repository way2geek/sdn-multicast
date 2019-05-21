from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.lib.packet import packet
from ryu.lib.packet import ethernet
from ryu.lib.packet import ether_types
from ryu.lib.packet import ipv4
from ryu.lib.packet import igmp
import igmplib
import json
import time
import datetime


PRIORITY_MAX = 2000
PRIORITY_MID = 900
PRIORITY_LOW = 800
PRIORITY_MIN = 700

TABLE_1 = 0
TABLE_2 = 10
TABLE_3 = 20


class Controlador(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(Controlador, self).__init__(*args, **kwargs)

        self.camino_grupos = {}

        'Datos de control para el controlador'
        self.groupID = 0
        self.lista_grupos = {}
        self.datapath_switch = {}
        self.caminos_entre_hosts = {}
        self.caminos_completos = {}
        self.switches_por_gid = {}
        self.dic_buckets = {}

        'Datos de la topologia en la cual el controlador funciona'
        self.conexion_switches = {}
        self.conexion_hosts_switches = {}
        self.dpids = {}

        self.leer_json()


    '####EVENTOS####'

    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        datapath = ev.msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        dpid = datapath.id

        self.obtener_datapath_switches(datapath)

        self.default_flows(datapath, parser, ofproto)

        self.dic_buckets.setdefault(self.obtener_nombre_switch(datapath.id), [])


    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def packet_in_handler(self, ev):
        "Handle incoming packets from a datapath"

        if ev.msg.msg_len < ev.msg.total_len:
            self.logger.debug("packet truncated: only %s of %s bytes",
                              ev.msg.msg_len, ev.msg.total_len)

        msg = ev.msg
        datapath = msg.datapath
        parser = datapath.ofproto_parser
        in_port = msg.match['in_port']

        # Parse the packet
        pkt = packet.Packet(msg.data)
        eth = pkt.get_protocols(ethernet.ethernet)[0]
        destino = eth.dst
        req_igmp = pkt.get_protocol(igmp.igmp)

        pktIPV4 = pkt.get_protocol(ipv4.ipv4)
        IPV4dst = pktIPV4.dst

        if req_igmp:
            #print('FUE IGMP')
            if igmp.IGMP_TYPE_LEAVE == req_igmp.msgtype:
                #print('FUE UN LEAVE')
                'HAY QUE VER SI EL SWITCH ES DESTINO'
                'SI ES DESTINO TOMO IN PORT Y LO BORRO DE LA LISTA DE PUERTOS ASOCIADOS A ESE SWITCH DESTINO'
                'SI ES EL UNICO PUERTO ASOCIADO A ESE DESTINO BORRO EL DESTINO'
                if self.puerto_es_de_host(in_port, datapath)[0]:
                    #print('VINO UN LEAVE DEL HOST {} DEL SWITCH {} AL GRUPO {}'.format(self.puerto_es_de_host(in_port, datapath)[1], datapath.id, req_igmp.address))
                    self.manejo_leave(datapath, req_igmp.address, in_port)

            elif igmp.IGMP_TYPE_REPORT_V1 == req_igmp.msgtype or igmp.IGMP_TYPE_REPORT_V2 == req_igmp.msgtype:
                #print('FUE UN REPORT')
                'HAY QUE VER SI EL IN PORT ES UN HOST Y SI PERTENECE A UN GRUPO'
                'SI EL GRUPO NO EXISTE SE CREA EL GRUPO'
                'SI EL GRUPO YA EXISTE SE MODIFICA EL GRUPO'
                if self.puerto_es_de_host(in_port, datapath)[0]:
                    #print('VINO UN REPORT DEL HOST {} DEL SWITCH {} AL GRUPO {}'.format(self.puerto_es_de_host(in_port, datapath)[1], datapath.id, IPV4dst))
                    self.manejo_report(datapath, IPV4dst, in_port)
            else:
                print('NO SE SOPORTA IGMPv3')

        else:
            if self.esMulticast(destino):

                if self.es_origen(datapath, in_port):

                    switch_origen = self.obtener_nombre_switch(datapath.id)

                    if IPV4dst in self.lista_grupos:

                        group_id = self.lista_grupos[IPV4dst]

                        self.camino_grupos[group_id]['origen'].update({switch_origen:in_port})
                        self.manejo_trafico_multicast(group_id, IPV4dst, switch_origen)

                    else:
                        print('NO EXISTE EL GRUPO {}'.format(IPV4dst))


    '''####FUNCIONES####'''

    def leer_json(self):
        filejson = open("salida_topo.json")
    	fp = json.load(filejson)

        self.conexion_switches = fp[0]
        #print('conexion_switches {}'.format(self.conexion_switches))
        self.conexion_hosts_switches = fp[1]
        #print('conexion_hosts_switches {}'.format(self.conexion_hosts_switches))
        self.dpids = fp[2]
        #print('dpids {}'.format(self.dpids))
        self.caminos_entre_hosts = fp[3]
        #print('caminos_entre_hosts {}'.format(self.caminos_entre_hosts))
        self.caminos_completos = fp[4]
        #print('caminos_completos {}'.format(self.caminos_completos))


    def send_msgs(self, dp, msgs):
        "Send all the messages provided to the datapath"
        for msg in msgs:
            dp.send_msg(msg)


    def esMulticast(self, dst):
        'Valida si direccion MAC es multicast'
        return (dst[0:2] == '01' or dst[0:5] == '33:33')


    def match(self, dp, in_port=None, eth_dst=None, eth_src=None, eth_type=None,
                  ipv4_dst = None, **kwargs):
        "Generate an OFPMatch message"
        if in_port != None:
            kwargs['in_port'] = in_port
        if eth_dst != None:
            kwargs['eth_dst'] = eth_dst
        if eth_src != None:
            kwargs['eth_src'] = eth_src
        if eth_type != None:
            kwargs['eth_type'] = eth_type
        if ipv4_dst != None:
            kwargs['ipv4_dst'] = ipv4_dst
        return dp.ofproto_parser.OFPMatch(**kwargs)


    def apply_actions(self, dp, actions):
        "Generate an OFPInstructionActions message with OFPIT_APPLY_ACTIONS"

        return dp.ofproto_parser.OFPInstructionActions(
            dp.ofproto.OFPIT_APPLY_ACTIONS, actions)


    def action_output(self, dp, port, max_len=None):
        "Generate an OFPActionOutput message"

        kwargs = {'port': port}
        if max_len != None:
            kwargs['max_len'] = max_len

        return dp.ofproto_parser.OFPActionOutput(**kwargs)


    def agrego_grupo_multicast(self, datapath, dpid, address, ofproto):

        self.groupID = self.groupID + 1
        #group_id = self.groupID
        self.agregar_par_IP_groupID(address, self.groupID)
        self.camino_grupos.setdefault(self.groupID, {})
        self.camino_grupos[self.groupID].setdefault('switches_destino', {})
        self.camino_grupos[self.groupID].setdefault('camino', {})
        self.camino_grupos[self.groupID].setdefault('origen', {})
        self.switches_por_gid.setdefault(self.groupID, {})
        for switch in self.conexion_switches:
            self.switches_por_gid[self.groupID].setdefault(switch, [])


    def modifico_grupo_multicast(self, datapath, dpid, address, ofproto, in_port, modo):
        group_id = self.lista_grupos[address]
        switch_destino = self.obtener_nombre_switch(dpid)

        if modo == 'report':

            if switch_destino not in self.camino_grupos[group_id]['switches_destino']:
                self.camino_grupos[group_id]['switches_destino'].update({switch_destino:[]})
                self.camino_grupos[group_id]['camino'].setdefault(switch_destino, {})
                print('Se agrego el switch {} al grupo {}'.format(switch_destino, group_id))
                self.camino_grupos[group_id]['switches_destino'][switch_destino].append(in_port)
            else:
                if in_port not in self.camino_grupos[group_id]['switches_destino'][switch_destino]:
                    self.camino_grupos[group_id]['switches_destino'][switch_destino].append(in_port)
                    self.switches_por_gid[group_id][switch_destino].append(in_port)

        elif modo == 'leave':
            if len(self.camino_grupos[group_id]['switches_destino'][switch_destino]) > 0:
                self.camino_grupos[group_id]['switches_destino'][switch_destino].remove(in_port)
                print('EL host conectado al puerto {} se fue del grupo {}'.format(in_port, group_id))

            if len(self.camino_grupos[group_id]['switches_destino'][switch_destino]) == 0:
                self.camino_grupos[group_id]['switches_destino'].pop(switch_destino)
                print('Se elimino el switch destino {} del grupo {}'.format(switch_destino, group_id))

                if len(self.camino_grupos[group_id]['switches_destino'].keys()) == 0:
                    self.elimino_grupo_multicast(address, switch_destino, group_id)
                    print('Se elimino el grupo'.format(group_id))


    def elimino_grupo_multicast(self, address, switch_destino, group_id):

        for switch_camino in list(self.camino_grupos[group_id]['camino'][switch_destino]):

            datapath = self.datapath_switch[switch_camino]['datapath']
            self.add_group_flow(datapath, group_id, datapath.ofproto.OFPGC_DELETE, datapath.ofproto.OFPGT_ALL)
            self.eliminar_flow_mcast(datapath, TABLE_3, address, group_id, datapath.id)
            print('ELIMINE FLUJO DEL GRUPO {} EN EL SWITCH {}'.format(group_id, switch_camino))

        self.camino_grupos.pop(group_id)
        self.switches_por_gid.pop(group_id)
        self.lista_grupos.pop(address)
        # if address in self.lista_grupos:
        #     group_id = self.lista_grupos[address]
        #     switch_aux = self.obtener_nombre_switch(dpid)
        #
        #     if self.switch_es_de_acceso(dpid) and switch_aux in self.camino_grupos[group_id]['switches_destino']:
        #
        #         for switch_destino in list(self.camino_grupos[group_id]['switches_destino']):
        #             if switch_aux == switch_destino:
        #                 for switch_camino in list(self.camino_grupos[group_id]['camino'][switch_destino]):
        #
        #                     datapath = self.datapath_switch[switch_camino]['datapath']
        #                     self.add_group_flow(datapath, group_id, datapath.ofproto.OFPGC_DELETE, datapath.ofproto.OFPGT_ALL)
        #                     self.eliminar_flow_mcast(datapath, TABLE_3, address, group_id, datapath.id)
        #
        #                     self.camino_grupos[group_id]['camino'][switch_destino].pop(switch_camino)
        #
        #                 self.camino_grupos[group_id]['camino'].pop(switch_destino)
        #                 self.camino_grupos[group_id]['switches_destino'].pop(switch_destino)
        #             self.datapath_switch[switch_destino]['cookies_grupos'].remove(group_id)
        #         print('SE ELIMINO EL GRUPO {}'.format(group_id))
        #
        #     if len(self.camino_grupos[group_id]['switches_destino'].keys()) == 0:
        #         try:
        #             self.lista_grupos.pop(address)
        #             self.switches_por_gid.pop(group_id)
        #         except KeyError:
        #             print("Key not found")


    def manejo_leave(self, datapath, address, in_port):
        ofproto = datapath.ofproto
        dpid = datapath.id
        modo = 'leave'
        self.modifico_grupo_multicast(datapath, dpid, address, ofproto, in_port, modo)


    def manejo_report(self, datapath, address, in_port):
        ofproto = datapath.ofproto
        dpid = datapath.id
        modo = 'report'

        if address not in self.lista_grupos:
            self.agrego_grupo_multicast(datapath, dpid, address, ofproto)
            self.modifico_grupo_multicast(datapath, dpid, address, ofproto, in_port, modo)
        else:
            self.modifico_grupo_multicast(datapath, dpid, address, ofproto, in_port, modo)


    # Funcion para escribir diccionario que se utiliza
    # para escribir puertos de salida en cada switch
    # sin importar a que grupo pertenezca
    def obtener_dic_buckets(self, dic_arboles):
        for gid in dic_arboles:
            for sw in dic_arboles[gid]:
                self.dic_buckets[sw].extend(dic_arboles[gid][sw])


    # Funcion para cargar un diccionario que representa
    # los arboles segun cada grupo multicast
    def obtener_dic_arboles(self, dic_camino_grupos):
        listado_puertos=[]
        for g_id in dic_camino_grupos:
            # tomo switches involucrados en el g_id
            # incluye sw origen, sw destino
            for sw_dst in dic_camino_grupos[g_id]['camino']:
                for sw_camino in dic_camino_grupos[g_id]['camino'][sw_dst]:
                    listado_puertos = self.diferencia_arrays(dic_camino_grupos[g_id]['camino'][sw_dst][sw_camino], self.switches_por_gid[g_id][sw_camino])
                    self.switches_por_gid[g_id][sw_camino].extend(listado_puertos)


    def manejo_trafico_multicast(self, group_id, IPV4dst, switch_origen):

        for switch_destino in self.camino_grupos[group_id]['switches_destino']:

            self.camino_grupos[group_id]['camino'][switch_destino] = self.caminos_completos[switch_origen][switch_destino]
            self.camino_grupos[group_id]['camino'][switch_destino][switch_destino] = self.camino_grupos[group_id]['switches_destino'][switch_destino]

            self.obtener_dic_arboles(self.camino_grupos)

            for switch_camino in self.camino_grupos[group_id]['camino'][switch_destino]:
                datapath = self.datapath_switch[switch_camino]['datapath']

                if self.existe_flujo_group_table(switch_camino, group_id):

                    puertos_salida = self.switches_por_gid[group_id][switch_camino]
                    #print('LOS PUERTOS DE SALIDA DEL SWITCH DEL CAMINO {} HACIA EL DESTINO {} DEL GRUPO {} SON {}'.format(switch_camino, switch_destino, group_id, puertos_salida))
                    buckets =  self.generoBuckets(datapath, puertos_salida)
                    self.add_group_flow(datapath, group_id, datapath.ofproto.OFPGC_MODIFY, datapath.ofproto.OFPGT_ALL, buckets)

                else:
                    self.add_group_flow(datapath, group_id, datapath.ofproto.OFPGC_ADD, datapath.ofproto.OFPGT_ALL)
                    self.add_flow_to_group(datapath, IPV4dst, group_id)
                    self.datapath_switch[switch_camino]['cookies_grupos'].append(group_id)

                    print('SE AGREGO FLUJO AL GRUPO {} EN EL SWITCH {}'.format(group_id, datapath.id))


    def genero_puertos_salida(self, datapath, switch_origen, switch_camino, switch_destino, group_id):
        puertos_de_salida = []
        array_aux = []
        # Comparar switch camino con el destino porque si coincide con el destino,
        # solo se cargan los puertos hacia los hosts
        if switch_camino == switch_destino:
            puertos_de_salida.extend(self.camino_grupos[group_id]['switches_destino'][switch_destino])
        else:
            puertos_de_salida.extend(self.camino_grupos[group_id]['camino'][switch_destino][switch_camino])

        return puertos_de_salida


    #Compara 2 arrays y devuelve True si
    #son iguales o False si son diferentes
    #no importa el orden de los elementos
    def arrays_iguales(self, ar1, ar2):
        ret = False
        array_resta=list(set(ar1) - set(ar2))
        if(len(array_resta)==0):
            ret = True
        return ret


    # Devuelve un array con los elementos
    #que estan en ar1 pero no estan en ar2
    def diferencia_arrays(self, ar1, ar2):
        result=[]
        result=list(set(ar1) - set(ar2))
        return result


    def existe_flujo_group_table(self, switch, group_id):
        retorno = False
        #print('COOKIES_GRUPOS {}'.format(self.datapath_switch[switch]['cookies_grupos']))
        if group_id in self.datapath_switch[switch]['cookies_grupos']:
            retorno = True

        return retorno


    def es_origen(self, datapath, in_port):
        retorno = False
        switch_aux = self.obtener_nombre_switch(datapath.id)

        for host in self.conexion_hosts_switches:
            if self.conexion_hosts_switches[host]['switch'] == switch_aux:
                if self.conexion_hosts_switches[host]['port'] == in_port:
                    retorno = True

        return retorno


    #Funcion que recibe el datapath y un puerto de un switch
    #y devuelve True y el Host en particular que
    #esta en ese puerto de ese switch.
    def puerto_es_de_host(self, un_puerto, datapath):
        #es = False
        #host = None
        retorno = [False, None]
        nom_sw = self.obtener_nombre_switch(datapath.id)
        #Se recorre diccionario de topologia y si
        #matchea el switch y puerto con cierto
        #con cualquier hosta, devuelve True
        for host_aux in self.conexion_hosts_switches:
            puerto_aux = self.conexion_hosts_switches[host_aux]['port']
            switch_aux = self.conexion_hosts_switches[host_aux]['switch']

            #print ("AUX = {}".format(switch_aux))

            if(switch_aux == nom_sw):
                if (puerto_aux == un_puerto):
                    retorno[0] = True
                    retorno[1] = host_aux
                    print ("DEBUG: Host hallado {}".format(host_aux))
                else:
                    pass
                    #print ("DEBUG: Puerto {} no coincidio con argumento {}".format(puerto_aux,un_puerto))
            else:
                pass
                #print ("DEBUG: Switch {} no coincidio con argumento {}".format(switch_aux,nom_sw))
        return retorno


    #Funcion que recibe un switch y su lista de puertos
    #y devuelve una lista que contiene los puertos
    #donde hay conectados hosts.
    def obtener_puertos_de_hosts(self, dpid, puertos):
        retorno = False
        switch_aux = None
        puertos_aux = []
        switch_aux = self.obtener_nombre_switch(dpid)
        for host_aux in self.conexion_hosts_switches:
            #print(host_aux)
            if self.conexion_hosts_switches[host_aux]['switch'] == switch_aux:
                for puerto in puertos:
                    if self.conexion_hosts_switches[host_aux]['port'] == puerto:
                        puertos_aux.append(puerto)

        return retorno


    #Funcion que devuelve el nombre de un switch
    #en formato "sN" siendo N el numero de switch
    def obtener_nombre_switch(self, dpid):
        switch_aux = None
        for switch in self.dpids:
            if self.dpids[switch] == dpid:
                switch_aux = switch
        return switch_aux


    def default_flows(self, datapath, parser, ofproto):
        'Se crean e instalan flow tables y flujos por defecto'

        #TABLE_1
        match = self.match(datapath)
        instructions = [parser.OFPInstructionGotoTable(TABLE_2)]
        self.add_flow(datapath, TABLE_1, PRIORITY_MIN, match, instructions)

        #TABLE_2
        self.NotRequiredTraffic(datapath)
        actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER,
                                          ofproto.OFPCML_NO_BUFFER)]
        instructions = [parser.OFPInstructionGotoTable(TABLE_3),
                        self.apply_actions(datapath, actions)]

        match = self.match(datapath, eth_type=ether_types.ETH_TYPE_IP,
                                ipv4_dst=('224.0.0.0', '240.0.0.0'))
        self.add_flow(datapath, TABLE_2, PRIORITY_MID, match, instructions)


    def add_flow(self, datapath, table_id, priority, match, instructions, buffer_id=None):
        'Se genera flujo en flow table'

        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        mod = parser.OFPFlowMod(datapath=datapath, table_id=table_id,
                                priority=priority,
                                match=match, instructions=instructions)
        datapath.send_msg(mod)


    def add_group_flow(self, datapath, group_id, command, type, buckets=None):
        'Se genera flujo en group table'

        parser = datapath.ofproto_parser

        if buckets:
            mod = parser.OFPGroupMod(datapath=datapath, group_id=group_id,
                                     command=command,
                                     type_=type,
                                     buckets=buckets)
        else:
            mod = parser.OFPGroupMod(datapath=datapath, group_id=group_id,
                                     command=command,
                                     type_=type)
        datapath.send_msg(mod)


    def add_flow_to_group(self, datapath, destino, group_id):
        'Se genera flujo en flow table hacia la group table'

        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        match = parser.OFPMatch(eth_type=ether_types.ETH_TYPE_IP,
                                ipv4_dst=destino)
        actions = [parser.OFPActionGroup(group_id=group_id)]
        instructions = [self.apply_actions(datapath, actions)]

        print('AGREGO FLUJO A GROUP TABLE {}'.format(group_id))
        self.add_flow(datapath, TABLE_3, PRIORITY_MAX, match, instructions)


    def flowdel(self, datapath, table_id, destino, out_group, priority=None):
        "Generate an OFPFlowMod through flowmod with the OFPFC_DELETE command"
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        match = parser.OFPMatch(eth_type=ether_types.ETH_TYPE_IP,
                                ipv4_dst=destino)

        return parser.OFPFlowMod(datapath=datapath, table_id=table_id,
                            priority=priority,
                            command=ofproto.OFPFC_DELETE,
                            match=match,
                            out_group=out_group)


    def generoBuckets(self, datapath, puertos):
        'Se generan buckets de acciones para puertos de salida'

        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        actions = []
        buckets = []

        for outPort in puertos:

            accion = [parser.OFPActionOutput(outPort)]
            actions.append(accion)

        for action in actions:
            bucket = parser.OFPBucket(actions=action)
            buckets.append(bucket)

        return buckets


    def dropPackage(self, datapath, priority, match, buffer_id=None):
        'Funcion para dropear paquetes no requeridos'

        parser = datapath.ofproto_parser

        msg = parser.OFPFlowMod(datapath=datapath,
                                table_id=TABLE_2,
                                priority=priority,
                                match=match,
                                instructions=[])
        return msg


    def NotRequiredTraffic(self, datapath):
        'Se filtra trafico no deseado en la red'

        global PRIORITY_MAX
        msgs = []
        #DROPS
        msgs.append(self.dropPackage(datapath, PRIORITY_MAX, self.match(datapath, eth_type=ether_types.ETH_TYPE_LLDP)))
        # Drop STP BPDU
        msgs.append(self.dropPackage(datapath, PRIORITY_MAX, self.match(datapath, eth_dst='01:80:c2:00:00:00')))
        msgs.append(self.dropPackage(datapath, PRIORITY_MAX, self.match(datapath, eth_dst='01:00:0c:cc:cc:cd')))
        # Drop Broadcast Sources
        msgs.append(self.dropPackage(datapath, PRIORITY_MAX, self.match(datapath, eth_src='ff:ff:ff:ff:ff:ff')))
        msgs.append(self.dropPackage(datapath, PRIORITY_MAX, self.match(datapath, eth_type=ether_types.ETH_TYPE_IPV6)))
        self.send_msgs(datapath, msgs)


    #Funcion que agrega la pareja IP-Group ID
    #al diccionario lista_grupos
    def agregar_par_IP_groupID(self, ip_mcast, group_id):
        #self.lista_grupos.setdefault(dpid, {})
        self.lista_grupos.update({ip_mcast:group_id})


    #Funcion que elimina un grupo del diccionario de grupos multicast
    def quitar_direccion_grupo(self, ip_mcast, dpid):
        self.lista_grupos.pop(ip_mcast)


    #Funcion para eliminar las reglas usadas en un grupo multicast
    def eliminar_flow_mcast(self, datapath, TABLE_ID, ip_mcast, group_id, dpid):
        print("Elimino grupo multicast {} del switch {}".format(group_id, dpid))
        #print(self.lista_grupos)
        #self.quitar_direccion_grupo(ip_mcast, dpid)
        #print(self.lista_grupos)
        self.flowdel(datapath, TABLE_ID, ip_mcast, group_id)


    #Funcion que devuelve True si un switch contiene
    #al menos un host conectado
    def switch_es_de_acceso(self, dpid):
        retorno = False
        aux = []
        for switch in self.conexion_switches:
            #print('VOY A TRABAJAR {}'.format(switch))
            if dpid == self.dpids[switch]:
                for host in self.conexion_hosts_switches:
                    if switch == self.conexion_hosts_switches[host]['switch']:
                        aux.append(host)
        if len(aux) > 0:
            #print('EL SWITCH {} ES DE ACCESO Y SE ENCUENTRA CONECTADO A LOS HOSTS {}'.format(dpid, aux))
            retorno = True
        else:
            #print('EL SWITCH {} NO ES DE ACCESO'.format(dpid))
            retorno = False
        return retorno


    def obtener_datapath_switches(self, datapath):
        switch = self.obtener_nombre_switch(datapath.id)
        self.datapath_switch.setdefault(switch, {})
        self.datapath_switch[switch].update({'datapath':datapath, 'id':datapath.id, 'cookies_grupos':[]})


    # Funcion para escribir estado de "arboles" multicast
    # en archivo de texto con el historico.
    # Permite ver los cambios dentro de los grupos a cada
    # momento
    def loggear_arbol_multicast(self, diccionario_camino_grupos):
        # Se crea archivo
        file_arboles = open("arboles_multicast.txt","a+")
        # Se loguea tiempo
        ts=time.time()
        st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
        file_arboles.write("\nLog Time = "+st)

        for grupo in diccionario_camino_grupos:
            ip_grupo = self.obterner_ip_grupo (grupo)
            # Se loguea IP del grupo Multicast
            file_arboles.write("\n\tIP GRUPO : "+str(ip_grupo))
            s_ori = diccionario_camino_grupos[grupo]['origen'].keys()
            # Se loguea switch origen del arbol Multicast
            file_arboles.write("\n\t\tSwitch Origen : "+(str(s_ori)[3:5]))

            for s_dst in diccionario_camino_grupos[grupo]['switches_destino']:
                # Se loguea un switch destino de ese gruposwitch_origen
                file_arboles.write("\n\t\t\tSwitch Destino : "+str(s_dst))
                file_arboles.write("\n\t\t\t\tCamino:")

                #Se loguea el camino para ese par Origen-destino
                for s_cami in diccionario_camino_grupos[grupo]['camino']:
                    puertos = diccionario_camino_grupos[grupo]['camino'][s_dst][s_cami].values()
                    text_sw_camino = "\n\t\t\t\t\tSwitch "+str(s_cami)+ " envia trafico por puerto/s"
                    puertos = str(puertos)
                    puertos = puertos.replace("["," ")
                    puertos = puertos.replace("]"," ")
                    text_sw_camino = text_sw_camino + puertos
                    file_arboles.write(text_sw_camino)
        # Se cierra archivo de salida
        file_arboles.close()

    # Funcion quevuelve la IP del grupo Multicast
    # para cierto group ID
    def obterner_ip_grupo (self, un_group_id):
        ip_del_grupo = -1
        for una_ip in self.lista_grupos:
            if (un_group_id == self.lista_grupos[una_ip]):
                ip_del_grupo = una_ip
            else:
                print "No se encontro IP del grupo"
                # pass
        return ip_del_grupo
