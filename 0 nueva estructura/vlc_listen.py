import sys
import os

def suscribir(una_ip):
    comando = "vlc udp://@{}".format(una_ip)
    # opcion quiet
    # comando = "vlc udp://@{} --quiet".format(una_ip)
    print (comando)
    os.system(comando)
    pass

if __name__ == '__main__':
    if(len(sys.argv)==2):
	    # IP_GRUPO = sys.argv[1]
        suscribir(sys.argv[1])
    else:
            print("ERROR: no se ingreso comando listen correcto. Cerrando...")
