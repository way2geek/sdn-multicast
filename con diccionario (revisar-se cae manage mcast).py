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


PRIORITY_MAX = 1000
PRIORITY_MID = 900
PRIORITY_LOW = 800
PRIORITY_MIN = 700


class Capa2(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]
    # _CONTEXTS = {'igmplib': igmplib.IgmpLib}

    def __init__(self, *args, **kwargs):
        super(Capa2, self).__init__(*args, **kwargs)
        self.mac_to_port = {}
        self.ip_to_port = {}

        # 'DEFINO SWITCH DE LA TOPOLOGIA COMO QUERIER'
        # self._snoop = kwargs['igmplib']
        # self._snoop.set_querier_mode(
        #     dpid=str_to_dpid('0000000000000001'), server_port=2)

        self.gruposM = {
            1:{
              '225.0.0.1':{
                        'replied':True,
                        'leave':False,
                        'ports':{
                                3:{
                                   'out':False,
                                   'in':True
                                  },
                                1:{
                                   'out':False,
                                   'in':True
                                  }
                                }
                        },
              '225.0.0.2':{
                          'replied':True,
                          'leave':False,
                          'ports':{
                                  4:{
                                     'out':False,
                                     'in':True
                                    },
                                  }
                          }
               }
            }
        self.groupID = 1
        self.lista_grupos={}

        #carga y genera los group ID correspondientes para los gruposM
        #provenientes del diccionario
        for dpath_id_aux in self.gruposM:
            for grupo_existente in self.gruposM[dpath_id_aux]:
                #self.groupID = self.groupID + 1
                self.unir_direccion_grupo(grupo_existente)


    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        datapath = ev.msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        self.NotRequiredTraffic(datapath)

        match = parser.OFPMatch()
        actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER,
                                          ofproto.OFPCML_NO_BUFFER)]
        self.add_flow(datapath, PRIORITY_MIN, match, actions)

        'Agrego flujo a flow table para ir a grouptable'
        #self.add_group_flow(datapath, self.groupID, ofproto.OFPGC_ADD,
        #                    ofproto.OFPGT_ALL)
        #actions = [parser.OFPActionGroup(group_id=self.groupID),
        #           parser.OFPActionOutput(ofproto.OFPP_CONTROLLER, max_len=256)]
        #match = parser.OFPMatch(eth_type=ether_types.ETH_TYPE_IP,
        #                        ipv4_dst=('224.0.0.0', '240.0.0.0'))
        #self.add_flow(datapath, PRIORITY_MAX, match, actions)


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
        print(self.mac_to_port)

        if self.esMulticast(destino):
            print('HAY TRAFICO MULTICAST\n')
            if eth.ethertype == ether_types.ETH_TYPE_IP:
                    ip = pkt.get_protocol(ipv4.ipv4)
                    srcip = ip.src
                    dstip = ip.dst
                    self.ip_to_port[dpid][srcip] = in_port
                    print(self.ip_to_port)
                    self.manage_Multicast(datapath, in_port, origen, dstip)
            else:
                print('MULTICAST NO CAPA 3')
                return
        else:
            print('NO HAY TRAFICO MULTICAST')
            if destino in self.mac_to_port[dpid]:
                out_port = self.mac_to_port[dpid][destino]
            else:
                out_port = ofproto.OFPP_FLOOD

            actions = [parser.OFPActionOutput(out_port)]

            if out_port != ofproto.OFPP_FLOOD:
                match = self.match(datapath, in_port, destino, origen)
                #instructions = [self.apply_actions(datapath, actions)]

                if msg.buffer_id != ofproto.OFP_NO_BUFFER:
                    self.add_flow(datapath, PRIORITY_LOW, match, actions, msg.buffer_id)
                    return
                else:
                    self.add_flow(datapath, PRIORITY_LOW, match, actions)
                data = None
            if msg.buffer_id == ofproto.OFP_NO_BUFFER:
                data = msg.data

            out = parser.OFPPacketOut(datapath=datapath, buffer_id=msg.buffer_id,
                                              in_port=in_port, actions=actions, data=data)
            datapath.send_msg(out)



    def send_msgs(self, dp, msgs):
        "Send all the messages provided to the datapath"
        for msg in msgs:
            dp.send_msg(msg)


    def esMulticast(self, dst):
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


    def add_flow(self, datapath, priority, match, actions, buffer_id=None):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS,
                                             actions)]
        if buffer_id:
            mod = parser.OFPFlowMod(datapath=datapath, buffer_id=buffer_id,
                                    priority=priority, match=match,
                                    instructions=inst)
        else:
            mod = parser.OFPFlowMod(datapath=datapath, priority=priority,
                                    match=match, instructions=inst)
        datapath.send_msg(mod)


    def add_group_flow(self, datapath, group_id, command, type, buckets=None):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        if buckets:
            mod = parser.OFPGroupMod(datapath=datapath, command=command, type_=type,
                                     group_id=group_id ,buckets=buckets)
        else:
            mod = parser.OFPGroupMod(datapath=datapath, group_id=group_id, command=command,
                                     type_=type)

        datapath.send_msg(mod)


    def manage_Multicast(self, datapath, in_port, origen, destino):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        dpid = datapath.id
        destinoReg = []

        #### NUEVO
        #Se carga group table con group ID existente o
        #uno nuevo segun ya exista el grupo o no
        if destino in self.gruposM[dpid]:

            group_id = self.lista_grupos[destino]

            actions = [parser.OFPActionGroup(group_id=group_id)]

            print('EL ID DEL GRUPO DEL DESTINO {} ES'.format(self.lista_grupos[destino]))

            match = parser.OFPMatch(eth_type=ether_types.ETH_TYPE_IP,
                                    ipv4_dst=destino)

            self.add_flow(datapath, PRIORITY_MAX, match, actions)
            self.encaminoMulticast(datapath, destino, dpid)

        else:
            actions = [parser.OFPActionGroup(group_id=self.obtenerGroupID(destino))]
            match = parser.OFPMatch(eth_type=ether_types.ETH_TYPE_IP,
                                    ipv4_dst=destino)

            self.add_flow(datapath, PRIORITY_MAX, match, actions)
            self.encaminoMulticast(datapath, destino, dpid)
            print('NO EXISTE ESE GRUPO MULTICAST {}'.format(destino))

        ########

    def encaminoMulticast(self, datapath, destino, dpid):
        ofproto = datapath.ofproto

        puertos = self.getGroupOutPorts(destino, dpid)
        print('Los puertos del grupo multicast {} son: {}\n'.format(destino, puertos))

        bucketsOutput = self.generoBuckets(datapath, puertos)

        '*****AGREGAR CONDICION DE PUERTOS PARA NO VOLVER A AGREGAR GROUP TABLE*****'
        self.add_group_flow(datapath, self.lista_grupos[destino], ofproto.OFPGC_ADD, ofproto.OFPGT_ALL, bucketsOutput)


    def getPorts(self, destino, dpid):
        'Se obtiene diccionario de puertos del switch'
        ports = {}
        puertosOut = []
        puertosIn = []

        for s_id, g_info in self.gruposM.items():
            if s_id == dpid:
                for dst, d_info in g_info.items():
                    if destino == dst:
                        ports = d_info['ports']
                    #     print "pase por if ok"
        return ports


    def getGroupOutPorts(self, destino, dpid):
        'Se obtienen los puertos de salida de un switch referidos a un grupo multicast'
        puertosOUT = []
        puertos = self.getPorts(destino, dpid)

        for puerto, p_info in puertos.items():
            if p_info['in'] == True:
                puertosOUT.append(puerto)
            #elif p_info['in'] ==True:
              # puertosIN.append(puerto)
        return puertosOUT


    def generoBuckets(self, datapath, puertos):
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
        'Funcion para dropear trafico'
        parser = datapath.ofproto_parser

        msg = parser.OFPFlowMod(datapath=datapath,
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


### NUEVO
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
        print(self.lista_grupos)


    #funcion para eliminar las rutas para un grupo multicast
    #que ya no se utilice
    def eliminar_flow_mcast(self, ip_mcast):
        print "elimino grupo multicast"
        print (ip_mcast)
        self.quitar_direccion_grupo(ip_mcast)
        #TODO: agregar borrado de openflow


    def cargarGroupID(self):
        #carga y genera los group ID correspondientes para los gruposM
        #provenientes del diccionario
        for dpath_id_aux in self.gruposM:
            for grupo_existente in self.gruposM[dpath_id_aux]:
                self.unir_direccion_grupo(grupo_existente)


####FIN NUEVO
