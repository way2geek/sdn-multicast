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


grupos = {
    1:{
        '225.0.0.1':{
                    'replied':True,
                    'leave':False,
                    'ports':{
                            3:{
                               'out':True,
                               'in':False
                              },
                            1:{
                               'out':True,
                               'in':False
                              }
                            }
                    }
       }
}


PRIORITY_MAX = 1000
PRIORITY_MID = 900
PRIORITY_LOW = 800
PRIORITY_MIN = 700

TABLE_MAC = 10

class Capa2(app_manager.RyuApp):

    def __init__(self, *args, **kwargs):
        super(Capa2, self).__init__(*args, **kwargs)
        self.mac_to_port = {}
        self.ip_to_port = {}
        self.gruposM = {
            1:{
                '225.0.0.1':{
                            'replied':True,
                            'leave':False,
                            'ports':{
                                    3:{
                                       'out':True,
                                       'in':False
                                      },
                                    1:{
                                       'out':True,
                                       'in':False
                                      }
                                    }
                            }
               }
        }

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


        #if eth.ethertype == ether_types.ETH_TYPE_IP:
        #        ip = pkt.get_protocol(ipv4.ipv4)
        #        srcip = ip.src
        #        dstip = ip.dst
        #        self.ip_to_port[dpid][srcip] = in_port
        #        print(self.ip_to_port)


        if self.esMulticast(destino):
            #self.multicast_tree.setdefault(destino, {})
            if eth.ethertype == ether_types.ETH_TYPE_IP:
                    ip = pkt.get_protocol(ipv4.ipv4)
                    srcip = ip.src
                    dstip = ip.dst
                    self.ip_to_port[dpid][srcip] = in_port
                    print(self.ip_to_port)
                    print('HAY TRAFICO MULTICAST')
                    self.manage_Multicast(datapath, in_port, origen, dstip)
            else:
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


    def add_group_flow(self, datapath, group_id, command, type, buckets):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        mod = parser.OFPGroupMod(datapath=datapath, group_id=group_id, command=command,
                                 type_=type, buckets=buckets)

        datapath.send_msg(mod)


    def manage_Multicast(self, datapath, in_port, origen, destino):

        dpid = datapath.id
        #print(self.gruposM)
        if destino in self.gruposM[dpid]:
            self.encaminoMulticast(datapath, destino, dpid)
        else:
            print('NO EXISTE ESE GRUPO MULTICAST {}'.format(destino))


    def encaminoMulticast(self, datapath, destino, dpid):

        puertos = self.getGroupPorts(destino, dpid)
        print('Los puertos del grupo multicast {} son: {}'.format(destino, puertos))

        'FALTA GENERAR BUCKETS PARA LA GROUP TABLE'
        
        return


    def getPorts(self, destino, dpid):
        'Se obtiene diccionario de puertos del switch'
        ports = {}
        puertosOut = []
        puertosIn = []

        for s_id, g_info in self.gruposM.items():
            if s_id == dpid:
                #print(dpid)
                for dst, d_info in g_info.items():
                    #print(dst)
                    if destino == dst:
                        #print('holaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa')
                        ports = d_info['ports']
                    else:
                        print('NO SE ENCUENTRA EL GRUPO REGISTRADO')
        return ports


    def getGroupPorts(self, destino, dpid):
        'Se obtienen los puertos de salida de un switch referidos a un grupo multicast'

        puertosOUT = []
        puertos = self.getPorts(destino, dpid)
        print(puertos)
        for puerto, p_info in puertos.items():
            if p_info['out'] == True:
                puertosOUT.append(puerto)
            #elif p_info['in'] ==True:
            #    puertosIN.append(puerto)
        return puertosOUT


    def dropPackage(self, datapath, priority, match, buffer_id=None):
        'Funcion para dropear trafico'
        parser = datapath.ofproto_parser

        msg = parser.OFPFlowMod(datapath=datapath,
                                priority=priority,
                                match=match,
                                instructions=[])
        datapath.send_msg(msg)


    def NotRequiredTraffic(self, datapath):
        'Se filtra trafico no deseado en la red'
        global PRIORITY_MAX

        #DROPS
        self.dropPackage(datapath, PRIORITY_MAX, self.match(datapath, eth_type=ether_types.ETH_TYPE_LLDP))
        #datapath.send_msg(msg)

        # Drop STDP BPDU
        self.dropPackage(datapath, PRIORITY_MAX, self.match(datapath, eth_dst='01:80:c2:00:00:00'))
        #datapath.send_msg(msg)
        self.dropPackage(datapath, PRIORITY_MAX, self.match(datapath, eth_dst='01:00:0c:cc:cc:cd'))
        #datapath.send_msg(msg)

        # Drop Broadcast Sources
        self.dropPackage(datapath, PRIORITY_MAX, self.match(datapath, eth_src='ff:ff:ff:ff:ff:ff'))
        #datapath.send_msg(msg)
        #msgs += self.dropPackage(dp, self.match(dp, eth_dst ='ff:ff:ff:ff:ff:ff'))

        self.dropPackage(datapath, PRIORITY_MAX, self.match(datapath, eth_type=ether_types.ETH_TYPE_IPV6))
        #datapath.send_msg(msg)