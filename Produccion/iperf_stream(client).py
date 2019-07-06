import os
import sys
def iperf_client(ip_group):
    comando = "iperf -c {} -u -T 32 -t 60 -i 1 -i 1".format(ip_group)
    os.system(comando)

if __name__ == '__main__':
	if(len(sys.argv)==2):
            IP_MCAST = sys.argv[1]
            iperf_client(IP_MCAST)
	else:
            print("ERROR: no se ingreso comando correcto. Cerrando...")
