import sys
import os
import json


#datos de topologia
switches = {}
hosts = {}
servers = {}
dpids = {} # datapah id de switches


def imprimirMenu():
    print('Seeccione la topologia que desea utilizar')
    print('1) Linear topology')
    print('2) Tree topology')
    print('3) Exit')


def validarIngreso():
    bien = False
    while not bien:
        try:
            num = int(input('Ingresar un numero entero: '))
            bien = True
        except ValueError:
            print('Error, ingresar un numero entero')
    return num


def _cargaDeParametrosLinear():
    pass

def _cargaDeParametrosArbol():
    pass

def _cargaDeParametros3():
    pass

def _cargaDeParametros4():
    pass


def import_jsonTopo(filename):
    global switches
    global hostsswitches
    global servers

    filejson = open(filename)
    topojson = json.load(filejson)

    switches = topojson['switches']
    hosts = topojson['hosts']
    servers = topojson['servidores']
    dpids = topojson['dpids']


def printDic(diccionario):
    for grupo, g_info in diccionario.items():
        print("\nGrupo Multicast:", grupo)

        for key in g_info:
            print(key + ':', g_info[key])


def obtenerPuertos(gruposM, direccionM, switch_id):
    aux = []
    for grupo, g_info in gruposM.items():
        if direccionM == grupo:
            #g_info = direccionM[grupo] #toma diccionarios de cada switch en el grupo multicast
            for s_id, s_info in g_info.items():
                if s_id == switch_id:
                    print(s_id)
                    for port, value in enumerate(s_info):
                        aux.append(port+1)
                        print('Puerto: {}, Estado: {}.'.format(port+1, value))

    return aux


def main():

    ok = True
    while ok:

        imprimirMenu()
        opcion = validarIngreso()

        if opcion == 1:
            print('Linear topology')
            _cargaDeParametrosLinear()
        elif opcion == 2:
            print('Tree topology')
            _cargaDeParametrosArbol()
        elif opcion == 3:
            print('game over')
            ok = False
        else:
            print('Ingrese una opcion valida')


if __name__ == '__main__':
    main()
