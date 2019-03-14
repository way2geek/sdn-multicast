
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
import logging

PRIORITY_MAX = 1000
PRIORITY_MID = 900
PRIORITY_LOW = 800
PRIORITY_MIN = 700

TABLE_ACL = 0
TABLE_FILTER = 10
TABLE_SRC = 11
TABLE_DST = 12

GROUP_TABLE_1 = 100
GROUP_TABLE_2 = 101


class PruebaRuteo(app_manager.RyuApp):

    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(PruebaRuteo, self).__init__(*args, **kwargs)
        #self.groups =


    #se instalan las flow tables y group tables en los witches al conocerlos
    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        "Handle new datapaths attaching to Ryu"
        dp = ev.msg.datapath
        ofp = dp.ofproto

        msgs = self.add_datapath(dp)

        self.send_msgs(dp, msgs)


    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def packet_in_handler(self, ev):
        "Handle incoming packets from a datapath"
        #msgs = []
        dp = ev.msg.datapath
        dpid = dp.id
        in_port = ev.msg.match['in_port']

        # Parse the packet
        pkt = packet.Packet(ev.msg.data)
        eth = pkt.get_protocols(ethernet.ethernet)[0]


        msgs = self.learn_source(
            dp=dp,
            port=in_port,
            eth_src=eth.src)

        self.send_msgs(dp, msgs)


    def add_datapath(self, dp):
        #msgs = []
        msgs = self.clean_all_flows(dp)
        msgs += self.add_default_flows(dp)
        return msgs

    def add_default_flows(self, dp):
        global TABLE_ACL
        global TABLE_FILTER
        global TABLE_SRC
        global TABLE_DST
        global PRIORITY_MAX
        global PRIORITY_MID
        global PRIORITY_LOW
        global PRIORITY_MIN

        ofp = dp.ofproto

        msgs = []
        ### TABLE_ACL ###
        # Add a low priority table-miss flow to forward to the switch table.
        # Other modules can add higher priority flows as needed.
        instructions = [self.goto_table(dp, TABLE_FILTER)]
        msgs += [self.flowmod(dp, TABLE_ACL,
                              match=self.match(dp),
                              priority=PRIORITY_LOW,
                              instructions=instructions)]


        ### TABLE_FILTER ###
        msgs += self.dropPackage(dp, self.match(dp, ipv4_dst = '192.168.1.13'))

        # Drop LLDP
        msgs += self.dropPackage(dp, self.match(dp, eth_type=ether_types.ETH_TYPE_LLDP))

        # Drop STDP BPDU
        msgs += self.dropPackage(dp, self.match(dp, eth_dst='01:80:c2:00:00:00'))
        msgs += self.dropPackage(dp, self.match(dp, eth_dst='01:00:0c:cc:cc:cd'))

        # Drop Broadcast Sources
        msgs += self.dropPackage(dp, self.match(dp, eth_src='ff:ff:ff:ff:ff:ff'))

        # All other packets go to table TABLE_ETH_SRC
        match = self.match(dp)
        instructions = [self.goto_table(dp, TABLE_SRC)]
        msgs += [self.flowmod(dp, TABLE_FILTER,
                              match=match,
                              priority=PRIORITY_MIN,
                              instructions=instructions)]


        ### TABLE_SRC ###
        # Table-miss sends to controller and sends to TABLE_ETH_DST
        # We send to TABLE_ETH_DST because the SRC rules will hard timeout
        # before the DST rules idle timeout. This gives a last chance to
        # prevent a flood event while the controller relearns the address.
        actions = [self.action_output(dp, ofp.OFPP_CONTROLLER, max_len=256)]
        instructions = [self.apply_actions(dp, actions),
                        self.goto_table(dp, TABLE_DST)]
        msgs += [self.flowmod(dp, TABLE_SRC,
                              match=match,
                              priority=PRIORITY_MIN,
                              instructions=instructions)]

        ###TABLE_DST ###
        "ENVIO TRAFICO MULTICAST A GROUP TABLE"
        eth = packet.get_protocols(ethernet.ethernet)[0]
        if self.esMulticast(eth.dst):
            msgs += [self.groupMod(dp,GROUP_TABLE_1)]
            actions = [self.action_output(dp, ofp.OFPP_CONTROLLER, max_len=256),
                       parser.OFPActionGroup(group_id=GROUP_TABLE_1)]
            match = self.match(dp)
            instructions = [self.apply_actions(dp, actions)]
            msgs += [self.flowmod(dp, TABLE_DST,
                                  match = match,
                                  priority = PRIORITY_MAX,
                                  instructions = instructions)]

        # Table-miss floods
        match = self.match(dp)
        actions = [self.action_output(dp, ofp.OFPP_FLOOD)]
        instructions = [self.apply_actions(dp, actions)]
        msgs += [self.flowmod(dp, TABLE_DST,
                              match=match,
                              priority=PRIORITY_MIN,
                              instructions=instructions)]

        return msgs


    def add_eth_src_flow(self, dp, in_port, eth_src):
        "Add flow to mark the source learned at a specific port"

        match = self.match(dp, eth_src=eth_src, in_port=in_port)
        instructions = [self.goto_table(dp, TABLE_DST)]
        return [self.flowmod(dp, TABLE_SRC,
                             hard_timeout=0,
                             match=match,
                             instructions=instructions,
                             priority=PRIORITY_MID)]


    def add_eth_dst_flow(self, dp, out_port, eth_dst):
        "Add flow to forward packet sent to eth_dst to out_port"

        match = self.match(dp, eth_dst=eth_dst)
        actions = [self.action_output(dp, out_port)]
        instructions = [self.apply_actions(dp, actions)]
        return [self.flowmod(dp, TABLE_DST,
                             idle_timeout=0,
                             match=match,
                             instructions=instructions,
                             priority=PRIORITY_MID)]


    def send_group_mode(self, dp):

        ofproto = dp.ofproto
        buckets = []
        ports = []
        ports = self.getGroupPorts(dp)
        bucket = self.setActionsBuckets(dp, ports)
        buckets.append(bucket)

        return [self.groupMod(dp, GROUP_TABLE_1,
                              type = ofproto.OFPGT_ALL,
                              buckets = buckets)]

    """SE DEBERIA MANDARLE COMO PARAMETRO EL DESTINO PARA VERIFICAR SI ES MULTICAST
       Y REALIZAR EL LLAMADA A LA FUNCION send_group_mode"""
    def learn_source(self, dp, port, eth_src):
        "Learn the port associated with the source MAC"
        #msgs = []
        msgs = self.unlearn_source(dp, eth_src=eth_src)
        msgs += self.add_eth_src_flow(dp, in_port=port, eth_src=eth_src)
        msgs += self.add_eth_dst_flow(dp, out_port=port, eth_dst=eth_src)
        return msgs


    def unlearn_source(self, dp, eth_src):
        "Remove any existing flow entries for this MAC address"
        global TABLE_SRC
        global TABLE_DST

        msgs = [self.flowdel(dp, TABLE_SRC,
                             match=self.match(dp, eth_src=eth_src))]
        msgs += [self.flowdel(dp, TABLE_DST,
                              match=self.match(dp, eth_dst=eth_src))]
        msgs += [self.barrier_request(dp)]
        return msgs


#-----------------------------------------------------------------------------#
    """FUNCIONES AUXILIARES"""

    def send_msgs(self, dp, msgs):
        "Send all the messages provided to the datapath"
        for msg in msgs:
            dp.send_msg(msg)


    def goto_table(self, dp, table_id):
        "Generate an OFPInstructionGotoTable message"

        return dp.ofproto_parser.OFPInstructionGotoTable(table_id)


    def action_output(self, dp, port, max_len=None):
        "Generate an OFPActionOutput message"

        kwargs = {'port': port}
        if max_len != None:
            kwargs['max_len'] = max_len

        return dp.ofproto_parser.OFPActionOutput(**kwargs)


    def apply_actions(self, dp, actions):
        "Generate an OFPInstructionActions message with OFPIT_APPLY_ACTIONS"

        return dp.ofproto_parser.OFPInstructionActions(
            dp.ofproto.OFPIT_APPLY_ACTIONS, actions)


    def setActionsBuckets(self, dp, ports):
        pass


    def getGroupPorts(self, dp):
        pass


    def groupMod(self, dp, group_id, command=None, type = None, buckets = None):

        mod_kwargs = {
            'datapath': dp,
            'group_id': group_id,
            'command': command or dp.ofproto.OFPGC_ADD,
            #'cookie': self.config.group_cookie
        }
        if type != None:
            mod_kwargs['type'] = type
        if buckets != None:
            mod_kwargs['buckets'] = buckets

        return dp.ofproto_parser.OFPGroupMod(**mod_kwargs)


    def flowmod(self, dp, table_id, command=None, idle_timeout=None,
                hard_timeout=None, priority=None, buffer_id=None,
                out_port=None, out_group=None, flags=None, match=None,
                instructions=None):
        "Generate an OFPFlowMod message with the cookie already specified"

        mod_kwargs = {
            'datapath': dp,
            'table_id': table_id,
            'command': command or dp.ofproto.OFPFC_ADD,
            'cookie': 0x55200000
        }
        # Selectively add kwargs so ofproto defaults will be used otherwise.
        # Not using **kwargs in method defintion so arguments can be easy to
        # parse for static analysis (autocompletion)
        if idle_timeout != None:
            mod_kwargs['idle_timeout'] = idle_timeout
        if hard_timeout != None:
            mod_kwargs['hard_timeout'] = hard_timeout
        if priority != None:
            mod_kwargs['priority'] = priority
        if buffer_id != None:
            mod_kwargs['buffer_id'] = buffer_id
        if out_port != None:
            mod_kwargs['out_port'] = out_port
        if out_group != None:
            mod_kwargs['out_group'] = out_group
        if flags != None:
            mod_kwargs['flags'] = flags
        if match != None:
            mod_kwargs['match'] = match
        if instructions != None:
            mod_kwargs['instructions'] = instructions
        return dp.ofproto_parser.OFPFlowMod(**mod_kwargs)


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


    def dropPackage(self, dp, match):
        global TABLE_FILTER
        global PRIORITY_MAX

        return [self.flowmod(dp, TABLE_FILTER,
                             match=match, priority=PRIORITY_MAX,
                             instructions=[])]


    def flowdel(self, dp, table_id, priority=None, match=None, out_port=None):
        "Generate an OFPFlowMod through flowmod with the OFPFC_DELETE command"

        return self.flowmod(dp, table_id,
                            priority=priority,
                            match=match,
                            command=dp.ofproto.OFPFC_DELETE,
                            out_port=out_port or dp.ofproto.OFPP_ANY,
                            out_group=dp.ofproto.OFPG_ANY)


    def clean_all_flows(self, dp):
        "Remove all flows with the SS2 cookie from all tables"
        all_ss2_tables = [TABLE_ACL, TABLE_FILTER, TABLE_SRC, TABLE_DST]
        msgs = []
        for table in all_ss2_tables:
            msgs += [self.flowdel(dp, table)]
        return msgs


    def barrier_request(self, dp):
        """Generate an OFPBarrierRequest message

        Used to ensure all previous flowmods are applied before running the
        flowmods after this request. For example, make sure the flowmods that
        delete any old flows for a host complete before adding the new flows.
        Otherwise there is a chance that the delete operation could occur after
        the new flows are added in a multi-threaded datapath."""


        return dp.ofproto_parser.OFPBarrierRequest(datapath=dp)
