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
