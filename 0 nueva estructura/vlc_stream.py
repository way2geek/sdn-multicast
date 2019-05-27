import os
import sys
def hacer_streaming(path_media, ip_group):
    comando = "vlc {} --sout udp:{}".format(path_media, ip_group)
    print("Comenzando streaming...")
    os.system(comando)

if __name__ == '__main__':
	if(len(sys.argv)==3):
            PATH_MEDIA= sys.argv[1]
            IP_MCAST = sys.argv[2]
            hacer_streaming(PATH_MEDIA, IP_MCAST)
	else:
            print("ERROR: no se ingreso comando stream correcto. Cerrando...")
