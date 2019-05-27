import sys

print("Start...")

print ("Cantidad de argumentos:{}".format(len(sys.argv)))
print ("Listado de argumentos:{}".format(str(sys.argv)))

print("LISTADO HACIA ABAJO:")
for elem in (sys.argv):
    print(elem)

print("Finish...")