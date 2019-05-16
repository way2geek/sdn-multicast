from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.lib.packet import packet
from ryu.lib.packet import ethernet
from ryu.lib.packet import ether_types
from ryu.lib.packet import ipv4
from ryu.lib.packet import in_proto
from ryu.lib.dpid import str_to_dpid
from ryu.lib.packet import igmp
import igmplib
import json


PRIORITY_MAX = 2000
PRIORITY_MID = 900
PRIORITY_LOW = 800
PRIORITY_MIN = 700

TABLE_1 = 0
TABLE_2 = 10
TABLE_3 = 20

cookie_group_table = 0x55200000


class Controlador(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]
    _CONTEXTS = {'igmplib': igmplib.IgmpLib}

    def __init__(self, *args, **kwargs):
        super(Controlador, self).__init__(*args, **kwargs)

        'DEFINO SWITCH DE LA TOPOLOGIA COMO QUERIER'
        self._snoop = kwargs['igmplib']
        self._snoop.set_querier_mode(
            dpid=str_to_dpid('0000000000000001'), server_port=1)

        'Obtengo grupos multicast generados por el protocolo IGMP'
        self.gruposM = self._snoop._snooper._to_hosts

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

        if not req_igmp:

            if self.esMulticast(destino):

                if self.es_origen(datapath, in_port):

                    switch_origen = self.obtener_nombre_switch(datapath.id)

                    if IPV4dst in self.lista_grupos:

                        group_id = self.lista_grupos[IPV4dst]

                        #self.camino_grupos[group_id].setdefault('origen', {})
                        self.camino_grupos[group_id]['origen'].update({switch_origen:in_port})

                        self.manejo_trafico_multicast(group_id, IPV4dst, switch_origen)

                    else:
                        pass
                        #print('NO EXISTE EL GRUPO {}'.format(IPV4dst))


    @set_ev_cls(igmplib.EventMulticastGroupStateChanged, MAIN_DISPATCHER)
    def _status_changed(self, ev):
        ofproto = ev.datapath.ofproto
        dpid = ev.datapath.id

        msg = {
            igmplib.MG_GROUP_ADDED: 'Multicast Group Added',
            igmplib.MG_MEMBER_CHANGED: 'Multicast Group Member Changed',
            igmplib.MG_GROUP_REMOVED: 'Multicast Group Removed',
        }

        self.logger.info("%s: [%s] querier:[%s] hosts:%s switch:%s group_id:%s",
                         msg.get(ev.reason), ev.address, ev.src,
                         ev.dsts, dpid, ev.group_id)

        if ev.reason == igmplib.MG_GROUP_ADDED and ev.address not in self.lista_grupos:

            self.agrego_grupo_multicast(ev.datapath, dpid, ev.address, ofproto)

        elif ev.reason == igmplib.MG_MEMBER_CHANGED:

            self.modifico_grupo_multicast(ev.datapath, dpid, ev.address, ofproto, ev.dsts)

        elif ev.reason == igmplib.MG_GROUP_REMOVED:

            self.elimino_grupo_multicast(ev.datapath, dpid, ev.address, ofproto)



    '''####FUNCIONES####'''

    def leer_json(self):
        filejson = open("test.json")
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


    def agrego_grupo_multicast(self, datapath, dpid, address, ofproto):

        self.groupID = self.groupID + 1
        self.unir_direccion_grupo(address, self.groupID)

        self.camino_grupos.setdefault(self.groupID, {})
        self.camino_grupos[self.groupID].setdefault('origen', {})
        self.camino_grupos[self.groupID].setdefault('switches_destino', {})
        self.camino_grupos[self.groupID].setdefault('camino', {})
        self.switches_por_gid.setdefault(self.groupID, {})

        for switch in self.conexion_switches:
            self.switches_por_gid[self.groupID].setdefault(switch, [])


    #Para que el update no afecte en el leave:
    def funcion (self, variable_nueva):
        if(variable_nueva == "agregar"):
            pass
            # codigo que ya estaba tal cual con UPDATE
        elif (variable_nueva == "eliminar"):
            # llamar funcion "elimno_miembro()"
            # usar pop()
            pass
        else:
            pass


    # Para saber si se vacio "destinos" de un grupo multicast
    def grupo_esta_vacio(self, un_dic, un_group_id):
        esta_vacio = False
        # observa el largo de la lista de switches destino
        # en caso de que no haya switches destino, significa
        # que el grupo esta vacio
        if (len(list(un_dic[un_group_id]["switches_destino"].keys()))==0):
            esta_vacio = True
        return esta_vacio

    def modifico_grupo_multicast(self, datapath, dpid, address, ofproto, dsts):

        group_id = self.lista_grupos[address]
        switch_destino = self.obtener_nombre_switch(dpid)
        puertos_host = self.puerto_es_de_host(dpid, dsts)

        if (len(puertos_host) > 0):
            print('ES UN HOST DESTINO EN EL SWITCH {}'.format(dpid))

            if switch_destino not in self.camino_grupos[group_id]['switches_destino']:
                # agrega switch en diccionario para el caso en que no exista
                self.camino_grupos[group_id]['camino'].setdefault(switch_destino, {})
                self.camino_grupos[group_id]['switches_destino'].update({switch_destino:[]})

            self.camino_grupos[group_id]['switches_destino'][switch_destino] = puertos_host

            if (len(puertos_host) < len((self.camino_grupos[group_id]['switches_destino'][switch_destino]))):
                # caso para eliminar miembro

                print " --- vinieron menos hosts desde igmplib"
                #eliminar_miembro(group_id,)

            elif(len(puertos_host) == len((self.camino_grupos[group_id]['switches_destino'][switch_destino]))):
                # caso para dejar como esta o chequear que los miembros uno a uno sean los mismos
                print " --- vino misma cantidad de hosts desde igmplib"

            else:
                print "vinieron mas hosts desde igmp"
                # caso para agregar miembro

            print('SE MODIFICO EL GRUPO {} SU CAMINO ES {}'.format(group_id, self.camino_grupos))

        elif len(puertos_host) == 0 and switch_destino in self.camino_grupos[group_id]['switches_destino']:
            #se borra switch destino
            self.camino_grupos[group_id]['switches_destino'].pop(switch_destino)
            print('SE ELIMINO EL SWITCH DESTINO {} DEL GRUPO {}'.format(switch_destino, group_id))
            # dic.pop(key[,default])


    def elimino_grupo_multicast(self, datapath, dpid, address, ofproto):
        #ELIMINO EL GRUPO MULTICAST Y LOS FLUJOS CORRESPONDIENTES EN TODOS LOS SWITCHES INTEGRANTES DEL MISMO.
        group_id = self.lista_grupos[address]
        switch_aux = self.obtener_nombre_switch(dpid)

        if switch_aux in self.camino_grupos[group_id]['switches_destino']:
            #self.camino_grupos[group_id]['switches_destino'].pop(switch_aux)

            if self.grupo_esta_vacio(self.camino_grupos, group_id) == True:

                for switch_destino in self.camino_grupos[group_id]['camino']:
                    for switch_camino in list(self.camino_grupos[group_id]['camino'][switch_destino]):

                        datapath1 = self.datapath_switch[switch_camino]['datapath']
                        self.add_group_flow(datapath1, group_id, datapath1.ofproto.OFPGC_DELETE, datapath1.ofproto.OFPGT_ALL)
                        self.camino_grupos[group_id]['camino'][switch_aux].pop(switch_camino)
                        self.eliminar_flow_mcast(datapath1, TABLE_3, address, group_id, dpid)

                #self.camino_grupos[group_id]['camino'].pop(switch_aux)
                self.switches_por_gid.pop(group_id)
                print('SE BORRO EL GRUPO {}'.format(group_id))
                self.lista_grupos.pop(address)


    # Funcion para escribir diccionario que se utiliza
    # para escribir puertos de salida en cada switch
    # sin importar a que grupo pertenezca
    # def obtener_dic_buckets(self, dic_arboles):
    #     for gid in dic_arboles:
    #         for sw in dic_arboles[gid]:
    #             self.dic_buckets[sw].extend(dic_arboles[gid][sw])


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
                    #dic_camino_grupos[g_id]['camino'][sw_dst][sw_camino].extend(listado_puertos)
                    self.switches_por_gid[g_id][sw_camino].extend(listado_puertos)
                    #print(self.switches_por_gid)


    def manejo_trafico_multicast(self, group_id, IPV4dst, switch_origen):

        for switch_destino in self.camino_grupos[group_id]['switches_destino']:

            self.camino_grupos[group_id]['camino'][switch_destino] = self.caminos_completos[switch_origen][switch_destino]
            self.camino_grupos[group_id]['camino'][switch_destino][switch_destino] = self.camino_grupos[group_id]['switches_destino'][switch_destino]
            #print('EL CAMINO DEL GRUPO {} ES {}'.format(group_id, self.camino_grupos))
            #print('Los switches del camino de origen {} y destino {} son {}'.format(switch_origen, switch_destino, self.camino_grupos[group_id]['camino'][switch_destino]))
            self.obtener_dic_arboles(self.camino_grupos)

            for switch_camino in self.camino_grupos[group_id]['camino'][switch_destino]:
                datapath = self.datapath_switch[switch_camino]['datapath']

                if self.existe_flujo_group_table(switch_camino, group_id):

                    puertos_salida = self.switches_por_gid[group_id][switch_camino]

                    #print('LOS PUERTOS DE SALIDA DEL SWITCH DEL CAMINO {} HACIA EL DESTINO {} DEL GRUPO {} SON {}'.format(switch_camino, switch_destino, group_id, puertos_salida))
                    buckets =  self.generoBuckets(datapath, puertos_salida)
                    self.add_group_flow(datapath, group_id, datapath.ofproto.OFPGC_MODIFY, datapath.ofproto.OFPGT_ALL, buckets)

                else:
                    #self.puertos_salida_switches_camino[group_id].setdefault(switch_destino, {})
                    self.add_group_flow(datapath, group_id, datapath.ofproto.OFPGC_ADD, datapath.ofproto.OFPGT_ALL)
                    self.add_flow_to_group(datapath, IPV4dst, group_id)
                    self.datapath_switch[switch_camino]['cookies_grupos'].append(group_id)

                    print('SE AGREGO FLUJO AL GRUPO {} EN EL SWITCH {}'.format(group_id, datapath.id))


    # def genero_puertos_salida(self, datapath, switch_origen, switch_camino, switch_destino, group_id):
    #     puertos_de_salida = []
    #     array_aux = []
    #     # Comparar switch camino con el destino porque si coincide con el destino,
    #     # solo se cargan los puertos hacia los hosts
    #     if switch_camino == switch_destino:
    #         puertos_de_salida.extend(self.camino_grupos[group_id]['switches_destino'][switch_destino])
    #     else:
    #         puertos_de_salida.extend(self.camino_grupos[group_id]['camino'][switch_destino][switch_camino])
    #
    #     return puertos_de_salida


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


    def puerto_es_de_host(self, dpid, puertos):

        switch_aux = None
        puertos_aux = []

        switch_aux = self.obtener_nombre_switch(dpid)

        for host_aux in self.conexion_hosts_switches:
            #print(host_aux)
            if self.conexion_hosts_switches[host_aux]['switch'] == switch_aux:
                for puerto in puertos:
                    if self.conexion_hosts_switches[host_aux]['port'] == puerto:
                        puertos_aux.append(puerto)

        return puertos_aux


    def obtener_nombre_switch(self, dpid):
        switch_aux = None

        for switch in self.dpids:
            if self.dpids[switch] == dpid:
                switch_aux = switch

        return switch_aux


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


    def quitar_direccion_grupo(self, ip_mcast, dpid):
        #Elimina del diccionario grupo multicast
        self.lista_grupos.pop(ip_mcast)


    def unir_direccion_grupo(self, ip_mcast, group_id):

        #self.lista_grupos.setdefault(dpid, {})
        self.lista_grupos.update({ip_mcast:group_id})


    #funcion para eliminar las rutas para un grupo multicast
    #que ya no se utilice
    def eliminar_flow_mcast(self, datapath, TABLE_ID, ip_mcast, group_id, dpid):

        print("Elimino grupo multicast {} del switch {}".format(group_id, datapath.id))
        self.flowdel(datapath, TABLE_ID, ip_mcast, group_id)


    def switch_acceso(self, dpid):
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
