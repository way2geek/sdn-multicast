def obtener_lista_sin_duplicados(una_lista):
    lista_depurada = []
    lista_repetidos = []

    return lista_depurada

def diferencia_arrays(ar1, ar2):
        en1_no2=[]
        elemento_a1_esta_en_ar2 = False

        for elemento_a1 in ar1:
            for elemento_a2 in ar2:
                if(elemento_a1 == elemento_a2):
                    elemento_no_esta_en_2 = True
                    break
                else:
                    if(elemento_a1 not in en1_no2):
                        en1_no2.append(elemento_a1)
                    else:
                        pass
        return en1_no2

lista1 = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

lista2 = [8, 9, 10, 11, 12]

print(diferencia_arrays(lista1, lista2))
