
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
from ryu.lib.packet import igmp
from ryu.lib.packet import igmplib
from ryu.lib.igmplib import IgmpQuerier


class MulticastController(app_manager.RyuApp):

    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]
    _CONTEXTS = {'igmplib': igmplib.IgmpLib}


    def __init__(self, *args, **kwargs):
        super(MulticastController, self).__init__(*args, **kwargs)
        self._snoop = kwargs['igmplib']
        self._snoop.set_querier_mode(
            dpid=str_to_dpid('0000000000000001'), server_port=1)

        self.groups = IgmpQuerier()._mcast
        #groups = IgmpQuerier().mcast.copy()
        #self.subscribers = {} #ip_group -> subscriber -> [MODE (include = True, exclude = False) ip_sources]
        #self.ip_2_mac = {}


    def log(self, message):
        self.logger.info(message)
        return


    def validoMulticast(dp,msg,pkt):

        eth = pkt[0]
        dst = eth.dst
        if (eth.ethertype == ether_types.ETH_TYPE_IP and dst != 'ff:ff:ff:ff:ff:ff'):
            forwardMulticast(dp,msg,pkt)
        else:
            #SOLO SE PROCESAN PAQUETES IPV4 MULTICAST
            return


#    def forwardMulticast(self,dp,msg,pkt):
#        self.log('IVP4 Multicast Message')
#        ofproto = dp.ofproto
#        parser = dp.ofproto_parser
#        action_buckets = []
#        ip = pkt.get_protocol(ipv4.ipv4)
#        ipdst = ip.dst

#        if ipdst in self.groups:
#            for port in self.groups:
#                if [ipdst][port] == 'True':
#                    self.log('Encontro puerto de grupo multicast')
                    #action_buckets.append(parser.OFPActionOutput(port))
#                    pass#AGREGAR ACCION A ACTION BUCKET(DESTINO)




    def procesoOtros(dp,msg,pkt):
        pass


    #SE VERIFICA SI EL DESTINO ES MULTICAST COMPARANDO CON LA MAC MULTICAST
    def esMulticast(dst):
        return (dst[0:2] == '01' or dst[0:5] == '33:33' or dst == 'ff:ff:ff:ff:ff:ff')


    #Conocimiento de los switches conectados en la red
    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        dp = ev.msg.datapath
        ofp = dp.ofproto
        parser = dp.ofproto_parser

        #Se agrega miss table
        match = parser.OFPMatch()
        actions = [parser.OFPActionOutput(ofp.OFPP_CONTROLLER, ofp.OFPCML_NO_BUFFER)]
        instr = [parser.OFPInstructionActions(ofp.OFPIT_APPLY_ACTIONS, actions)]
        cmd = parser.OFPFlowMod(datapath=dp, priority=0, match=match, instructions=instr)
        dp.send_msg(cmd)


    #Recibe un paquete
    @set_ev_cls(igmplib.EventPacketIn, MAIN_DISPATCHER)
    def packet_in_handler(self, ev):
        msg = ev.msg
        dp = msg.datapath
        in_port = msg.match['in_port']

        pkt = packet.Packet(msg.data)
        eth = pkt.get_protocols(ethernet.ethernet)[0]
        ip = pkt.get_protocol(ipv4.ipv4)
        protocol = ip.proto

        self.log('Received ethernet packet')
        src = eth.src
        dst = eth.dst

        if esMulticast(dst):
            if protocol != in_proto.IPPROTO_IGMP:#and self.groups[dst][in_port]=='True':
                validoMulticast(dp,msg,pkt)
        else:
            procesoOtros(dp,msg,pkt)


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
