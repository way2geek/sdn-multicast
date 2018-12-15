
#defino funcion
def funcion_nombre():
    nombre = raw_input('Ingresa tu nombre: ')
    apellido = raw_input('Ingresa tu apellido: ')

    print 'Tu nombre completo es {} {}'.format(nombre,apellido)

    print 'Tu nombre tiene {} caracteres'.format(len(nombre))
    print 'Tu apellido tiene {} caracteres'.format(len(apellido))
    return  #en realidad no devuelve nada
#fin de la funcion

#llamado a funcion
funcion_nombre()
