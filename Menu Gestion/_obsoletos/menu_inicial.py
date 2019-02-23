#!/usr/bin/python3

import sys
import os


def pedirNumeroEntero():

    correcto=False
    num=0
    while(not correcto):
        try:
            num = int(input("Introduce un numero entero: "))
            correcto=True
        except ValueError:
            print('Error, introduce un numero entero')

    return num


def imprimirMenu():
	print ("1. Opcion 1")
	print ("2. Opcion 2")
	print ("3. Opcion 3")
	print ("4. Salir")

	print ("Elige una opcion")


#def _cargaDeParametros(topologiaSeleccionada):
#    switch (topologiaSeleccionada):
#        if (topologiaSeleccionada == '1'):
#            #llamar funcion especifica para lineal
#            _cargaDeParametrosLinear()

#        elif (topologiaSeleccionada == '2'):
            #llamar funcion especifica para arbol
#            _cargaDeParametrosArbol()
#        elif (topologiaSeleccionada == '3'):
            #llamar funcion especifica

#        elif (topologiaSeleccionada == '4'):
            #llamar funcion especifica


def _cargaDeParametrosLinear():
    pass

def _cargaDeParametrosArbol():
    pass

def _cargaDeParametros3():
    pass

def _cargaDeParametros4():
    pass


if __name__ == '__main__':

    salir = False
    opcion = 0

    while not salir:

	    imprimirMenu()

        opcion = pedirNumeroEntero()

	    if opcion == 1:
	        print ("Opcion 1")
	    elif opcion == 2:
	        print ("Opcion 2")
	    elif opcion == 3:
	        print("Opcion 3")
	    elif opcion == 4:
	        salir = True
	    else:
	        print ("Introduce un numero entre 1 y 3")

	print ("Fin")
