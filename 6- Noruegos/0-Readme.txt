Pasos para probarlo:

1) Correr una topologia dada.
  Puede usarse net.py para que lea una topologia en formato json desde
  la carpeta /topo en este mismo directorio.

2) Correr controlador:
        ryu-manager ryu.app.simple_switch_13 ryu.app.ofctl_rest

3) Correr app.py


Requisitos: revisar que se use 127.0.0.:8080 como interfaz de API
