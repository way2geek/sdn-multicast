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
from ryu.lib import igmplib
from ryu.lib.dpid import str_to_dpid
from ryu.lib.packet import igmp


PRIORITY_MAX = 1000
PRIORITY_MID = 900
PRIORITY_LOW = 800
PRIORITY_MIN = 700

TABLE_1 = 0
TABLE_2 = 10
TABLE_3 = 20

GROUP_TABLE_1 = 50
GROUP_TABLE_2 = 51


class Capa2(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]
    _CONTEXTS = {'igmplib': igmplib.IgmpLib}

    def __init__(self, *args, **kwargs):
        super(Capa2, self).__init__(*args, **kwargs)
        self.mac_to_port = {}
        self.ip_to_port = {}

        'DEFINO SWITCH DE LA TOPOLOGIA COMO QUERIER'
        self._snoop = kwargs['igmplib']
        self._snoop.set_querier_mode(
            dpid=str_to_dpid('0000000000000002'), server_port=1)

        'Obtengo grupos multicast generados por el protocolo IGMP'
        self.gruposM = self._snoop._snooper._to_hosts

        self.groupID = 0
        self.lista_grupos={}


    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        datapath = ev.msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser


        self.default_flows(datapath, parser, ofproto)
        #TABLE_1
        #match = self.match(datapath)
        #instructions = [parser.OFPInstructionGotoTable(TABLE_2)]
        #self.add_flow(datapath, TABLE_1, PRIORITY_MIN, match, instructions)

        #TABLE_2
        #self.NotRequiredTraffic(datapath)
        #actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER, max_len=256)]
        #instructions = [self.apply_actions(datapath, actions)]
        #self.add_flow(datapath, TABLE_2, PRIORITY_MIN, match, instructions)

        #TABLE_3
        #match = self.match(datapath, eth_type=ether_types.ETH_TYPE_IP,
        #                        ipv4_dst=('224.0.0.0','240.0.0.0'))
        #actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER, max_len=256)]
        #instructions = [self.apply_actions(datapath, actions)]
        #self.add_flow(datapath, TABLE_3, PRIORITY_MAX, match, instructions)


    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def packet_in_handler(self, ev):
        "Handle incoming packets from a datapath"
        #msgs = []

        if ev.msg.msg_len < ev.msg.total_len:
            self.logger.debug("packet truncated: only %s of %s bytes",
                              ev.msg.msg_len, ev.msg.total_len)

        msg = ev.msg
        datapath = msg.datapath
        dpid = datapath.id
        in_port = ev.msg.match['in_port']
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        # Parse the packet
        pkt = packet.Packet(msg.data)
        eth = pkt.get_protocols(ethernet.ethernet)[0]
        destino = eth.dst
        origen = eth.src

        self.mac_to_port.setdefault(dpid, {})
        self.ip_to_port.setdefault(dpid, {})
        self.mac_to_port[dpid][origen] = in_port
        #print(self.mac_to_port)

        if self.esMulticast(destino):
            print('HAY TRAFICO MULTICAST')
            if eth.ethertype == ether_types.ETH_TYPE_IP:
                    ip = pkt.get_protocol(ipv4.ipv4)
                    srcip = ip.src
                    dstip = ip.dst
                    protocol = ip.proto
                    self.ip_to_port[dpid][srcip] = in_port
                    print(self.gruposM)

                    self.manage_Multicast(datapath, dstip)

            else:
                print('MULTICAST NO CAPA 3')
                return
        #else:
            #print('NO HAY TRAFICO MULTICAST')
            #if destino in self.mac_to_port[dpid]:
            #    out_port = self.mac_to_port[dpid][destino]
            #else:
            #    out_port = ofproto.OFPP_FLOOD

            #actions = [parser.OFPActionOutput(out_port)]
            #instructions = [self.apply_actions(datapath, actions)]

            #if out_port != ofproto.OFPP_FLOOD:
            #    match = self.match(datapath, in_port, destino, origen)
                #instructions = [self.apply_actions(datapath, actions)]

            #    if msg.buffer_id != ofproto.OFP_NO_BUFFER:
            #        self.add_flow(datapath, TABLE_2, PRIORITY_LOW, match, instructions, msg.buffer_id)
            #        return
            #    else:
            #        self.add_flow(datapath, TABLE_2, PRIORITY_LOW, match, instructions)
            #    data = None
            #if msg.buffer_id == ofproto.OFP_NO_BUFFER:
            #    data = msg.data

            #out = parser.OFPPacketOut(datapath=datapath, buffer_id=msg.buffer_id,
            #                                  in_port=in_port, actions=actions, data=data)
            #datapath.send_msg(out)


    @set_ev_cls(igmplib.EventMulticastGroupStateChanged,
                MAIN_DISPATCHER)
    def _status_changed(self, ev):
        msg = {
            igmplib.MG_GROUP_ADDED: 'Multicast Group Added',
            igmplib.MG_MEMBER_CHANGED: 'Multicast Group Member Changed',
            igmplib.MG_GROUP_REMOVED: 'Multicast Group Removed',
        }
        self.logger.info("%s: [%s] querier:[%s] hosts:%s",
                         msg.get(ev.reason), ev.address, ev.src,
                         ev.dsts)


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
        actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER, max_len=256)]
        instructions = [self.apply_actions(datapath, actions)]
        self.add_flow(datapath, TABLE_2, PRIORITY_MIN, match, instructions)


    def add_flow(self, datapath, table_id, priority, match, instructions, buffer_id=None):
        'Se genera flujo en flow table'

        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        if buffer_id:
            mod = parser.OFPFlowMod(datagruposMpath=datapath, table_id=table_id, buffer_id=buffer_id,
                                    priority=priority, match=match,
                                    instructions=instructions)
        else:
            mod = parser.OFPFlowMod(datapath=datapath, table_id=table_id, priority=priority,
                                    match=match, instructions=instructions)
        datapath.send_msg(mod)


    def add_group_flow(self, datapath, group_id, command, type, buckets=None):
        'Se genera flujo en group table'

        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        if buckets:
            mod = parser.OFPGroupMod(datapath=datapath, group_id=group_id, command=command,
                                 type_=type, buckets=buckets)
        else:
            mod = parser.OFPGroupMod(datapath=datapath, group_id=group_id, command=command,
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
        self.add_flow(datapath, TABLE_2, PRIORITY_MAX, match, instructions)


    def manage_Multicast(self, datapath, destino):
        'Se recibe paquete con destino multicast y se encamina. Se valida si es un grupo nuevo.'

        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        dpid = datapath.id
        existe = False
        print('GRUPOS MULTICAST {}'.format(self.gruposM))
        print('ID DE SWITCH: {}'.format(dpid))

        if (self.gruposM) and (destino in self.gruposM[dpid]):

            if destino in self.lista_grupos:
                existe = True
                group_id = self.lista_grupos[destino]
                print(group_id)
                self.encaminoMulticast(datapath, destino, dpid, group_id, existe)
                #self.add_flow_to_group(datapath, destino, group_id)
            else:
                self.obtenerGroupID(destino)
                group_id = self.lista_grupos[destino]
                print('grupo nuevo {}'.format(group_id))
                self.encaminoMulticast(datapath, destino, dpid, group_id, existe)
                self.add_flow_to_group(datapath, destino, group_id)

        else:

            print('NO SE ENCUENTRA REGISTRADO EL GRUPO')
            #self.eliminar_flow_mcast(destino)
            #FALTA HACER FUNCION PARA ELIMINAR GROUP TABLE
            #FALTA HACER FUNCION PARA ELIMINAR FLUJO

    def encaminoMulticast(self, datapath, destino, dpid, group_id, existe):
        '''Se obtienen los puertos de salida del switch segun grupo multicast registrado
        y se generan las acciones correspondientes'''

        ofproto = datapath.ofproto

        puertos = self.getGroupOutPorts(destino, dpid)
        print('Los puertos del grupo multicast {} en el switch {} son: {}'.format(destino, dpid, puertos))

        bucketsOutput = self.generoBuckets(datapath, puertos)

        if existe:
            self.add_group_flow(datapath, group_id, ofproto.OFPGC_MODIFY, ofproto.OFPGT_ALL, bucketsOutput)
        else:
            self.add_group_flow(datapath, group_id, ofproto.OFPGC_ADD, ofproto.OFPGT_ALL, bucketsOutput)


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

        # Drop STDP BPDU
        msgs.append(self.dropPackage(datapath, PRIORITY_MAX, self.match(datapath, eth_dst='01:80:c2:00:00:00')))
        msgs.append(self.dropPackage(datapath, PRIORITY_MAX, self.match(datapath, eth_dst='01:00:0c:cc:cc:cd')))

        # Drop Broadcast Sources
        msgs.append(self.dropPackage(datapath, PRIORITY_MAX, self.match(datapath, eth_src='ff:ff:ff:ff:ff:ff')))

        msgs.append(self.dropPackage(datapath, PRIORITY_MAX, self.match(datapath, eth_type=ether_types.ETH_TYPE_IPV6)))

        self.send_msgs(datapath, msgs)


    def obtenerGroupID(self, destino):
        print "group ID anterior: "
        print self.groupID
        #Cambiar valor de Group ID
        self.groupID = self.groupID + 1
        self.unir_direccion_grupo(destino)
        print "group ID nuevo: "
        print self.groupID
        return self.groupID

    def quitar_direccion_grupo(self, ip_mcast):
        #Elimina del diccionario grupo multicast
        print "saque IP:"
        print (ip_mcast)
        self.lista_grupos.pop(ip_mcast)

    def unir_direccion_grupo(self, ip_mcast):
        print "Agregue IP NUEVA:"
        print (ip_mcast)
        #Almacenar en diccionario relacion IP:group ID
        self.lista_grupos.update({ip_mcast:self.groupID})

    #funcion para eliminar las rutas para un grupo multicast
    #que ya no se utilice
    def eliminar_flow_mcast(self, ip_mcast):
        print "elimino grupo multicast"
        print (ip_mcast)
        self.quitar_direccion_grupo(ip_mcast)
        #TODO: agregar borrado de openflow
