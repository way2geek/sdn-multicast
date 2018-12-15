unaLista = ['uno','dos','tres','cuatro','cinco']

print '\n Imprimo...\n'
print unaLista[0]
print unaLista[1]
print unaLista[2]
print unaLista[3]
print unaLista[4]
# unaLista[5] este ya da un error de "out of range"

#replace
unaLista[3]='nueve'
print unaLista
#otro ejemplo
stringPrueba='Habia una vez una cosa que tenia otra cosa y hacia una cosa impresionante. Que cosa mas rara'
print stringPrueba
stringPrueba= stringPrueba.replace('cosa','pelota')
print stringPrueba

#append
unaLista.append('pepito')
print unaLista

#insert
unaLista.insert(3,'insertado')
print unaLista

#remove
del unaLista[2]
print unaLista

#otra forma
unaLista.remove('uno')
print unaLista
