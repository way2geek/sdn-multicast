import time
import datetime


ts=time.time()
st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
print st
# time.sleep(3)


def loggear_arbol_multicast(texto):
    file_arboles = open("arboles_multicast.txt","a+")
    file_arboles.write(texto)
    file_arboles.close()


loggear_arbol_multicast(st+" - "+"\nprueba1 hola como va")

# loggear_arbol_multicast(st+" - "+"\t*3prueba1")
# puertos =["hola", "5", "pepe"]
# print puertos
# print (', ' . join(puertos))

# puertos= (', ' . join(puertos))
# print ("nuevos puertos = "+str(puertos))

puertos =[10, 5,6,8]

print puertos
print ("nuevos puertos = "+str(puertos))

string = str(puertos)
string = string.replace("["," ")
string = string.replace("]"," ")
print string
