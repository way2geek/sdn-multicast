Pasos para probarlo:

1) Correr una topologia dada.
  Puede usarse net.py para que lea una topologia en formato json desde
  la carpeta /topo en este mismo directorio.

2) Correr controlador:
        ryu-manager ryu.app.simple_switch_13 ryu.app.ofctl_rest

3) Correr app.py


Requisitos: revisar que se use 127.0.0.:8080 como interfaz de API

Shortes paths:

sp[s1]: {u's8': u's7', u's3': u's2', u's2': u's1', u's1': None, u's7': u's6', u's6': u's5', u's5': u's1', u's4': u's3'}
sp[s2]: {u's8': u's7', u's3': u's2', u's2': None, u's1': u's2', u's7': u's6', u's6': u's5', u's5': u's1', u's4': u's3'}
sp[s3]: {u's8': u's7', u's3': None, u's2': u's3', u's1': u's2', u's7': u's6', u's6': u's5', u's5': u's1', u's4': u's3'}
sp[s4]: {u's8': u's7', u's3': u's4', u's2': u's3', u's1': u's2', u's7': u's6', u's6': u's5', u's5': u's1', u's4': None}
sp[s5]: {u's8': u's7', u's3': u's2', u's2': u's1', u's1': u's5', u's7': u's6', u's6': u's5', u's5': None, u's4': u's3'}
sp[s6]: {u's8': u's7', u's3': u's2', u's2': u's1', u's1': u's5', u's7': u's6', u's6': None, u's5': u's6', u's4': u's3'}
sp[s7]: {u's8': u's7', u's3': u's2', u's2': u's1', u's1': u's5', u's7': None, u's6': u's7', u's5': u's6', u's4': u's3'}
sp[s8]: {u's8': None, u's3': u's2', u's2': u's1', u's1': u's5', u's7': u's8', u's6': u's7', u's5': u's6', u's4': u's3'}
