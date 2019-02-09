# Parejas de clave:valor.
# La clave no puede cambiar, es inmutable

diccionario1 = {'clave1':'valor1', 'clave2':'valor2','clave3':'valor3'}

#funciones utiles:
diccionario1.items()
diccionario1.keys()
diccionario1.values()

if 'clave1' in diccionario1:
    print "barbaro"

if (diccionario1.get('clave1',0)==0):
    print "No hay calve 1"

# elif print "hay clave 1"


#Como instanciar un diccionario
diccionario2_keys = range(10) #array de 0 a 9
diccionario2_values = list('abcdefghij') #10 letras del abecedario

#funcion dict para instanciar
#funcion zip que crea una tupla con las dos listas
diccionario2=dict(zip(diccionario2_keys,diccionario2_values))

print(diccionario2[4])
diccionario2[4]='RRRR'
print(diccionario2[4])

#borrar elementos de un diccionario1
del diccionario2[4]

#largo del diccionario
len(diccionario2)

#funcion para chequear si una key existe dentro de un diccionario1
print diccionario1.get('clave90',0) #devuelve 0 (o lo que le ponga) si la key no existe




#funcion para setear valor a keys que pueden no existir
diccionario1.setdefault('clave4',50)
diccionario1.setdefault('clave3',10)
print diccionario1.items()


#NESTED DICCIONARIES - DICCIONARIOS ANIDADOS
fecha1 = '2019/01/14'
fecha2 = '2019/01/10'
dict3 = {fecha1:{'asistente1':'lucas','asistente2':'bruno'},
         fecha2:{'asistente1':'nadie'}}

print dict3.items()
print dict3[fecha2]['asistente1']



personas = {'persona1': {'nombre':'pepe', 'apellido':'gonzalez', 'edad':'90'},
            'persona2': {'nombre':'pepe2', 'apellido':'gonzalez2', 'edad':'902'}}

print personas.items()

print "\n"


print personas.keys()

print "\n"

print personas.values()

print "\n"

print personas['persona2'].values()

if personas['persona1']['edad']=='90':
    print 'toy barbaro dio 90'


if personas['persona1']['nombre']=='pepe':
    print 'vamo pepe'
