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
                            2:{
                               'out':False,
                               'in':True
                               },
                            1:{
                               'out':True,
                               'in':False
                              }
                            }
                    }
       },
      1:{
          '225.0.0.5':{
                      'replied':True,
                      'leave':False,
                      'ports':{
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

TABLE_ACL = 0
TABLE_FILTER = 10
TABLE_SRC = 11
TABLE_DST = 12

GROUP_TABLE_1 = 100
GROUP_TABLE_2 = 101


class PruebaGroupTable(app_manager.RyuApp):

    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(PruebaGroupTable, self).__init__(*args, **kwargs)



    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        "Handle new datapaths attaching to Ryu"
        dp = ev.msg.datapath
        ofp = dp.ofproto
        #pkt = packet.Packet(ev.msg.data)

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

        destino = dst.eth
        "ENVIO TRAFICO MULTICAST A GROUP TABLE"

        if self.esMulticast(destino):
            print('HAY TRAFICO MULTICAST EN LA RED')
            msgs += [self.send_group_mode(dp,destino)]
            actions = [self.action_output(dp, ofp.OFPP_CONTROLLER, max_len=256),
                       parser.OFPActionGroup(group_id=GROUP_TABLE_1)]
            match = self.match(dp)
            instructions = [self.apply_actions(dp, actions)]
            msgs += [self.flowmod(dp, TABLE_FILTER,
                                  match = match,
                                  priority = PRIORITY_MAX,
                                  instructions = instructions)]

    #    msgs = self.learn_source(
    #        dp=dp,
    #        port=in_port,
    #        eth_src=eth.src)

        self.send_msgs(dp, msgs)


    def add_datapath(self, dp):

        msgs = []
        msgs = self.add_default_flows(dp)

        return msgs


    def add_default_flows(self, dp):
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
        #msgs += self.dropPackage(dp, self.match(dp, ipv4_dst = '192.168.1.13'))

        # Drop LLDP
        msgs += self.dropPackage(dp, self.match(dp, eth_type=ether_types.ETH_TYPE_LLDP))

        # Drop STDP BPDU
        msgs += self.dropPackage(dp, self.match(dp, eth_dst='01:80:c2:00:00:00'))
        msgs += self.dropPackage(dp, self.match(dp, eth_dst='01:00:0c:cc:cc:cd'))

        # Drop Broadcast Sources
        msgs += self.dropPackage(dp, self.match(dp, eth_src='ff:ff:ff:ff:ff:ff'))

        return msgs


    def send_group_mode(self, dp, dst):

        global grupos
        ofproto = dp.ofproto
        buckets = []
        ports = []

        ports = self.getGroupPorts(grupos, dst, dp)
        bucket = self.setActionsBuckets(dp, ports)
        buckets.append(bucket)

        return [self.groupMod(dp, GROUP_TABLE_1,
                              type = ofproto.OFPGT_ALL,
                              buckets = buckets)]


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
        actions = []

        for port in ports:
            actions.append(parser.OFPActionOutput(port))

        return actions


    def esMulticast(dst):
        return (dst[0:2] == '01' or dst[0:5] == '33:33' or dst == 'ff:ff:ff:ff:ff:ff')


    def getDicPorts(self, grupos, dst, datapath):
        ports = {}
        puertosOut = []
        puertosIn = []
        for dp, g_info in grupos.items():
            if dp == datapath:
                print(dp)
                for destino, d_info in g_info.items():
                    print(destino)
                    if destino == dst:
                        ports = d_info['ports']
                    else:
                        print('NO SE ENCUENTRA EL GRUPO REGISTRADO')
        return ports


    def getGroupPorts(self, grupos, dst, dp):
        puertosIN = []
        puertosOUT = []
        puertos = self.getDicPorts(grupos, dst, dp)
        for puerto, p_info in puertos.items():
            print(p_info)
            if p_info['out'] == True:
                puertosOUT.append(puerto)
            #elif p_info['in'] ==True:
            #    puertosIN.append(puerto)
        return puertosOUT


    def groupMod(self, dp, group_id, command=None, type = None, buckets = None):

        mod_kwargs = {
            'datapath': dp,
            'group_id': group_id,
            'command': command or dp.ofproto.OFPGC_ADD,
            'cookie': 0x55200001
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
