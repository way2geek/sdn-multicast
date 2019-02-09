
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


        self.groups = IgmpQuerier._mcast
        self.subscribers = {} #ip_group -> subscriber -> [MODE (include = True, exclude = False) ip_sources]
        self.ip_2_mac = {}


    #This function gets triggered before the topology controller flows are added
    #But late enough to be able to remove flows
    @set_ev_cls(ofp_event.EventOFPStateChange, [CONFIG_DISPATCHER])
    def state_change_handler(self, ev):
        dp = ev.datapath
        ofp = dp.ofproto
        parser = dp.ofproto_parser

        #Delete any possible currently existing flows.
        del_flows = parser.OFPFlowMod(dp, table_id=ofp.OFPTT_ALL, out_port=ofp.OFPP_ANY, out_group=ofp.OFPG_ANY, command=ofp.OFPFC_DELETE)
        dp.send_msg(del_flows)

        #Delete any possible currently existing groups
        del_groups = parser.OFPGroupMod(datapath=dp, command=ofp.OFPGC_DELETE, group_id=ofp.OFPG_ALL)
        dp.send_msg(del_groups)

        #Make sure deletion is finished using a barrier before additional flows are added
        barrier_req = parser.OFPBarrierRequest(dp)
        dp.send_msg(barrier_req)


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
    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def packet_in_handler(self, ev):
        msg = ev.msg
        dp = msg.datapath

        pkt = packet.Packet(msg.data)
        eth = pkt[0]

        self.log('Received ethernet packet')
        src = eth.src
        dst = eth.dst

        if eth.protocol_name != 'ethernet':
            #Se procesan los paquetes que no son multicast
            self.procesoOtros(dp,msg,pkt)
            return

        if

        if eth.ethertype == ether_types.ETH_TYPE_LLDP:
            return

        if esMulticast(dst):
            procesoMulticast(dp,msg,pkt)













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
