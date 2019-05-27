def obtener_lista_sin_duplicados(una_lista):
    lista_depurada = []
    lista_repetidos = []
    indice_aux = 1
    depu_y_repe = []
    for elemento in una_lista:
        if(elemento in una_lista[indice_aux:len(una_lista)]):
            lista_repetidos.append(elemento)
        else:
            lista_depurada.append(elemento)
        indice_aux = indice_aux +1
    print("DEPURADA =")
    print(lista_depurada)

    print ("REPETIDOS =")
    print(lista_repetidos)
    depu_y_repe.append(lista_depurada)
    depu_y_repe.append(lista_repetidos)
    print (depu_y_repe[0])
    print (depu_y_repe[1])
    return depu_y_repe

def diferencia_arrays(ar1, ar2):
    en1_no2=[]
    for elemento_a1 in ar1:
        if (elemento_a1 in ar2):
            print ("Elemento {} estaba en ar2".format(elemento_a1))
        else:
            print ("Elemento {} no estaba en ar2".format(elemento_a1))
            en1_no2.extend(elemento_a1)
    return en1_no2

lista1 = [4, 1, 2, 3, 4, "a", 5, 6, 6, 7, 8, 9, 10, "a", "v"]
lista2 = [8, 9, 10, 11, 12]

obtener_lista_sin_duplicados(lista1)
