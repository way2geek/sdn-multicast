from  ryu.base  import  app_manager
from  ryu.controller  import  ofp_event
from  ryu.controller.handler  import  CONFIG_DISPATCHER
from  ryu.controller.handler  import  MAIN_DISPATCHER
from  ryu.controller.handler  import  set_ev_cls
from  ryu.ofproto  import  ofproto_v1_3
from  ryu.lib  import  igmplib
from  ryu .lib.dpid  import  str_to_dpid
from  ryu.lib.packet  import  packet
from  ryu.lib.packet  import ethernet
from  ryu.app  import  simple_switch_13


class  SimpleSwitchIgmp13 ( Simple_switch_13 . SimpleSwitch13 ):
    OFP_VERSIONS  =  [ Ofproto_v1_3 . OFP_VERSION ]
    _CONTEXTS  =  { 'Igmplib' :  Igmplib . IgmpLib }

    def  __init__ ( self ,  * args ,  ** kwargs ):
        super ( SimpleSwitchIgmp13 ,  self ) . __init__ ( * args ,  ** kwargs )
        self . Mac_to_port  =  {}
        self . _Snoop  =  kwargs [ 'Igmplib' ]
        self . _Snoop . Set_querier_mode (
            dpid = str_to_dpid ( '0000000000000001'),  server_port = 2 )

    Attoset_ev_cls ( Igmplib . EventPacketIn ,  MAIN_DISPATCHER )
    def  _Packet_in_handler ( Self ,  Ev ):
        Msg  =  Ev . Msg
        Datapath  =  Msg . Datapath
        Ofproto  =  Datapath . Ofproto
        Parser  =  Datapath . Ofproto_parser
        In_port  =  Msg . Match [ 'In_port' ]

        pkt  =  packet . Packet ( msg . data )
        eth  =  pkt . get_protocols ( ethernet . ethernet ) [ 0 ]

        dst  =  eth . dst
        src  =  eth . src

        dpid  =  datapath . id
        self . mac_to_port . setdefault ( dpid ,  {})

        self . logger . info ( "packet in % s % s % s % s " , dpid , src , dst , in_port )

        # learn a mac address to avoid FLOOD next time.
        self . mac_to_port [ dpid ] [ src ]  =  in_port

        If  Dst  In  Self . Mac_to_port [ Dpid ]:
            Out_port  =  Self . Mac_to_port [ Dpid ] [ Dst ]
        Else :
            Out_port  =  Ofproto . OFPP_FLOOD

        actions  =  [ parser . OFPActionOutput ( out_port )]

        Install A Flow # To Avoid Packet_in Next Time
        If  Out_port  =!  Ofproto . OFPP_FLOOD :
            Match  =  Parser . OFPMatch ( In_port = In_port ,  Eth_dst = Dst )
            Self . Add_flow ( Datapath ,  1 ,  Match ,  Actions )

        data  =  None
        if  msg . buffer_id  ==  ofproto . OFP_NO_BUFFER :
            data  =  msg . data

        out  =  parser . OFPPacketOut ( datapath = datapath ,  buffer_id = msg . buffer_id ,
                                  in_port = in_port ,  actions = actions ,  data = data )
        datapath . send_msg ( out )

    Attoset_ev_cls ( Igmplib . IbuiienutiemuulticastGroupStateChanged ,
                MAIN_DISPATCHER )
    def  _Status_changed ( self ,  ev ):
        msg  =  {
            Igmplib . MG_GROUP_ADDED :  'Multicast Group Added' ,
            Igmplib . MG_MEMBER_CHANGED :  'Multicast Group Member Changed' ,
            Igmplib . MG_GROUP_REMOVED :  'Multicast Group the Removed' ,
        }
        self . logger . info ( "% s : [ % s ] querier: [ % s ] hosts: % s " ,
                         msg . get ( ev . reason ),  ev . address ,  ev . src ,
                         ev . dsts )
