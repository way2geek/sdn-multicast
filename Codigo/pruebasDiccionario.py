
gruposM = {
    '225.0.30.2':
                {'s1':[True, False, True],
                 's2':[False, True, True]
    },
    '225.0.31.2':
                {'s1':[True, True, False],
                 's2':[False, False, True]

    }
}

def printDic(diccionario):
    for grupo, g_info in diccionario.items():
        print("\nGrupo Multicast:", grupo)

        for key in g_info:
            print(key + ':', g_info[key])

printDic(gruposM)

print('\n')

def obtenerPuertos(gruposM, direccionM, switch_id):
    aux = []
    for grupo, g_info in gruposM.items():
        if direccionM == grupo:
            #g_info = direccionM[grupo] #toma diccionarios de cada switch en el grupo multicast
            for s_id, s_info in g_info.items():
                if s_id == switch_id:
                    print(s_id)
                    for port, value in enumerate(s_info):
                        print('Puerto: {}, Estado: {}.'.format(port+1, value))



obtenerPuertos(gruposM, '225.0.30.2', 's1')
