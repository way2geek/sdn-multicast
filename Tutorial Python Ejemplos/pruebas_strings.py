string_prueba = 'abcdefghijklmnopqrstuvwxyz'
print string_prueba

recorte_inicial = string_prueba[0:10]
print recorte_inicial

recorte_final = string_prueba[11:]
print recorte_final

recorte_parcial = string_prueba[3:15]
print recorte_parcial

#Recorrer string en intervalos dados desde una posicion hasta otra
intercalado = string_prueba[2:18:2]
# intercalado = string_prueba[2::2] #sin especificar el final
# intercalado = string_prueba[18:2:-1] #recorrida en modo inverso
print intercalado


#Funciones sobre Strings

#Largo de un string
largo = len(string_prueba)
print largo

#Pasar a Mayuscula
mayus = string_prueba.upper()
print mayus
#Pasar a Minuscula
minus = mayus.lower()
print minus

#Split de informacion segun criterio (parseo)
frase = 'hola esta es una frase que voy a aplicar split'
print frase
frase_split = frase.split()
print frase_split

frase2 = 'esto*esta*todo*junto*necesito*separarlo'
print frase2
frase_sin_aster = frase2.split('*')
print frase_sin_aster

#Contar cantidad de caracteres dentro de un string_prueba
letras_e = frase.count('e')
print letras_e

#Encontrar cadena de caracteres en un string_prueba
posicion_palabra_hola = frase.find('hola')
print posicion_palabra_hola

#Encontrar ultima ocurrencia de una cadena de caracteres
frase3 = 'una vez habia una vez una vez vez una una vez'
print frase3.rfind('una')
