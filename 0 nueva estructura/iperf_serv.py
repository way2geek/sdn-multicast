import os
import sys
def iperf_serv(ip_group):
    comando = "iperf -s -u -B {} -i 1".format(ip_group)
    os.system(comando)

if __name__ == '__main__':
	if(len(sys.argv)==3):
            IP_MCAST = sys.argv[1]
            iperf_serv(IP_MCAST)
	else:
            print("ERROR: no se ingreso comando correcto. Cerrando...")