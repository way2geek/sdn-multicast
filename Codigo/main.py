
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
from ryu.lib.igmplib import IgmpSnooper

#aplicacion de ruteo multicast
#es padre de la aplicacion igmp
class App(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        self.mac_to_port = {}
        self.groups = IgmpSnooper()._to_hosts.copy()



    def packet_in_handler():

        pass


    def ruteoMulticast():
        pass


    def ruteoOtros():
        pass


    #SE VERIFICA SI EL DESTINO ES MULTICAST COMPARANDO CON LA MAC MULTICAST
    def esMulticast(dst):
        return (dst[0:2] == '01' or dst[0:5] == '33:33' or dst == 'ff:ff:ff:ff:ff:ff')


    def validoMulticast(dp,msg,pkt):

        eth = pkt[0]
        dst = eth.dst
        if (eth.ethertype == ether_types.ETH_TYPE_IP and dst != 'ff:ff:ff:ff:ff:ff'):
            forwardMulticast(dp,msg,pkt)
        else:
            #SOLO SE PROCESAN PAQUETES IPV4 MULTICAST
            return


    def log(self, message):
        self.logger.info(message)
        return


    def set_flow_entry():
        pass


    def del_flow_entry():
        pass


    def groupTable(self, datapath):
        




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
