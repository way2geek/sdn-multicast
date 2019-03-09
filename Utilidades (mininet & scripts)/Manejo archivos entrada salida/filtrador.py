#######################################################################
#           FUNCIONES
#######################################################################
def procesarSalidaController(nombres_archivos, txt_of, txt_mcast):
#   Array nombres_archivos = [archivo con salida de controller,
#                               archivo para openflow,
#                               archivo para IGMP
#                               archivo para multicast]
#   txt_of es la forma de identificar la linea para openflow
#   txt_mcast es la forma de identificar la linea para Multicast
#   el resto se sabe sera IGMP

    if nombres_archivos[0].mode == 'r':
        lineas = nombres_archivos[0].readlines()
        for lin in lineas:
            # Observa primeros 5 caracteres de la linea
            # y compara con posibles sintaxis de openflow
            if(lin[0:6] == txt_of[0]):
                #Escribe detalle openflow
                nombres_archivos[1].write(lin)
            elif lin[0:9]==txt_mcast[0]:
                #Escribe detalle multicast
                nombres_archivos[3].write(lin)
            else:
                #Escribe detalle controller e IGMP
                nombres_archivos[2].write(lin)

def procesarGruposMulticast(arch_mcast,dic_grupos_mcast):
    eventos = ["Multicast Group Added",
               "Multicast Group Member Changed",
               "Multicast Group Removed"]

    if arch_mcast.mode == 'r':
        lin_mcast = arch_mcast.readlines()
        for lin in lin_mcast:
            #se hace un split para obtener el comienzo de las lineas
            #del archivo. Coincidiran con uno de los tres mensajes
            #de "eventos"
            lin_aux = lin.split(":",1)

            #Caso Grupo Agregado
            if (lin_aux[0]==eventos[0]):
                ip_grupo = obtenerGroupIP(lin_aux[1])
                print (" - Se agrego grupo: "+ ip_grupo)
                #agregar key a diccionario?

            #Caso Miembro Agregado a Grupo
            if (lin_aux[0]==eventos[1]):
                ip_grupo=obtenerGroupIP(lin_aux[1])
                host = obtenerHost(lin_aux[1])
                print (" - - Se modifico un miembro del grupo : " + ip_grupo)
                print(" - - Nuevos miembros: " + host)
                #agregar value a diccionario?

            #Caso Grupo Removido
            if (lin_aux[0]==eventos[2]):
                ip_grupo = obtenerGroupIP(lin_aux[1])
                print(" - - - Se borro un grupo: " + ip_grupo)
                # eliminar key de diccionario?
    else:
        print "hola :) "

def obtenerGroupIP(linea):
    ip_grupo = linea.split("]",1)[0].split("[",1)[1]
    return ip_grupo

def obtenerHost(linea):
    host=linea.split("hosts:[")[1].split("]")[0]
    return host

def cerrarArchivos(nombres_archivos):
    for i in nombres_archivos:
        i.close()


#######################################################################
#           FUNCION MAIN()
#######################################################################

def main():
    file_lectura_raw = open("0-output_controller.txt", "r")
    file_salida_of = open("1-output_of.txt","w+")
    file_salida_controller = open("2-salidaIGMPController.txt","w+")

    file_salida_multicast = open("3-output_mcast.txt","w+")
    texto_openflow= ["packet"]
    texto_multicast= ["Multicast"]

    #Diccionario de grupos Multicast
    #keys = IP Multicast del grupo
    #values = array de hosts del grupo
    dic_grupos_mcast = {}

    lista_archivos = [file_lectura_raw,
                      file_salida_of,
                      file_salida_controller,
                      file_salida_multicast]

    #completar archivos
    procesarSalidaController(lista_archivos, texto_openflow, texto_multicast)

    #Se cierran archivos utlizados
    cerrarArchivos(lista_archivos)

    file_salida_multicast = open("3-output_mcast.txt","r")
    #presentar informacion de grupos multicast
    procesarGruposMulticast(file_salida_multicast, dic_grupos_mcast)
    #Se cierran archivos utlizados
    cerrarArchivos(file_salida_multicast)

#CORRER PROGRAMA !
if __name__=="__main__":
    main()
