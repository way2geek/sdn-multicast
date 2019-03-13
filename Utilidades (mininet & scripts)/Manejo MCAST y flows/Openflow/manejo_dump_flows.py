#cookie=0x0, duration=352.407s, table=0, n_packets=27, n_bytes=2346, priority=10,in_port="s1-eth2" actions=group:50
#cookie=0x0, duration=352.407s, table=0, n_packets=4, n_bytes=280, priority=10,in_port="s1-eth3" actions=group:51
#cookie=0x0, duration=352.407s, table=0, n_packets=27, n_bytes=2346, priority=0 actions=CONTROLLER:65535

def procesar_archivo(archivo):
    entradas = {'':''}
    entry = 1
    if archivo.mode == 'r':
        lineas = archivo.readlines()
        for lin in lineas:
            # print entry
            # split segun comas, mantiene encabezados
            cookie, duracion, tabla, paquetes, bytes, prioridad, inPortAndAction= lin.split(",")
            inPort, accion = inPortAndAction.split(" ")

            # split segun "=" y toma el segundo valor. Elimina encabezados
            cookie = cookie.split("=")[1]
            duracion = duracion.split("=")[1]
            tabla = tabla.split("=")[1]
            paquetes = paquetes.split("=")[1]
            bytes = bytes.split("=")[1]
            prioridad = prioridad.split("=")[1]
            inPort = inPort.split("=")[1]
            accion = accion.split("=")[1]

            #armado de diccionario
            valor =[cookie, duracion, tabla, paquetes, bytes, prioridad, inPort, accion]
            # print valor
            entradas[entry]=valor
            entry = entry + 1

    return entradas


def imprimir_tabla_completa(contenido):
    print ("cookie: \t duration: \t table: \t n_packets: \t n_bytes: \t priority: \t in_port: \t actions:")
    for a, b in contenido.items():
        print (b)

def cerrarArchivos(nombres_archivos):
    for i in nombres_archivos:
        i.close()

#######################################################################
#           FUNCION MAIN()
#######################################################################

def main():
    file_lectura = open("dump_flows.txt", "r")
    lista_archivos = [file_lectura]
    contenido = procesar_archivo(file_lectura)
    # print "Tabla completa:"
    imprimir_tabla_completa(contenido)

    #Se cierran archivos utlizados
    cerrarArchivos(lista_archivos)

#CORRER PROGRAMA !
if __name__=="__main__":
    main()
