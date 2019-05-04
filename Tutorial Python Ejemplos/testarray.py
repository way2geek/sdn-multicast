array1=['1','2','3']

array2=['11','12','13']

array3=['21','22','23']

arraycompleto=array2
print arraycompleto
arraycompleto=arraycompleto+array1
print arraycompleto

arraycompleto2=array2
# arraycompleto2.append(array1)
# print arraycompleto2
arraycompleto.extend(array3)
print arraycompleto
