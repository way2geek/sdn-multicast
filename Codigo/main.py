
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
from .aux import AuxApp
from . import host_cache

#aplicacion de ruteo multicast
class App(app_manager.RyuApp, AuxApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(App, self).__init__(*args, **kwargs)
        self.mac_to_port = {}
        self.groups = IgmpSnooper()._to_hosts.copy()


    #se instalan las flow tables y group tables en los witches al conocerlos
    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        "Handle new datapaths attaching to Ryu"
        dp = ev.msg.datapath
        ofp = dp.ofproto
        parser = dp.ofproto_parser

        msgs = self.add_datapath(ev.msg.datapath)

        self.send_msgs(ev.msg.datapath)


    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def packet_in_handler():
        dp = ev.msg.datapath
        in_port = ev.msg.match['in_port']

        # Parse the packet
        pkt = packet.Packet(ev.msg.data)
        eth = pkt.get_protocols(ethernet.ethernet)[0]
        # Ensure this host was not recently learned to avoid flooding the switch
        # with the learning messages if the learning was already in process.
        if not self.host_cache.is_new_host(dp.id, in_port, eth.src):
            return




    def add_datapath(datapaht):
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


    def set_flow_entry():
        pass


    def del_flow_entry():
        pass


    #borrar los flujos en grouptables y flowtables de todos los switches
    def clean_all_flows(dp):
        pass
