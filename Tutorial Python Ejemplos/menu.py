import sys
import os

def mostrarAyuda():
    print("-AYUDA-")

    print("\t1- Topologia linear pequena:")
    print("\t\t Se trata de una topologia con X switches en linea. Cada switch tiene N hosts conectados.")
    # imprimir_topo_linear_peq()
    
    print("\t2- Topologia linear grande.")
    print("\t\t Se trata de una topologia con X switches en linea. Cada switch tiene N hosts conectados.")
    # imprimir_topo_linear_gra()
    
    print("\t3- Tolologia arbol con 3 ramificiaciones.")
    print("\t\t Se trata de una topologia que representa un arbol de tres ramificaciones.")
    print("\t\t Se compone de X switches y cada switch tiene N hosts conectados.")
    # imprimir_topo_arbol_3_ram()
    
    print("\t4- Topologia arbol con 4 niveles de profundidad.")
    print("\t\t Se trata de una topologia que representa un arbol de varias ramificaciones y 4 niveles de profundidad.")
    print("\t\t Se compone de X switches y cada switch tiene N hosts conectados.")
    # imprimir_topo_arbol_profunda()

    print("\t5- Topologia anillo simple.")
    print("\t\t Se trata de una topologia de 4 switches conectados en forma de anillo.")
    print("\t\t Cada switch cuenta con N hosts conectados.")
    # imprimir_topo_anillo_simple()
    
    print("\t6- Topologia arbol con anillos.")
    print("\t\t Similar a topologia 4 pero agregando enlaces nuevos en los niveles inferiores del arbol.")
    print("\t\t Cada enlace nuevo, forma un anillo dentro del arbol.")
    print("\t\t Cada switch cuenta con N hosts conectados.")
    # imprimir_topo_arbol_con_anillos()

    print("\t7- Topologia full mesh simple.")
    print("\t\t Similar a topologia 5 pero agregando enlaces que interconectan todos los switches")
    print("\t\t Cada switch cuenta con N hosts conectados.")
    # imprimir_topo_full_mesh_simple()

    print("\t8- Topologia full mesh compleja.")
    print("\t\t Se trata de una topologia de 8 switches con interconexion directa entre todos ellos.")
    print("\t\t Cada switch cuenta con N hosts conectados.")
    # imprimir_topo_full_mesh_compleja()
    pass

def imprimir_topo_linear_peq():
    pass
def imprimir_topo_linear_gra():
    pass
def imprimir_topo_arbol_3_ram():
    pass
def imprimir_topo_arbol_profunda():
    pass
def imprimir_topo_anillo_simple():
    pass
def imprimir_topo_arbol_con_anillos():
    pass
def imprimir_topo_full_mesh_simple():
    pass
def imprimir_topo_full_mesh_compleja():
    pass

def imprimirMenu():
    print("")
    print("")
    print("- - MENU PRINCIPAL - -")
    print("Seleccione la opción deseada o ingrese 0 para salir")
    print("\t1- Topologia linear pequena.")
    print("\t2- Topologia linear grande.")
    print("\t3- Tolologia arbol con 3 ramificiaciones.")
    print("\t4- Topologia arbol con 4 niveles de profundidad.")
    print("\t5- Topologia anillo simple.")
    print("\t6- Topologia arbol con anillos.")
    print("\t7- Topologia full mesh simple.")
    print("\t8- Topologia full mesh compleja.")
    print("\t9- Ver ayuda.")
    print("\t0- Salir.")
    pass

def cerrar_programa():
    print("Cerrando programa")
    print("Cerrando programa.")
    print("Cerrando programa..")
    print("Cerrando programa...")
    print("Cerrando programa....")
    print("Cerrando programa.....")

def leerIngreso():
    while (True):
        ingreso = input("Opcion:")
        try:
            ingreso = int(ingreso)
        except:
            print("ERROR: ingreso incorrecto.")
            continue
        if(ingreso >= 0 and ingreso <= 9):
            break
        else:
            print ("Ingreso fuera de rango.")
    # ingreso = int(input())
    return ingreso

def ejec_app_gen_json():
    pass
def ejec_leer_topo_json():
    pass
def ejec_controller():
    pass
    
# LLAMADOS

opcion = -1
while (opcion != 0):
    imprimirMenu()
    print("Seleccione una opcion.")
    opcion = leerIngreso()
    print("OPCION INGRESADA: {}".format(opcion))
    
    if (opcion == 1):
        print ('Seleccion opcion 1')
    elif (opcion == 2):
        print ('Seleccion opcion 2')
    elif (opcion ==3):
        print ('Seleccion opcion 3')
    elif (opcion ==4):
        print ('Seleccion opcion 4')
    elif (opcion ==5):
        print ('Seleccion opcion 5')
    elif (opcion ==6):
        print ('Seleccion opcion 6')
    elif (opcion ==7):
        print ('Seleccion opcion 7')
    elif (opcion ==8):
        print ('Seleccion opcion 8')
    elif (opcion ==9):
        mostrarAyuda()
    elif (opcion ==0):
        cerrar_programa()
    else:
        print('Ingreso invalido.')




# def _cargaDeParametros(topologiaSeleccionada):
#     switch (topologiaSeleccionada):
#         if (topologiaSeleccionada == '1'):
#             #llamar funcion especifica para lineal
#             _cargaDeParametrosLinear()

#         elif (topologiaSeleccionada == '2'):
#             #llamar funcion especifica para arbol
#             _cargaDeParametrosArbol()
#         elif (topologiaSeleccionada == '3'):
#             #llamar funcion especifica

#         elif (topologiaSeleccionada == '4'):
#             #llamar funcion especifica


# def _cargaDeParametrosLinear()

# def _cargaDeParametrosArbol()

# def _cargaDeParametros3()

# def _cargaDeParametros4()


