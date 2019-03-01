
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


    def esMulticast():
        pass


    def validoMulticast():
        pass


    def logger():
        pass


    
