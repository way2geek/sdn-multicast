import sys
import os


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


def main():

    ok = True
    while ok:

        imprimirMenu()
        opcion = validarIngreso()

        if opcion == 1:
            print('Linear topology')
        elif opcion == 2:
            print('Tree topology')
        elif opcion == 3:
            print('game over')
            ok = False
        else:
            print('Ingrese una opcion valida')

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


if __name__ == '__main__':
    main()
