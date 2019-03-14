
#def printDic(diccionario):
#    for grupo, g_info in diccionario.items():
#        print("\nGrupo Multicast:", grupo)

#        for key in g_info:
#            print(key + ':', g_info[key])

#printDic(gruposM)

print('\n')

grupos = {
    12:{
        '225.0.0.1':{
                    'replied':True,
                    'leave':False,
                    'ports':{
                            3:{
                               'out':True,
                               'in':False
                              },
                            2:{
                               'out':False,
                               'in':True
                               },
                            1:{
                               'out':True,
                               'in':False
                              }
                            }
                    }
       },
      13:{
          '225.0.0.5':{
                      'replied':True,
                      'leave':False,
                      'ports':{
                              1:{
                                 'out':True,
                                 'in':False
                                }
                              }
                      }
         }
}


def getDicPorts(grupos, dst, datapath):
    ports = {}
    puertosOut = []
    puertosIn = []
    for dp, g_info in grupos.items():
        if dp == datapath:
            print(dp)
            for destino, d_info in g_info.items():
                print(destino)
                if destino == dst:
                    ports = d_info['ports']
                else:
                    print('NO SE ENCUENTRA EL GRUPO REGISTRADO')
    return ports


def puertos_IN_OUT(grupos):
    puertosIN = []
    puertosOUT = []
    puertos = getDicPorts(grupos, '225.0.0.1', 12)
    for puerto, p_info in puertos.items():
        print(p_info)
        if p_info['out'] == True:
            puertosOUT.append(puerto)
        #elif p_info['in'] ==True:
        #    puertosIN.append(puerto)
    print(puertosOUT)


#puertos = getDicPorts(grupos, '225.0.0.34', 12)

puertos_IN_OUT(grupos)
