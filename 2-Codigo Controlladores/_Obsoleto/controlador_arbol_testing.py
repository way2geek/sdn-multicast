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

PRIORITY_MAX = 1000
PRIORITY_MID = 900
PRIORITY_LOW = 800
PRIORITY_MIN = 700

TABLE_1 = 0
TABLE_2 = 10
TABLE_3 = 20

RUTA_TOPOLOGIA_JSON = "..//2-Topologias/json/2-topo_linear_grande.json"

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

        'Datos de control para el controlador'
        self.groupID = 0
        self.lista_grupos = {}

        'Datos de la topologia en la cual el controlador funciona'
        self.conexion_switches = {}
        self.conexion_hosts_switches = {}
        self.dpids = {}


    '####EVENTOS####'

    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        datapath = ev.msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        dpid = datapath.id

        self.obtenerRed()
        #self.obtenerConexiones(dpid)
        puertos_to_switches = self.get_ports_to_switches(dpid)

        print ('Los puertos conectados al switch {} son {}'.format(dpid, puertos_to_switches))

        if self.switch_acceso(dpid) == True:
            for port in puertos_to_switches:

                match = self.match(datapath)
                actions = [parser.OFPActionOutput(port)]
                instructions = [self.apply_actions(datapath, actions)]
                self.add_flow(datapath, TABLE_3, PRIORITY_LOW, match, instructions)

        self.default_flows(datapath, parser, ofproto)


    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def packet_in_handler(self, ev):
        "Handle incoming packets from a datapath"

        if ev.msg.msg_len < ev.msg.total_len:
            self.logger.debug("packet truncated: only %s of %s bytes",
                              ev.msg.msg_len, ev.msg.total_len)

        msg = ev.msg
        datapath = msg.datapath
        parser = datapath.ofproto_parser
        dpid = datapath.id
        puertos_to_switches = []

        # Parse the packet
        pkt = packet.Packet(msg.data)
        eth = pkt.get_protocols(ethernet.ethernet)[0]
        destino = eth.dst

    #    if self.esMulticast(destino):
    #        if eth.ethertype == ether_types.ETH_TYPE_IP:
    #                ip = pkt.get_protocol(ipv4.ipv4)
    #                srcip = ip.src
    #                dstip = ip.dst
    #                protocol = ip.proto

    #                if protocol != in_proto.IPPROTO_IGMP:
                        #print('NO ES IGMP')
    #    match = self.match(datapath)

        # if self.switch_acceso(dpid) == True:
        #     puertos_to_switches = self.get_ports_to_switches(dpid)
        #     for port in puertos_to_switches:
        #         actions = [parser.OFPActionOutput(port)]
        #         instructions = [self.apply_actions(datapath, actions)]
        #         self.add_flow(datapath, TABLE_3, PRIORITY_LOW, match, instructions)


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

        print('\n')
        print('Los grupos multicast son {}'.format(self.gruposM))
        print('\n')

        if ev.reason == igmplib.MG_GROUP_ADDED:

            group_id = self.gruposM[dpid][ev.address]['group_id']
            self.unir_direccion_grupo(ev.address, group_id, dpid)
            print('SE AGREGO EL GRUPO {}'.format(group_id))
            self.add_group_flow(ev.datapath, group_id, ofproto.OFPGC_ADD, ofproto.OFPGT_ALL)
            self.add_flow_to_group(ev.datapath, ev.address, group_id)

        elif ev.reason == igmplib.MG_MEMBER_CHANGED:

            group_id = self.lista_grupos[dpid][ev.address]
            puertos = self.getGroupOutPorts(ev.address, dpid)
            print('LOS PUERTOS DEL GRUPO {} EN EL SWITCH {} SON {}'.format(ev.address, dpid, puertos))
            buckets = self.generoBuckets(ev.datapath, puertos)
            self.add_group_flow(ev.datapath, group_id, ofproto.OFPGC_MODIFY, ofproto.OFPGT_ALL, buckets)
            print('SE MODIFICO EL GRUPO {} EN EL SWITCH {}'.format(group_id, dpid))

        elif ev.reason == igmplib.MG_GROUP_REMOVED:

            group_id = self.lista_grupos[dpid][ev.address]
            puertos = self.getGroupOutPorts(ev.address, dpid)
            buckets = self.generoBuckets(ev.datapath, puertos)
            self.add_group_flow(ev.datapath, group_id, ofproto.OFPGC_DELETE, ofproto.OFPGT_ALL, buckets)
            self.eliminar_flow_mcast(ev.datapath, TABLE_3, ev.address, group_id, dpid)



    '''####FUNCIONES####'''

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
        #instructions = [parser.OFPInstructionGotoTable(TABLE_3)]
        match = self.match(datapath, eth_type=ether_types.ETH_TYPE_IP,
                                ipv4_dst=('225.0.0.0', '240.0.0.0'))
        self.add_flow(datapath, TABLE_2, PRIORITY_MID, match, instructions)


    def add_flow(self, datapath, table_id, priority, match, instructions, buffer_id=None):
        'Se genera flujo en flow table'

        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        if buffer_id:
            mod = parser.OFPFlowMod(datagruposMpath=datapath, table_id=table_id,
                                    buffer_id=buffer_id,
                                    priority=priority, match=match,
                                    instructions=instructions)
        else:
            mod = parser.OFPFlowMod(datapath=datapath, table_id=table_id,
                                    priority=priority,
                                    match=match, instructions=instructions)
        datapath.send_msg(mod)


    def add_group_flow(self, datapath, group_id, command, type, buckets=None):
        'Se genera flujo en group table'

        ofproto = datapath.ofproto
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


    def getGroupPorts(self, destino, dpid):
        'Se obtiene diccionario de puertos del switch'

        ports = {}
        puertosOut = []
        puertosIn = []

        for s_id, g_info in self.gruposM.items():
            if s_id == dpid:
                for dst, d_info in g_info.items():
                    if destino == dst:
                        ports = d_info['ports']
        return ports


    def getGroupOutPorts(self, destino, dpid):
        'Se obtienen los puertos de salida de un switch referidos a un grupo multicast'

        puertosOUT = []
        puertos = self.getGroupPorts(destino, dpid)
        #print(puertos)
        for puerto in puertos:
            puertosOUT.append(puerto)

        return puertosOUT


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


    def quitar_direccion_grupo(self, ip_mcast, dpid):
        #Elimina del diccionario grupo multicast
        self.lista_grupos[dpid].pop(ip_mcast)


    def unir_direccion_grupo(self, ip_mcast, group_id, dpid):
    #   print "Agregue IP NUEVA:"
    #    print (ip_mcast)
        self.lista_grupos.setdefault(dpid, {})
        if ip_mcast not in self.lista_grupos[dpid]:
            self.lista_grupos[dpid].update({ip_mcast:group_id})


    #funcion para eliminar las rutas para un grupo multicast
    #que ya no se utilice
    def eliminar_flow_mcast(self, datapath, TABLE_ID, ip_mcast, group_id, dpid):

        print("Elimino grupo multicast {} del switch {}".format(group_id, dpid))
        print(self.lista_grupos)
        self.quitar_direccion_grupo(ip_mcast, dpid)
        print(self.lista_grupos)
        self.flowdel(datapath, TABLE_ID, ip_mcast, group_id)


    def obtenerRed(self):

        filejson = open(RUTA_TOPOLOGIA_JSON)
        topojson = json.load(filejson)

        self.conexion_switches = topojson['switches']
        self.conexion_hosts_switches = topojson['hosts']
        self.dpids = topojson['dpids']


    def get_ports_to_switches(self, dpid):

        aux = []
        for switch in self.conexion_switches:
            print('SWITCH: {}'.format(switch))

            if self.dpids.get(switch) == None:
                print('ERROR')
            else:
                if dpid == self.dpids[switch]:
                    aux = self.conexion_switches[switch].values()
        return aux


    def switch_acceso(self, dpid):
        retorno = False
        aux = []

        for switch in self.conexion_switches:
            print('VOY A TRABAJAR {}'.format(switch))
            if dpid == self.dpids[switch]:

                for host in self.conexion_hosts_switches:
                    if switch == self.conexion_hosts_switches[host]['switch']:
                        aux.append(host)

        if len(aux) > 0:
            print('EL SWITCH {} ES DE ACCESO Y SE ENCUENTRA CONECTADO A LOS HOSTS {}'.format(dpid, aux))
            retorno = True
        else:
            print('EL SWITCH {} NO ES DE ACCESO'.format(dpid))
            retorno = False

        return retorno
