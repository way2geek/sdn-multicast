linea = "cookie=0x0, duration=352.407s, table=0, n_packets=27, n_bytes=2346, priority=10,in_port=s1-eth2 actions=group:50"
cookie, duracion, tabla, paquetes, bytes, prioridad, in_port_and_action= linea.split(",")
in_port, accion = in_port_and_action.split(" ")

cookie = cookie.split("=")[1]
duracion = duracion.split("=")[1]
tabla = tabla.split("=")[1]
paquetes = paquetes.split("=")[1]
bytes = bytes.split("=")[1]
prioridad = prioridad.split("=")[1]
in_port = in_port.split("=")[1]
accion = accion.split("=")[1]

print cookie
print duracion
print tabla
print paquetes
print bytes
print prioridad
print in_port
print accion
