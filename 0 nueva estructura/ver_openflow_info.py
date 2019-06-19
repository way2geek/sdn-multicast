import sys
import os
import json

#Ejecuta dump-flows y dump-groups para todos los switches de la topologia.
def mostrar_of_info(nombre_topologia):
    filejson = open("./topologias/{}".format(nombre_topologia))
    topojson = json.load(filejson)    
    for switch in topojson['switches']:
        flow_command = "ovs-ofctl -O OpenFlow13 dump-flows {}".format(switch)
        group_command = "ovs-ofctl -O OpenFlow13 dump-groups {}".format(switch)
        print("\n - OPENFLOW - DUMP FLOWS SWITCH {} \n".format(switch))
        os.system(flow_command)
        # file_command = flow_command+str(">>info_openflow.txt")

        print("\n - OPENFLOW - DUMP GROUPS SWITCH {} \n".format(switch))
        os.system(group_command)
        # file_command = group_command+str("&>info_openflow.txt")

if __name__ == '__main__':
    if(len(sys.argv)==2):
        mostrar_of_info(sys.argv[1])
    else:
        #print("ERROR: no se ingreso comando correcto. Cerrando...")
        mostrar_of_info("topo_anillo_simple.json")
