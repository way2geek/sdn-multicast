
import sys
import os
from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER, DEAD_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.lib.packet import packet
from ryu.lib.packet import ethernet
from ryu.lib.packet import ether_types
from ryu.lib.packet import ipv4
from ryu.lib.packet import igmp
from ryu.lib.packet import lldp
import json
import time
import datetime
import app_crea_json

from ryu.topology import event
from ryu.topology.api import get_all_switch, get_all_link, get_switch, get_link
from ryu.lib import dpid as dpid_lib
from ryu.controller import dpset
import copy
from ryu.lib.dpid import dpid_to_str


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

        self.topo_shape = TopoStructure()

        'Datos de control para el controlador'
        self.groupID = 0
        self.lista_grupos = {}
        self.switches_por_gid = {}
        self.datapath_switch = {}

        'Datos de la topologia en la cual el controlador funciona'
        self.conexion_switches = {}
        self.conexion_hosts_switches = {}
        self.caminos_completos = {}
        self.dpids = {}

        self.leer_json('salida_topo.json')


    '####EVENTOS####'

    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        datapath = ev.msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        dpid = datapath.id

        self.obtener_datapath_switches(datapath)

        self.default_flows(datapath, parser, ofproto)

        self.topo_shape.switch_ports_state.setdefault(dpid, {})
        self.topo_shape.switch_ports_state[dpid].setdefault('puertos', {})
        self.obtener_puertos_switch(dpid)

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
        req_lldp = pkt.get_protocol(lldp.lldp)

        if not req_lldp:
            pktIPV4 = pkt.get_protocol(ipv4.ipv4)
            IPV4dst = pktIPV4.dst

        if req_igmp:

            if igmp.IGMP_TYPE_LEAVE == req_igmp.msgtype:
                'HAY QUE VER SI EL SWITCH ES DESTINO'
                'SI ES DESTINO TOMO IN PORT Y LO BORRO DE LA LISTA DE PUERTOS ASOCIADOS A ESE SWITCH DESTINO'
                'SI ES EL UNICO PUERTO ASOCIADO A ESE DESTINO BORRO EL DESTINO'
                if self.puerto_es_de_host(in_port, datapath)[0]:
                    self.manejo_leave(datapath, req_igmp.address, in_port)

            elif igmp.IGMP_TYPE_REPORT_V1 == req_igmp.msgtype or igmp.IGMP_TYPE_REPORT_V2 == req_igmp.msgtype:
                'HAY QUE VER SI EL IN PORT ES UN HOST Y SI PERTENECE A UN GRUPO'
                'SI EL GRUPO NO EXISTE SE CREA EL GRUPO'
                'SI EL GRUPO YA EXISTE SE MODIFICA EL GRUPO'
                if self.puerto_es_de_host(in_port, datapath)[0]:
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


    'Evento para reconocer cuando se agrega un switch con sus respectivos links a la topologia'
    @set_ev_cls(event.EventSwitchEnter)
    def handler_switch_enter(self, ev):
        self.topo_shape.topo_raw_switches = copy.copy(get_switch(self, None))
        self.topo_shape.topo_raw_links = copy.copy(get_link(self, None))
        for i,link in enumerate(self.topo_shape.topo_raw_links):
            self.topo_shape.links_info.setdefault(i, {})
            self.topo_shape.links_info[i].update({'switch_origen':link.src.dpid})
            self.topo_shape.links_info[i].update({'switch_destino':link.dst.dpid})
            self.topo_shape.links_info[i].update({'puerto_origen':link.src.port_no})
            self.topo_shape.links_info[i].update({'puerto_destino':link.dst.port_no})


    @set_ev_cls(ofp_event.EventOFPPortStatus, MAIN_DISPATCHER)
    def port_status_handler(self, ev):
        msg = ev.msg
        dp = msg.datapath
        ofp = dp.ofproto
        dpid_str = {'dpid': dpid_to_str(dp.id)}
        port = msg.desc
        reason = msg.reason
        dpid = dp.id

        if reason is dp.ofproto.OFPPR_ADD:
            self.logger.info('[port=%d] Port add.',
                             port.port_no, extra=dpid_str)

        elif reason is dp.ofproto.OFPPR_DELETE:
            self.logger.info('[port=%d] Port delete.',
                             port.port_no, extra=dpid_str)

        else:
            assert reason is dp.ofproto.OFPPR_MODIFY
            port_down = port.state & ofp.OFPPS_LINK_DOWN
            port_up = port.state & ofp.OFPPS_LIVE
            if port_down and self.topo_shape.switch_ports_state[dpid]['puertos'][port.port_no] == 'UP':
                estado_puertos = []
                lista_links = []
                print('PUERTO {} DEL SWITCH {} DOWN'.format(port.port_no, dpid))
                #print(self.topo_shape.switch_ports_state)
                'CADA VEZ QUE SE CAE UN PUERTO HAY QUE VERIFICAR EN LOS LINKS DE LA TOPOLOGIA, SI LOS PUERTOS QUE UNEN'
                'DOS SWITCHES ESTAN DOWN, SE DA DE BAJA EL PUERTO QUE CONECTA AMBOS SWITCHES Y SE INFORMA QUE EL LINK'
                'ESTA CAIDO. LUEGO SE RECALCULAN CAMINOS'

                link = self.topo_shape.obtener_link(dpid, port.port_no, self.topo_shape.topo_raw_links)
                print(link)
                if link is not None:
                    if link not in self.topo_shape.links_down:
                        self.topo_shape.links_down.append(link)
                        lista_links = self.topo_shape.recargar_links(link, port)
                        self.topo_shape.topo_raw_links = copy.copy(lista_links)
                        self.topo_shape.switch_ports_state[dpid]['puertos'][port.port_no] = 'DOWN'
                        #print(self.topo_shape.topo_raw_links)

                    estado_puertos = self.topo_shape.ambos_puertos_link_down(link)
                    if estado_puertos[0] == True and estado_puertos[1] == True:
                        print('LINK DOWN QUE UNE EL SWITCH {} CON EL SWITCH {} EN LOS PUERTOS {} {}'.format(link.src.dpid, link.dst.dpid,
                                                                                                            link.src.port_no, link.dst.port_no))
                        self.eliminar_conexion_entre_switches(link.src.dpid, link.dst.dpid, link.src.port_no, link.dst.port_no)
                        self.recalcular_caminos()
                else:
                    print('LINK ES NONETYPE')

            if self.topo_shape.switch_ports_state.get(dpid) != None:
                if port_up and self.topo_shape.switch_ports_state[dpid]['puertos'][port.port_no] == 'DOWN':
                    estado_puertos = []
                    lista_links_aux = []
                    lista_links = self.topo_shape.topo_raw_links

                    'HAY QUE VER SI SE LEVANTAN AMBOS PUERTOS QUE CORRESPONDEN A UN LINK DE LA TOPOLOGIA Y SETEAR'
                    'LOS PUERTOS CORRESPONDIENTES EN LA CONEXION ENTRE SWITCHES. LUEGO SE RECALCULAN CAMINOS'
                    #print(self.topo_shape.switch_ports_state)
                    print('PUERTO {} DEL SWITCH {} UP'.format(port.port_no, dpid))
                    link = self.topo_shape.obtener_link(dpid, port.port_no, self.topo_shape.links_down)
                    if link is not None:
                        if link in self.topo_shape.links_down:
                            lista_links_aux = self.topo_shape.agregar_link_up(link, port)
                            lista_links.extend(lista_links_aux)
                            self.topo_shape.topo_raw_links = copy.copy(lista_links)
                            self.topo_shape.links_down.remove(link)
                            self.topo_shape.switch_ports_state[dpid]['puertos'][port.port_no] = 'UP'

                        estado_puertos = self.topo_shape.ambos_puertos_link_down(link)
                        if estado_puertos[0] == False and estado_puertos[1] == False:
                            print('LINK UP QUE UNE EL SWITCH {} CON EL SWITCH {} EN LOS PUERTOS {} {}'.format(link.src.dpid, link.dst.dpid,
                                                                                                                link.src.port_no, link.dst.port_no))
                            self.agregar_conexion_entre_switches(link.src.dpid, link.dst.dpid, link.src.port_no, link.dst.port_no)
                            self.recalcular_caminos()
                    else:
                        print('LINK ES NONETYPE')


    '###########FUNCIONES###########'

    def obtener_puertos_switch(self, dpid):
        switch = self.obtener_nombre_switch(dpid)
        for switch_aux in self.conexion_switches[switch]:
            #print(self.conexion_switches[switch][switch_aux])
            self.topo_shape.switch_ports_state[dpid]['puertos'].update({self.conexion_switches[switch][switch_aux]:'UP'})
        #print(self.topo_shape.switch_ports_state)


    def eliminar_conexion_entre_switches(self, dpid_1, dpid_2, puerto_1, puerto_2):
        lista_group_id = []
        buckets = []
        switch_1 = self.obtener_nombre_switch(dpid_1)
        switch_2 = self.obtener_nombre_switch(dpid_2)
        self.conexion_switches[switch_1].pop(switch_2)
        self.conexion_switches[switch_2].pop(switch_1)
        #self.borrar_puertos_switch_groupID(dpid_1, puerto_1, dpid_2, puerto_2)
        self.limpio_camino_grupos()
        self.limpio_switches_por_groupID()


    def agregar_conexion_entre_switches(self, dpid_1, dpid_2, puerto_1, puerto_2):
        lista_group_id = []
        switch_1 = self.obtener_nombre_switch(dpid_1)
        switch_2 = self.obtener_nombre_switch(dpid_2)
        print('switch 1 : {}'.format(switch_1))
        print('switch 2 : {}'.format(switch_2))
        self.conexion_switches[switch_1].update({switch_2:puerto_1})
        self.conexion_switches[switch_2].update({switch_1:puerto_2})
        #self.borrar_puertos_switch_groupID(dpid_1, puerto_1, dpid_2, puerto_2)
        self.limpio_camino_grupos()
        self.limpio_switches_por_groupID()


    def recalcular_caminos(self):
        diccionario_nuevo = {}
        diccionario_nuevo.update({'switches':self.conexion_switches})
        diccionario_nuevo.update({'dpids':self.dpids})
        diccionario_nuevo.update({'hosts':self.conexion_hosts_switches})
        filename = 'topo_nueva.json'
        with open(filename, 'w') as fd:
    	    fd.write(json.dumps(diccionario_nuevo))
        fd.close()
        os.system('python app_crea_json.py topo_nueva.json')
        self.leer_json('salida_topo.json')
        self.actualizo_camino_grupos()
        

    def actualizo_camino_grupos(self):

        for group_id in self.lista_grupos.values():
            switch_origen = self.camino_grupos[group_id]['origen'].keys()[0]
            for switch_destino in self.camino_grupos[group_id]['switches_destino']:
                self.camino_grupos[group_id]['camino'][switch_destino] = self.caminos_completos[switch_origen][switch_destino]
                self.camino_grupos[group_id]['camino'][switch_destino][switch_destino] = self.camino_grupos[group_id]['switches_destino'][switch_destino]

                self.obtener_dic_arboles(self.camino_grupos)
                print('NUEVO SWITCHES POR GROUP ID {}'.format(self.switches_por_gid))

                for switch_camino in self.camino_grupos[group_id]['camino'][switch_destino]:
                    datapath = self.datapath_switch[switch_camino]['datapath']

                    if self.existe_flujo_group_table(switch_camino, group_id):

                        puertos_salida = self.switches_por_gid[group_id][switch_camino]
                        #print('switch {} puertos {}'.format(switch_camino, puertos_salida))
                        buckets = self.generoBuckets(datapath, puertos_salida)
                        #print(buckets)
                        self.add_group_flow(datapath, group_id, datapath.ofproto.OFPGC_ADD, datapath.ofproto.OFPGT_ALL)
                        #print('BORRE GRUPO {} EN SWITCH {}'.format(group_id, switch_camino))
                        self.add_group_flow(datapath, group_id, datapath.ofproto.OFPGC_MODIFY, datapath.ofproto.OFPGT_ALL, buckets)

                    else:
                        self.add_group_flow(datapath, group_id, datapath.ofproto.OFPGC_ADD, datapath.ofproto.OFPGT_ALL)
                        self.add_flow_to_group(datapath, IPV4dst, group_id)
                        self.datapath_switch[switch_camino]['cookies_grupos'].append(group_id)
                        print('SE AGREGO FLUJO AL GRUPO {} EN EL SWITCH {}'.format(group_id, datapath.id))


    def limpio_switches_por_groupID(self):
        for group_id in self.switches_por_gid:
            for switch in self.switches_por_gid[group_id]:
                self.switches_por_gid[group_id][switch] = []


    def limpio_camino_grupos(self):
        for group_id in self.camino_grupos:
            for switch_destino in self.camino_grupos[group_id]['camino']:
                for switch_camino in self.camino_grupos[group_id]['camino'][switch_destino]:
                    self.camino_grupos[group_id]['camino'][switch_destino] = []


    def borrar_puertos_switch_groupID(self, dpid_1, puerto_1, dpid_2, puerto_2):
        switch_a = self.obtener_nombre_switch(dpid_1)
        switch_b = self.obtener_nombre_switch(dpid_2)
        for group_id in self.switches_por_gid:
            switches = self.switches_por_gid[group_id].keys()
            if switch_a in switches:
                if puerto_1 in self.switches_por_gid[group_id][switch_a]:
                    self.switches_por_gid[group_id][switch_a].remove(puerto_1)
                    print('borre puerto {} del switch {}'.format(puerto_1, switch_a))
            if switch_b in switches:
                if puerto_2 in self.switches_por_gid[group_id][switch_b]:
                    self.switches_por_gid[group_id][switch_b].remove(puerto_2)
                    print('borre puerto {} del switch {}'.format(puerto_2, switch_b))
        print(self.switches_por_gid)


    def leer_json(self, filename_path):
        filejson = open(filename_path)
    	fp = json.load(filejson)

        self.conexion_switches = fp[0]
        self.conexion_hosts_switches = fp[1]
        self.dpids = fp[2]
        self.caminos_completos = fp[4]


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


    def agrego_grupo_multicast(self, datapath, dpid, address, ofproto):

        self.groupID = self.groupID + 1
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
                self.log_arbol_multicast(self.camino_grupos, "Grupo multicast creado?")

            else:
                if in_port not in self.camino_grupos[group_id]['switches_destino'][switch_destino]:
                    self.camino_grupos[group_id]['switches_destino'][switch_destino].append(in_port)
                    self.switches_por_gid[group_id][switch_destino].append(in_port)
                    self.log_arbol_multicast(self.camino_grupos, "Host agregado al grupo?")

        elif modo == 'leave':
            if len(self.camino_grupos[group_id]['switches_destino'][switch_destino]) > 0:
                self.camino_grupos[group_id]['switches_destino'][switch_destino].remove(in_port)
                print('El host conectado al puerto {} se fue del grupo {}'.format(in_port, group_id))
                self.log_arbol_multicast(self.camino_grupos, "Host abandono grupo multicast?")

            if len(self.camino_grupos[group_id]['switches_destino'][switch_destino]) == 0:
                self.camino_grupos[group_id]['switches_destino'].pop(switch_destino)
                print('Se elimino el switch destino {} del grupo {}'.format(switch_destino, group_id))
                self.log_arbol_multicast(self.camino_grupos, "Switch abandono grupo multicast?")

                if len(self.camino_grupos[group_id]['switches_destino'].keys()) == 0:
                    self.elimino_grupo_multicast(address, switch_destino, group_id)
                    print('Se elimino el grupo {}'.format(group_id))
                    self.log_arbol_multicast(self.camino_grupos, "Grupo multicast eliminado?")


    def elimino_grupo_multicast(self, address, switch_destino, group_id):

        for switch_camino in list(self.camino_grupos[group_id]['camino'][switch_destino]):

            datapath = self.datapath_switch[switch_camino]['datapath']
            self.add_group_flow(datapath, group_id, datapath.ofproto.OFPGC_DELETE, datapath.ofproto.OFPGT_ALL)
            self.eliminar_flow_mcast(datapath, TABLE_3, address, group_id, datapath.id)
            print('ELIMINE FLUJO DEL GRUPO {} EN EL SWITCH {}'.format(group_id, switch_camino))

        self.camino_grupos.pop(group_id)
        self.switches_por_gid.pop(group_id)
        self.lista_grupos.pop(address)


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


    # Funcion para cargar un diccionario que representa
    # los arboles segun cada grupo multicast
    def obtener_dic_arboles(self, dic_camino_grupos):
        listado_puertos=[]
        for g_id in dic_camino_grupos:
            # tomo switches involucrados en el g_id
            # incluye sw origen, sw destino
            for sw_dst in dic_camino_grupos[g_id]['camino']:
                for sw_camino in dic_camino_grupos[g_id]['camino'][sw_dst]:
                    #listado_puertos = self.diferencia_arrays(dic_camino_grupos[g_id]['camino'][sw_dst][sw_camino], self.switches_por_gid[g_id][sw_camino])
                    #if self.switches_por_gid[g_id].get(sw_camino) != None:
                    self.switches_por_gid[g_id][sw_camino].extend(dic_camino_grupos[g_id]['camino'][sw_dst][sw_camino])
                    #print(self.switches_por_gid)
                    self.switches_por_gid[g_id][sw_camino] = self.obtener_lista_sin_duplicados(self.switches_por_gid[g_id][sw_camino])
                    #print(self.switches_por_gid)


    def obtener_lista_sin_duplicados(self, una_lista):
        lista_depurada = []
        lista_repetidos = []
        indice_aux = 1
        depu_y_repe = []
        for elemento in una_lista:
            if(elemento in una_lista[indice_aux:len(una_lista)]):
                lista_repetidos.append(elemento)
            else:
                lista_depurada.append(elemento)
            indice_aux = indice_aux +1
        return lista_depurada


    def manejo_trafico_multicast(self, group_id, IPV4dst, switch_origen):
        #buckets = []
        for switch_destino in self.camino_grupos[group_id]['switches_destino']:

            self.camino_grupos[group_id]['camino'][switch_destino] = self.caminos_completos[switch_origen][switch_destino]
            self.camino_grupos[group_id]['camino'][switch_destino][switch_destino] = self.camino_grupos[group_id]['switches_destino'][switch_destino]


            self.log_arbol_multicast(self.camino_grupos, "que pasa aca?")

            for switch_camino in self.camino_grupos[group_id]['camino'][switch_destino]:
                datapath = self.datapath_switch[switch_camino]['datapath']

                if self.existe_flujo_group_table(switch_camino, group_id):
                    self.obtener_dic_arboles(self.camino_grupos)
                    puertos_salida = self.switches_por_gid[group_id][switch_camino]
                    #print('switch {} puertos {}'.format(switch_camino, puertos_salida))
                    'VER COMO HACER PARA QUE NO MODIFIQUE SIEMPRE LA GROUP TABLE'
                    #print('puertos del grupo {} en el switch {} {}'.format(group_id, switch_camino, self.switches_por_gid[group_id]))
                    #self.add_group_flow(datapath, group_id, datapath.ofproto.OFPGC_ADD, datapath.ofproto.OFPGT_ALL)
                    buckets = self.generoBuckets(datapath, puertos_salida)
                    #print(buckets)
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


    # Devuelve un array con los elementos
    #que estan en ar1 pero no estan en ar2
    def diferencia_arrays(self, ar1, ar2):
        result=[]
        result=list(set(ar1) - set(ar2))
        return result


    def existe_flujo_group_table(self, switch, group_id):
        retorno = False
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

            if(switch_aux == nom_sw):
                if (puerto_aux == un_puerto):
                    retorno[0] = True
                    retorno[1] = host_aux

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


    def add_flow(self, datapath, table_id, priority, match, instructions, idle_timeout = None, hard_timeout = None):
        'Se genera flujo en flow table'

        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        if idle_timeout != None and hard_timeout != None:
            mod = parser.OFPFlowMod(datapath=datapath, table_id=table_id,
                                    idle_timeout=idle_timeout,
                                    hard_timeout=hard_timeout,
                                    priority=priority,
                                    match=match, instructions=instructions)
        else:
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

        idle_timeout = 15
        hard_timeout = 300
        #print('AGREGO FLUJO A GROUP TABLE {}'.format(group_id))
        self.add_flow(datapath, TABLE_3, PRIORITY_MAX, match, instructions, idle_timeout, hard_timeout)


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
        self.lista_grupos.update({ip_mcast:group_id})


    #Funcion que elimina un grupo del diccionario de grupos multicast
    def quitar_direccion_grupo(self, ip_mcast, dpid):
        self.lista_grupos.pop(ip_mcast)


    #Funcion para eliminar las reglas usadas en un grupo multicast
    def eliminar_flow_mcast(self, datapath, TABLE_ID, ip_mcast, group_id, dpid):
        print("Elimino grupo multicast {} del switch {}".format(group_id, dpid))
        self.flowdel(datapath, TABLE_ID, ip_mcast, group_id)


    #Funcion que devuelve True si un switch contiene
    #al menos un host conectado
    def switch_es_de_acceso(self, dpid):
        retorno = False
        aux = []
        for switch in self.conexion_switches:
            if dpid == self.dpids[switch]:
                for host in self.conexion_hosts_switches:
                    if switch == self.conexion_hosts_switches[host]['switch']:
                        aux.append(host)
        if len(aux) > 0:
            retorno = True
        else:
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
    def log_arbol_multicast(self, diccionario_camino_grupos, accion_grupo):
        # Se crean archivos
        file_arboles_log = open("arboles_multicast.txt","a+")
        file_arboles_reciente = open("arboles_multicast.txt","w")
        # Se loguea tiempo
        ts=time.time()
        st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
        file_arboles_log.write("\nLog Time = "+st)
        file_arboles_reciente.write("\nLog Time = "+st)
        for grupo in diccionario_camino_grupos:
            ip_grupo = self.obtener_ip_grupo(grupo)
            # Se loguea IP del grupo Multicast
            file_arboles_log.write("\n\tIP GRUPO : "+str(ip_grupo))
            file_arboles_log.write("\n\tFue "+str(accion_grupo))
            file_arboles_reciente.write("\n\tIP GRUPO : "+str(ip_grupo))
            file_arboles_reciente.write("\n\tAccion: "+str(accion_grupo))
            
            if len(diccionario_camino_grupos[grupo]['origen'].keys()) > 0:
                s_ori = diccionario_camino_grupos[grupo]['origen'].keys()
                # Se loguea switch origen del arbol Multicast
                file_arboles_log.write("\n\t\tSwitch Origen : "+(str(s_ori)[3:5]))
                file_arboles_reciente.write("\n\t\tSwitch Origen : "+(str(s_ori)[3:5]))
            else:
                file_arboles_log.write("\n\t\tSwitch Origen : No definido")
                file_arboles_reciente.write("\n\t\tSwitch Origen : No definido")

            if len(diccionario_camino_grupos[grupo]['switches_destino'].keys()) > 0:
                for s_dst in diccionario_camino_grupos[grupo]['switches_destino']:
                    # Se loguea un switch destino de ese gruposwitch_origen
                    file_arboles_log.write("\n\t\t\tSwitch Destino : "+str(s_dst))
                    file_arboles_reciente.write("\n\t\t\tSwitch Destino : "+str(s_dst))
                    file_arboles_log.write("\n\t\t\t\tCamino de {} a {}:".format(s_ori ,s_dst))
                    file_arboles_reciente.write("\n\t\t\t\tCamino de {} a {}:".format(s_ori ,s_dst))

                    #Se loguea el camino para ese par Origen-destino
                    if  len(diccionario_camino_grupos[grupo]['camino'][s_dst].keys()) > 0:
                        for s_cami in diccionario_camino_grupos[grupo]['camino'][s_dst]:
                            puertos = diccionario_camino_grupos[grupo]['camino'][s_dst][s_cami]
                            text_sw_camino = "\n\t\t\t\t\tSwitch "+str(s_cami)+ " envia trafico por los siguientes puertos:"
                            puertos = str(puertos)
                            puertos = puertos.replace("["," ")
                            puertos = puertos.replace("]"," ")
                            text_sw_camino = text_sw_camino + puertos
                            file_arboles_log.write(text_sw_camino)
                            file_arboles_reciente.write(text_sw_camino)
            else:
                file_arboles_log.write("\n\t\t\tSwitch Destino : No definido")
                file_arboles_reciente.write("\n\t\t\tSwitch Destino : No definido")
                file_arboles_log.write("\n\t\t\t\tCamino: No definido")
                file_arboles_reciente.write("\n\t\t\t\tCamino: No definido")
        # Se cierran archivon de salida
        file_arboles_log.close()
        file_arboles_reciente.close()


    # Funcion quevuelve la IP del grupo Multicast
    # para cierto group ID
    def obtener_ip_grupo (self, un_group_id):
        ip_del_grupo = None
        for una_ip in self.lista_grupos:
            if (un_group_id == self.lista_grupos[una_ip]):
                ip_del_grupo = una_ip

        return ip_del_grupo


'CLASE QUE CONTIENE LOS DATOS DE LA TOPOLOGIA UTILIZADA'
class TopoStructure():
    def __init__(self, *args, **kwargs):
        self.topo_raw_switches = []
        self.topo_raw_links = []
        self.links_info = {}
        self.links_down = []
        self.switch_ports_state = {}

    def print_links(self, func_str=None):
        # Convert the raw link to list so that it is printed easily
        print(" \t" + str(func_str) + ": Current Links:")
        for l in self.topo_raw_links:
            print (" \t\t" + str(l))


    def print_switches(self, func_str=None):
        print(" \t" + str(func_str) + ": Current Switches:")
        for s in self.topo_raw_switches:
            print (" \t\t" + str(s))


    def ambos_puertos_link_down(self, link):
        puerto_o = link.src.port_no
        dpid_o = link.src.dpid
        puerto_d = link.dst.port_no
        dpid_d = link.dst.dpid

        list_aux = [False, False]

        for switch_dpid in self.switch_ports_state:
            if switch_dpid == dpid_o:
                if puerto_o in self.switch_ports_state[switch_dpid]['puertos']:
                    if self.switch_ports_state[switch_dpid]['puertos'][puerto_o] == 'DOWN':
                        list_aux[0] = True
            if switch_dpid == dpid_d:
                if puerto_d in self.switch_ports_state[switch_dpid]['puertos']:
                    if self.switch_ports_state[switch_dpid]['puertos'][puerto_d] == 'DOWN':
                        list_aux[1] = True
        return list_aux


    def recargar_links(self, link, port):
        tmp_list = []

        for link_aux in self.topo_raw_links:
            if link_aux.src.dpid == link.src.dpid and link_aux.src.port_no == port.port_no:
                pass
            elif link_aux.dst.dpid == link.dst.dpid and link_aux.dst.port_no == port.port_no:
                pass
            else:
                tmp_list.append(link_aux)

        return tmp_list


    def agregar_link_up(self, link, port):
        tmp_list = []
        for link_aux in self.links_down:
            if link_aux.src.dpid == link.src.dpid and link_aux.src.port_no == port.port_no:
                tmp_list.append(link_aux)
            elif link_aux.dst.dpid == link.dst.dpid and link_aux.dst.port_no == port.port_no:
                tmp_list.append(link_aux)
            else:
                pass

        return tmp_list


    def obtener_link(self, dpid, port, lista):
        retorno = None

        for link in lista:
            if link.src.dpid == dpid and link.src.port_no == port:
                retorno = link
            else:
                print('Switch {} puerto {}'.format(link.src.dpid, link.src.port_no))

        return retorno
