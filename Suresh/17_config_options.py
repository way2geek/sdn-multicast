'''

ryu-manager 17_config_options.py   --config-file  params.conf

reference:
https://stackoverflow.com/questions/17424905/passing-own-arguments-to-ryu-proxy-app

ryu-manager paramtest.py --config-file [PATH/TO/FILE/params.conf]

'''

from ryu import cfg
from ryu.base import app_manager


class SimpleSwitch13(app_manager.RyuApp):
    def __init__(self, *args, **kwargs):
        super(SimpleSwitch13, self).__init__(*args, **kwargs)
        CONF = cfg.CONF
        CONF.register_opts([
            cfg.IntOpt('param1_int', default=0, help = ('The ultimate answer')),
            cfg.StrOpt('param2_str', default='default', help = ('A string')),
            cfg.ListOpt('param3_list', default = None, help = ('A list of numbers')),
            cfg.FloatOpt('param4_float', default = 0.0, help = ('Pi? Yummy.'))]
            )

        print 'param1_int = {}'.format(CONF.param1_int)
        print 'param2_str = {}'.format(CONF.param2_str)
        print 'param3_list = {}'.format(CONF.param3_list)
        print 'param4_float = {}'.format(CONF.param4_float)