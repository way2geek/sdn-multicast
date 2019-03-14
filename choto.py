
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

TABLE_ACL = 10
TABLE_FILTER = 11
TABLE_MAC = 12

class Choto(app_manager.RyuApp):

    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(Choto, self).__init__(*args, **kwargs)
        self.mac_to_port = {}
        self.ip_to_port = {}
        self.multicast_tree = {}


    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        datapath = ev.msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        #match = parser.OFPMatch()
        #actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER,
        #                                  ofproto.OFPCML_NO_BUFFER)]
        #self.add_flow(datapath, PRIORITY_MIN, match, actions)

        # entry 2
        #actions = [parser.OFPActionGroup(group_id=51)]
         #match = parser.OFPMatch(in_port=3)
         #self.add_flow(datapath, 10, match, actions)

        msgs = self.add_default_flows(datapath)
        self.send_msgs(datapath, msgs)


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
        self.mac_to_port[dpid][origen] = in_port
        print('HOLAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA')

        if self.esMulticast(destino):
            #self.multicast_tree.setdefault(destino, {})
            print('HAY TRAFICO MULTICAST')
            self.manage_Multicast(datapath)

        else:
            #if in_port != 2:
            print('NO HAY TRAFICO MULTICAST')
            if destino in self.mac_to_port[dpid]:
                out_port = self.mac_to_port[dpid][destino]
            else:
                out_port = ofproto.OFPP_FLOOD

            actions = [parser.OFPActionOutput(out_port)]

            # install a flow to avoid packet_in next time
            if out_port != ofproto.OFPP_FLOOD:
                match = self.match(datapath, in_port, destino, origen)
                instructions = [self.apply_actions(datapath, actions)]
                # verify if we have a valid buffer_id, if yes avoid to send both
                # flow_mod & packet_out
                if msg.buffer_id != ofproto.OFP_NO_BUFFER:
                    flujo = [self.flowmod(datapath,TABLE_MAC,
                                match=match,
                                priority=PRIORITY_MID,
                                instructions=instructions,
                                buffer_id= msg.buffer_id)]
                    datapath.send_msg(flujo)
                else:
                    flujo = [self.flowmod(datapath,TABLE_MAC,
                                match=match,
                                priority=PRIORITY_MID,
                                instructions=instructions)]
                    datapath.send_msg(flujo)

            data = None
            if msg.buffer_id == ofproto.OFP_NO_BUFFER:
                data = msg.data

            out = parser.OFPPacketOut(datapath=datapath, buffer_id=msg.buffer_id,
                                              in_port=in_port, actions=actions, data=data)
            datapath.send_msg(out)


    def add_default_flows(self, dp):
        msgs = []
        ofp = dp.ofproto
        parser = dp.ofproto_parser


        if dp.id == 1:
            # add group tables
            self.manage_Multicast(dp)
            actions = [parser.OFPActionGroup(group_id=50)]
            instructions = [self.apply_actions(dp, actions)]
            match = parser.OFPMatch(in_port=2)
            msgs += [self.flowmod(dp, TABLE_ACL,
                                   match=match,
                                   priority=PRIORITY_LOW,
                                   instructions=instructions)]


        ### TABLE_ACL ###
        # Add a low priority table-miss flow to forward to the switch table.
        # Other modules can add higher priority flows as needed.
        instructions = [self.goto_table(dp, TABLE_FILTER)]
        msgs += [self.flowmod(dp, TABLE_ACL,
                              match=self.match(dp),
                              priority=PRIORITY_MIN,
                              instructions=instructions)]

        ### TABLE_FILTER ###

        # Drop LLDP
        msgs += self.dropPackage(dp, self.match(dp, eth_type=ether_types.ETH_TYPE_LLDP))

        # Drop STDP BPDU
        msgs += self.dropPackage(dp, self.match(dp, eth_dst='01:80:c2:00:00:00'))
        msgs += self.dropPackage(dp, self.match(dp, eth_dst='01:00:0c:cc:cc:cd'))

        #drop paquete igmp
        #msgs += self.dropPackage(dp, self.match(dp, eth_dst='01:00:5e:00:00:16'))

        # Drop Broadcast Sources
        msgs += self.dropPackage(dp, self.match(dp, eth_src='ff:ff:ff:ff:ff:ff'))

        #msgs += self.dropPackage(dp, self.match(dp, eth_dst ='ff:ff:ff:ff:ff:ff'))

        msgs += self.dropPackage(dp, self.match(dp, eth_type=ether_types.ETH_TYPE_IPV6))

        #VOY A MAC TABLE
        match = self.match(dp)
        actions = [self.action_output(dp, ofp.OFPP_CONTROLLER, max_len=256)]
        instructions = [self.apply_actions(dp, actions),
                        self.goto_table(dp, TABLE_MAC)]
        msgs += [self.flowmod(dp,
                              TABLE_FILTER,
                              match=match,
                              priority=PRIORITY_MIN,
                              instructions=instructions)]


        #TABLE_MAC
        actions = [self.action_output(dp, ofp.OFPP_FLOOD)]
        instructions = [self.apply_actions(dp, actions)]
        msgs += [self.flowmod(dp,
                              TABLE_MAC,
                              match=match,
                              priority=PRIORITY_MIN,
                              instructions=instructions)]

        return msgs


    def send_msgs(self, dp, msgs):
        "Send all the messages provided to the datapath"
        for msg in msgs:
            dp.send_msg(msg)


    def goto_table(self, dp, table_id):
        "Generate an OFPInstructionGotoTable message"

        return dp.ofproto_parser.OFPInstructionGotoTable(table_id)


    def esMulticast(self, dst):
        return (dst[0:2] == '01' or dst[0:5] == '33:33')


    def manage_Multicast(self, datapath):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        # Hardcoding the stuff, as we already know the topology diagram.
        # Group table1
        # Receiver port2, forward it to port1 and Port3
        actions1 = [parser.OFPActionOutput(1)]
        actions2 = [parser.OFPActionOutput(3)]
        actions3 = [parser.OFPActionOutput(4)]

        buckets = [parser.OFPBucket(actions=actions1),
                   parser.OFPBucket(actions=actions2),
                   parser.OFPBucket(actions=actions3)]

        req = parser.OFPGroupMod(datapath, ofproto.OFPGC_ADD,
                                 ofproto.OFPGT_ALL, 50, buckets)
        datapath.send_msg(req)


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


    def dropPackage(self, dp, match):
        global TABLE_FILTER
        global PRIORITY_MAX

        return [self.flowmod(dp, TABLE_FILTER,
                             match=match, priority=PRIORITY_MAX,
                             instructions=[])]


    def add_group_mode():
        pass
