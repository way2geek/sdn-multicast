listaok=[3]
set(listaok)
print (listaok)

listamal = 3
listamal2 = 5
print(type(listamal))
print(type(listamal2))
# set(listamal)  # <--aca fallaria

        # Resolucion:

# 1- casteo int a str
listok1 = str(listamal)
listok2 = str(listamal2)
# 2- casteo lista a set (simplemente elimina duplicados)
set1 = set(listok1)
set2 = set(listok2)
print (set1)
print (set2)
# resto sets, resultado da tipo set
valores_de_1_que_no_tiene_2 = set1 - set2
print (valores_de_1_que_no_tiene_2)
print (type (valores_de_1_que_no_tiene_2))
# 3- casteo set a lista
final = list(valores_de_1_que_no_tiene_2)
print (final)
print (type(final))