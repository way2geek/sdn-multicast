import sys
import os
import subprocess
import time

def mostrarAyuda():
    print("-AYUDA-")

    print("\t1- Topologia linear pequena:")
    print("\t\t Se trata de una topologia con 2 switches interconectados.")
    print("\t\t Cada switch tiene 5 hosts conectados.")
    # imprimir_topo_linear_peq()

    print("\t2- Topologia linear grande.")
    print("\t\t Se trata de una topologia con 10 switches en linea.")
    print("\t\t Cada switch tiene 2 hosts conectados.")
    # imprimir_topo_linear_gra()

    print("\t3- Topologia arbol con 3 ramificiaciones.")
    print("\t\t Se trata de una topologia que representa un arbol de tres ramificaciones.")
    print("\t\t Se compone de 4 switches y cada switch tiene 3 hosts conectados.")
    # imprimir_topo_arbol_3_ram()

    print("\t4- Topologia arbol con 3 niveles de profundidad.")
    print("\t\t Se trata de una topologia de arbol con 3 niveles de profundidad.")
    print("\t\t Se compone de 15 switches y cada switch tiene 1 host conectado.")
    # imprimir_topo_arbol_profunda()

    print("\t5- Topologia anillo simple.")
    print("\t\t Se trata de una topologia de 4 switches conectados en forma de anillo.")
    print("\t\t Cada switch cuenta con 2 hosts conectados.")
    # imprimir_topo_anillo_simple()

    print("\t6- Topologia arbol con anillos.")
    print("\t\t Similar a topologia 4 pero agregando enlaces nuevos en los niveles superiores del arbol.")
    print("\t\t Cada enlace nuevo, forma un anillo dentro del arbol.")
    print("\t\t Cada switch cuenta con 1 host conectado.")
    # imprimir_topo_arbol_con_anillos()

    print("\t7- Topologia full mesh simple.")
    print("\t\t Similar a topologia 5 pero agregando enlaces que interconectan todos los switches.")
    print("\t\t Cada switch cuenta con 2 hosts conectados.")
    # imprimir_topo_full_mesh_simple()

    print("\t8- Topologia full mesh compleja.")
    print("\t\t Se trata de una topologia de 8 switches con interconexion directa entre todos ellos.")
    print("\t\t Cada switch cuenta con 2 hosts conectados.")
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
    print("- - MENU PRINCIPAL - -")
    print("Seleccione la opción deseada o ingrese 0 para salir")
    print("\t1- Topologia linear pequena.")
    print("\t2- Topologia linear grande.")
    print("\t3- Tolologia arbol con 3 ramificiaciones.")
    print("\t4- Topologia arbol con 3 niveles de profundidad.")
    print("\t5- Topologia anillo simple.")
    print("\t6- Topologia arbol con anillos.")
    print("\t7- Topologia full mesh simple.")
    print("\t8- Topologia full mesh compleja.")
    print("\t9- Ver ayuda.")
    print("\t0- Salir.")
    pass

def cerrar_programa():
    print("Cerrando programa")
    time.sleep(0.5)
    print("Cerrando programa.")
    print("Cerrando programa..")
    print("Cerrando programa...")
    time.sleep(0.5)
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

def ejec_app_crea_json(una_opcion):
    if(una_opcion == 1):
        os.system("python app_crea_json.py topologias/topo_linear_pequena.json")
    elif(una_opcion == 2):
        os.system("python app_crea_json.py topologias/topo_linear_grande.json")
    elif(una_opcion == 3):
        os.system("python app_crea_json.py topologias/topo_arbol_3_ramas.json")
    elif(una_opcion == 4):
        os.system("python app_crea_json.py topologias/topo_arbol_profundo.json")
    elif(una_opcion == 5):
        os.system("python app_crea_json.py topologias/topo_anillo_simple.json")
    elif(una_opcion == 6):
        os.system("python app_crea_json.py topologias/topo_arbol_con_anillos.json")
    elif(una_opcion == 7):
        os.system("python app_crea_json.py topologias/topo_full_mesh_simple.json")
    elif(una_opcion == 8):
        os.system("python app_crea_json.py topologias/topo_full_mesh_compleja.json")
    else:
        print("ERROR: No fue una opcion valida")
        pass


def ejec_leer_topo_json(una_opcion):
    if(una_opcion == 1):
        os.system("python leer_topo_json.py topologias/topo_linear_pequena.json")
    elif(una_opcion == 2):
        os.system("python leer_topo_json.py topologias/topo_linear_grande.json")
    elif(una_opcion == 3):
        os.system("python leer_topo_json.py topologias/topo_arbol_3_ramas.json")
    elif(una_opcion == 4):
        os.system("python leer_topo_json.py topologias/topo_arbol_profundo.json")
    elif(una_opcion == 5):
        os.system("python leer_topo_json.py topologias/topo_anillo_simple.json")
    elif(una_opcion == 6):
        os.system("python leer_topo_json.py topologias/topo_arbol_con_anillos.json")
    elif(una_opcion == 7):
        os.system("python leer_topo_json.py topologias/topo_full_mesh_simple.json")
    elif(una_opcion == 8):
        os.system("python leer_topo_json.py topologias/topo_full_mesh_compleja.json")
    else:
        print("ERROR: No fue una opcion valida")
        pass

#Funcion que unifica las funciones
# ejec_app_crea_json y
# ejec_leer_topo_json
def crear_json_y_correr_topo(una_op):
    print("Creando app json...")
    ejec_app_crea_json(una_op)
    time.sleep(2)
    print("Creando simulacion Mininet...")
    ejec_leer_topo_json(una_op)

def ejec_controller():
    pass
def cerrar_mininet():
    print("Debug: Cerrando Mininet...")
    os.system("mn -c")
    print("Debug: Mininet finalizado.")
# LLAMADOS

opcion = -1
while (opcion != 0):
    imprimirMenu()
    #kill Mininet
    # cerrar_mininet()
    print("Seleccione una opcion.")
    opcion = leerIngreso()
    # print("DEBUG: OPCION INGRESADA: {}".format(opcion))
    if (opcion == 1):
        # print ('DEBUG Seleccion opcion 1')
        crear_json_y_correr_topo(1)
    elif (opcion == 2):
        # print ('Debug Seleccion opcion 2')
        crear_json_y_correr_topo(2)
    elif (opcion ==3):
        # print ('Debug Seleccion opcion 3')
        crear_json_y_correr_topo(3)
    elif (opcion ==4):
        # print ('Debug Seleccion opcion 4')
        crear_json_y_correr_topo(4)
    elif (opcion ==5):
        # print ('Debug Seleccion opcion 5')
        crear_json_y_correr_topo(5)
    elif (opcion ==6):
        # print ('Debug Seleccion opcion 6')
        crear_json_y_correr_topo(6)
    elif (opcion ==7):
        # print ('Debug Seleccion opcion 7')
        crear_json_y_correr_topo(7)
    elif (opcion ==8):
        # print ('Debug Seleccion opcion 8')
        crear_json_y_correr_topo(8)
    elif (opcion ==9):
        mostrarAyuda()
    elif (opcion ==0):
        cerrar_programa()
    else:
        print('Ingreso invalido.')
