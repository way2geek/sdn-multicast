#DEFINO FUNCIONES AUXILIARES PARA LA APLICACION

from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.lib.packet import ethernet, ether_types as ether, packet
from ryu.ofproto import ofproto_v1_3


class AuxApp(object):

    "Metodos auxiliares para la aplicacion"

    ## Static Helper Methods

    @staticmethod
    def send_msgs(dp, msgs):
        "Send all the messages provided to the datapath"

        for msg in msgs:
            dp.send_msg(msg)


    @staticmethod
    def apply_actions(dp, actions):
        "Generate an OFPInstructionActions message with OFPIT_APPLY_ACTIONS"

        return dp.ofproto_parser.OFPInstructionActions(
            dp.ofproto.OFPIT_APPLY_ACTIONS, actions)


    @staticmethod
    def action_output(dp, port, max_len=None):
        "Generate an OFPActionOutput message"

        kwargs = {'port': port}
        if max_len != None:
            kwargs['max_len'] = max_len

        return dp.ofproto_parser.OFPActionOutput(**kwargs)


    @staticmethod
    def match(dp, in_port=None, eth_dst=None, eth_src=None, eth_type=None,
              **kwargs):
        "Generate an OFPMatch message"

        if in_port != None:
            kwargs['in_port'] = in_port
        if eth_dst != None:
            kwargs['eth_dst'] = eth_dst
        if eth_src != None:
            kwargs['eth_src'] = eth_src
        if eth_type != None:
            kwargs['eth_type'] = eth_type
        return dp.ofproto_parser.OFPMatch(**kwargs)


    @staticmethod
    def log(self, message):
        self.logger.info(message)
        return
