import sys
import os


opcion = -1

def _imprimrMenu():

  print("- - \tMENU PRINCIPAL\t - - \n");
  print("Seleccione la topologia deseada o ingrese 0 para salir:\n");

  print("\t1) Topologia linear.\n");
  print("\t2) Topologia de arbol.\n");
  print("\t3) Tolologia    \n");
  print("\t4) Topologia    \n");

def _cargaDeParametros(topologiaSeleccionada):
    switch (topologiaSeleccionada):
        if (topologiaSeleccionada == '1'):
            #llamar funcion especifica para lineal
            _cargaDeParametrosLinear()

        elif (topologiaSeleccionada == '2'):
            #llamar funcion especifica para arbol
            cargaDeParametrosArbol()
        elif (topologiaSeleccionada == '3'):
            #llamar funcion especifica

        elif (topologiaSeleccionada == '4'):
            #llamar funcion especifica


def _cargaDeParametrosLinear()

def _cargaDeParametrosArbol()

def _cargaDeParametros3()

def _cargaDeParametros4()

def _leerIngreso()


if __name__ == '__main__':
    opcion = -1

    while opcion != 0:
        imprimirMenu();
        print("Seleccione una opcion.")
        # opcion = leerIngreso();
        opcion =1 #para probarlo
        if opcion == '1'
            print ('Seleccioné opcion Linear')
        elif opcion == '2'
            print ('Seleccioné opcion Arbol')
        elif opcion =='3'
            print ('Seleccion opcion 3')

        else:
            print('Ingreso invalido.')
