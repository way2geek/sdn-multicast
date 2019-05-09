array1=['1','2','3']

array2=['11','12','13','3']

array3=['21','22','23']

arraycompleto=array2
print arraycompleto
arraycompleto=arraycompleto+array1
print arraycompleto

arraycompleto2=array2
# arraycompleto2.append(array1)
# print arraycompleto2

print "prueba extend"
arraycompleto.extend(array3)
print arraycompleto
arraycompleto.extend(array3)
arraycompleto.extend(array3)
arraycompleto.extend(array3)
print arraycompleto

# if array1 in array2:
#     print"ARRAY 1 en ARRAY 2"
# else:
#     print "ARRAY 1 NO en ARRAY 2"


# def unValorDeArrayEnOtro(arrayA, arrayB):
#     retorno = False
#     for valor in arrayA:
#         if(valor in arrayB):
#             retorno = True
#         else:
#             retorno = False
#     return retorno
#
# ret=unArrayEnOtro(array1, array2)
# print ret



def arraysSonIguales(arrayA, arrayB):
    retorno = True
    if(len(arrayA)==0 and len(arrayB)==0):
        retorno = False
    for valor in arrayA:
        if(valor not in arrayB):
            retorno = False
    return retorno

array10=['1','2','3']
ret2=arraysSonIguales(array1, array10)
print ret2

a=[]
b=[]
ret3 =arraysSonIguales(a,b)
print ret3
ret4=arraysSonIguales(array1, array10)
print ret4


cortito=[]
# print len(cortito)



car = {
  "brand": "Ford",
  "model": "Mustang",
  "year": 1964
}

car.update({"color": "White"})

print(car)


print "array"
arrayXX =array1
print arrayXX

arrayXX.append(array2)
arrayXX.append(array2)
arrayXX.append(array2)
arrayXX.append(array2)
print arrayXX

array_puertos0 = ["puerto 2", "puerto 1", "puerto 3","hola"]
array_puertos = ["puerto 1", "puerto 2", "puerto 3","baba"]
array_puertos2 = ["puerto 3", "puerto 4"]
# array_puertos.extend(array_puertos2)
# print "RESULT="
# print array_puertos

# print "resta"
array_resta=list(set(array_puertos) - set(array_puertos2))
# print (array_resta)

#Compara 2 arrays y devuelve True si
#son iguales o False si son diferentes
#no importa el orden de los elementos
def arrays_iguales(ar1, ar2):
    ret = False
    array_resta=list(set(ar1) - set(ar2))
    if(len(array_resta)==0):
        ret = True
    return ret

# Devuelve un array con los elementos
#que estan en ar1 pero no estan en ar2
def diferencia_arrays(ar1, ar2):
    result=[]
    result=list(set(ar1) - set(ar2))
    return result

print "FUNCIONNNN"
print arrays_iguales(array_puertos,array_puertos0)
print "diferenciaaa"
print diferencia_arrays(array_puertos,array_puertos0)

print "palo"
print diferencia_arrays(['A'],["1","2","3"])
