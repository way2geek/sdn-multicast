# sudo ovs-ofctl -O OpenFlow13 dump-flows s1
#       7 10
#cookie=0x0, duration=352.407s, table=0, n_packets=27, n_bytes=2346, priority=10,in_port="s1-eth2" actions=group:50
#cookie=0x0, duration=352.407s, table=0, n_packets=4, n_bytes=280, priority=10,in_port="s1-eth3" actions=group:51
#cookie=0x0, duration=352.407s, table=0, n_packets=27, n_bytes=2346, priority=0 actions=CONTROLLER:65535

def procesar_archivo(archivo):
    flow_entries = {'',''}
    entry = 0
    if archivo.mode == 'r':
        lineas = archivo.readlines()
        for lin in lineas:
            entry = entry + 1
            lin_aux = lin.split('= ,')
            # lin_aux2 = extraer_titulos(lin_aux)
            for j in lin_aux:
                print (lin_aux)
            flow_entries={entry:lin_aux}

    return flow_entries

# def extraer_titulos(linea):
#     for i in linea:
#         cookie=linea[2]
#         cookie = linea.split("=",1)[1]
#         duracion = linea.split("=")[2]
#         tabla = linea.split("=",3)[4]
#         paquetes = linea.split("=",4)[6]
#         bytes = linea.split("=",5)[8]
#         prioridad = linea.split("=",6)[10]
#         in_port = linea.split("=",7)[12]
#         actions = linea.split("=",8)[14]
#     retorno = [cookie, duracion, tabla, paquetes, bytes, prioridad, in_port, actions]
#     return retorno

def imprimir_tabla_completa(flow_entries):
    print ("Cookie:\t\tDuracion:\t\tTabla:\t\tPaquetes:\t\tBytes:\t\tin_port:\t\tActions:")
    for i in flow_entries.keys():
        for j in flow_entries[i]:
            print (flow_entries[i])

# def imprimir_tabla_resumen(flow_entries):
#     print ("Tabla:\t\tPaquetes:\t\tin_port:\t\tActions:\n")


def cerrarArchivos(nombres_archivos):
    for i in nombres_archivos:
        i.close()

#######################################################################
#           FUNCION MAIN()
#######################################################################

def main():
    file_lectura = open("dump_flows.txt", "r")
    lista_archivos = [file_lectura]
    f_entries = procesar_archivo(file_lectura)

    # print "Tabla completa:"
    imprimir_tabla_completa(f_entries)

    # print "Tabla resumen:"
    # imprimir_tabla_resumen(f_entries)

    #Se cierran archivos utlizados
    cerrarArchivos(lista_archivos)


#CORRER PROGRAMA !
if __name__=="__main__":
    main()
