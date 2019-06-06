#1 = cookie=0x0, duration=102.594s, table=0, n_packets=3, n_bytes=238, priority=1,in_port=3,dl_dst=00:00:00:00:11:11 actions=output:2
#2 = cookie=0x0, duration=352.407s, table=0, n_packets=4, n_bytes=280, priority=10,in_port="s1-eth3" actions=group:51
#3 = cookie=0x0, duration=352.407s, table=0, n_packets=27, n_bytes=2346, priority=0 actions=CONTROLLER:65535

def tipo_entry(linea):
    tipo = -1

    if("CONTROLLER" in linea):
        tipo=3  #formato de flow entry que envia a controlador
    elif ("dl_dst" in linea):
        tipo=1
    else:
        tipo=2

    return tipo


def procesar_archivo(archivo, output):
    if archivo.mode == 'r':
        lineas = archivo.readlines()
        for lin in lineas:
            lin2 = reemplazar_no_deseado(lin)
            # lin2=lin2.repalce("\t"," ")
            # print (lin2)
            if output.mode == 'w+':
                output.write("\n")
                output.write(lin2)


def reemplazar_no_deseado(linea_sin_proce):
    lin_proce = linea_sin_proce.replace("cookie","")
    lin_proce = lin_proce.replace("duration","")
    lin_proce = lin_proce.replace("table","")
    lin_proce = lin_proce.replace("n_packets","")
    lin_proce = lin_proce.replace("n_bytes","")
    lin_proce = lin_proce.replace("priority","")
    lin_proce = lin_proce.replace("in_port","")
    lin_proce = lin_proce.replace("actions","")
    lin_proce = lin_proce.replace("=","")
    lin_proce = lin_proce.replace(" ","")
    lin_proce = lin_proce.replace(",","\t\t\t\t\t")
    return lin_proce

def cerrarArchivos(nombres_archivos):
    for i in nombres_archivos:
        i.close()

#######################################################################
#           FUNCION MAIN()
#######################################################################

def main():
    file_lectura = open("dump_flows3.txt", "r")
    file_salida = "salida.txt"

    output = open(file_salida, "w+")
    if output.mode == 'w+':
        output.write("cookie: \t duration: \t table: \t n_packets: \t n_bytes: \t priority: \t in_port: \t actions:")

    procesar_archivo(file_lectura, output)

    #Se cierran archivos utlizados
    lista_archivos = [file_lectura, output]
    cerrarArchivos(lista_archivos)

#CORRER PROGRAMA !
if __name__=="__main__":
    main()























#                       OLD

# def procesar_archivo(archivo, arch_output):
#     entradas = {'':''}
#     entry = 1
#     if archivo.mode == 'r':
#         lineas = archivo.readlines()
#         for lin in lineas:
#             # print entry
#             # split segun comas, mantiene encabezados
#             cookie, duracion, tabla, paquetes, bytes, prioridad, inPortAndAction= lin.split(",")
#             inPort, accion = inPortAndAction.split(" ")
#
#             # split segun "=" y toma el segundo valor. Elimina encabezados
#             cookie = cookie.split("=")[1]
#             duracion = duracion.split("=")[1]
#             tabla = tabla.split("=")[1]
#             paquetes = paquetes.split("=")[1]
#             bytes = bytes.split("=")[1]
#             prioridad = prioridad.split("=")[1]
#             inPort = inPort.split("=")[1]
#             accion = accion.split("=")[1]
#
#             linea_leida = cookie + duracion + tabla + paquetes + bytes + prioridad + inPort + accion
#             print (linea_leida)
#             # escribir_linea(linea_leida, arch_output)
#
#             # extraer_info(lin)
#             #armado de diccionario
#             # valor =[cookie, duracion, tabla, paquetes, bytes, prioridad, inPort, accion]
#             # print valor
#             # entradas[entry]=valor
#             # entry = entry + 1
#
#     return entradas
