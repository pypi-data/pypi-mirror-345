print('Módulo: ESTRUCTURA\nEste modulo contiene las funciones que permiten modificar la estructura del flujo de procesos. Así mismo, contiene las funciones que modifican la Tabla Maestra.')

import networkx as nx
import pandas as pd

from A_TRANSVERSAL import dataset_id,mastertable,project # Se cargan objetos fijos relevantes
from A_TRANSVERSAL import charge_serv,create_schema,create_table,fechas_relevantes,multiple_query,timer,upload_table,simple_query_sender # Se cargan funciones relevantes
from datetime import datetime

# Requeridos: networkx, pandas, datetime

# Lo que va en __init__.py es lo siguiente:
# De este script solo se debe permitir el uso de los objetos: grafo inicial
# De este script solo se debe permitir el uso de las funciones: ejecutor_estructura, cargador_estructura

def creador_grafo(nodos:list,enlaces:list):
    '''
    Esta función creará un onjeto tipo grafo dirigido de NetworkX que representa la estructura del flujo de procesos. 
    Recibe dos listados: nodos y enlaces.
    inputs:
        nodos: listado que contiene str que representan los ids de los procesos (i.e. los nodos)
        enlaces: listado que contiene tuplas (A,B) que representan los enlaces que existen entre nodos. Aquí, la primera
        entrada es el nodo out del enlace y la segunda el nodo in del enlace (i.e. el enlace sale de A y apunta a B).
    output:
        Grafo dirigido de NetworkX que representa la estructura del flujo de procesos. 
    '''
    nodos_en_enlaces = True
    if any([(e[0] not in nodos)|(e[1] not in nodos) for e in enlaces]):
        nodos_en_enlaces = False
    if nodos_en_enlaces==False: # Revisa que los nodos en los enlaces sean nodos del grafo.
        raise Exception('Nodos no coinciden con los que están en los enlaces. Ingrese inputs correctos.')
    if nodos_en_enlaces:
        grafo = nx.DiGraph()
        grafo.add_nodes_from(nodos)
        grafo.add_edges_from(enlaces)
        return grafo
    else:
        raise Exception('Nodos no coinciden con los que están en los enlaces. Ingrese inputs correctos.')
    
def creador_matriz(grafo:nx.DiGraph):
    '''
    Esta función crea la matriz que representa la tabla maestra del flujo de procesos. Devuelve un pd.DataFrame
    input:
        grafo: nx.DiGraph que representa el flujo de procesos.
    output:
        pd.DataFrame que contiene una fila, de bool o timestamp, que representa la tabla maestra.
    '''
    fecha = datetime.strptime(fechas_relevantes('PAN')['f_corte'],'%Y-%m-%d')
    diccionario = {'FECHA':[fecha]}|{i:[False] for i in grafo.nodes}
    return pd.DataFrame(diccionario)

def creador_estructura_condicionales(grafo:nx.DiGraph,nube_local:str='nube'):
    '''
    Esta función crea la estructura de condicionales dado un grafo dirigido de NetworkX que representa el flujo de procesos. 
    Luego, hace el print de dicha estructura para poderla copiar y poner en el respectivo archivo donde se va a montar.
    input:
        grafo: nx.DiGraph que representa el flujo de procesos.
    output:
        None
    '''
    nodos = grafo.nodes
    print('-'*30+'\n','A continuación se hace el print de la estructura de condicionales:\n\n')
    condicional = 'if '
    if nube_local == 'nube':
        for i in nodos:
            predecesores = list(grafo.predecessors(i))
            len_predecesores = len(predecesores)
            if len_predecesores>0:
                string0 = condicional+' & '.join(["(Checker['{}'])".format(k) for k in predecesores])+" & (not Checker['{}']):".format(i)
                string1 = "\n\tChecker['{}']=True".format(i)
                print(string0,string1)
                condicional = 'elif '
    elif nube_local == 'local':
        for i in nodos:
            predecesores = list(grafo.predecessors(i))
            len_predecesores = len(predecesores)
            if len_predecesores==0:
                print("\n(Checker['{}'])".format(i))
    print('\n\n'+'-'*30)

def ejecutor_estructura(nodos:list,enlaces:list):
    '''
    Esta función toma un listado de nodos y enlaces, que conformarán un grafo, y retorna la estructura de grafo en
    networkx, así como un pd.DataFrame que será la tabla maestra inicializada. Además imprime la estructura de condicionales
    que dado el grafo modela el flujo de tareas y cuando se deberían ejecutar. 
    inputs:
        nodos: listado que contiene str que representan los ids de los procesos (i.e. los nodos)
        enlaces: listado que contiene tuplas (A,B) que representan los enlaces que existen entre nodos. Aquí, la primera
        entrada es el nodo out del enlace y la segunda el nodo in del enlace (i.e. el enlace sale de A y apunta a B).
    outputs:
        grafo: Grafo dirigido de NetworkX que representa la estructura del flujo de procesos.
        matriz: pd.DataFrame que contiene una fila, de bool o timestamp, que representa la tabla maestra.
    '''
    grafo = creador_grafo(nodos=nodos,enlaces=enlaces)
    matriz = creador_matriz(grafo)
    creador_estructura_condicionales(grafo)
    return grafo,matriz

def cargador_estructura(matriz,where_to_run:str='cloud_run',job_type:str='update'):
    '''
    Esta función recibe un pd.DataFrame que es consistente con la estructura de Tabla Maestra y crea una tabla de BigQuery
    que representa dicha tabla. Si la tabla ya está creada, entonces la elimina y crea una nueva consistente con la 
    estructura del pd.DataFrame.
    inputs:
        matriz: pd.DataFrame consistente con la estructura de tabla maestra creada a partir de un grafo de flujo de tareas. 
        where_to_run: str que dice en que caso de la función charge_serv del módulo A_TRANSVERSAL se crea el client
        de BigQuery.
        job_type: str que dice si se va a hacer un cargue de un nuevo registro o se va a modificar el registro sobre el que
        se trabaja en el día. Puede tomar dos valores: 'create' y 'update'. 
    output:
        None 
        '''
    variables = list(matriz.columns) # Se obtienen las variables de la tabla
    #from A_TRANSVERSAL import project, dataset_id # Use solo cuando haga pruebas
    #where_to_run = 'local' # Use solo cuando haga pruebas
    client = charge_serv(where_to_run=where_to_run,
                        project=project,
                        dataset_id=dataset_id,
                        tables_names=[])[0] # Se obtiene el cliente
    big_query_table_ref = '.'.join([project,dataset_id,mastertable]) # Se obtiene el id de la tabla
    schema = create_schema({j:({'type':'BOOL','mode':'REQUIRED'} if j!= "FECHA" else {'type':'DATETIME','mode':'REQUIRED'}) for j in variables}) # Se crea el esquema
    if job_type == 'create':
        create_table(client=client,
                    big_query_table_ref=big_query_table_ref,
                    table_to_append=matriz,
                    schema=schema)
    elif job_type == 'update':
        for d in list(matriz['FECHA']):
            print(d)
            d = datetime.strftime(d,"%Y-%m-%d")
            query = f"DELETE FROM `{big_query_table_ref}` WHERE FECHA = DATE('{d}')"
            simple_query_sender(client,query)
        upload_table(client,big_query_table_ref,matriz,schema)
    else:
        raise Exception('No se ha elegido un tipo correcto de job_type')

def obtencion_tabla_maestra(fecha:str=None,where_to_run:str='cloud_run'):
    '''
    Esta función llama a la tabla maestra, en el día que se le indique. No confundir con la función obtener_registro_actual,
    pues esta está diseñada para crear el registro del día si no extiste o para cargarlo en caso contrario.
    inputs:
        fecha: str que indica en el formato %Y-%m-%d el día a consultar. Si es None, 
        se toma el último día creado en la tabla maestra de BigQuery.
        where_to_run: str que dice en que caso de la función charge_serv del módulo A_TRANSVERSAL 
        se crea el client de BigQuery.
    output:
        pd.Series que contiene la sección de la tabla maestra que se quiere obtener del día especificado.'''
    big_query_table_ref = '.'.join([project,dataset_id,mastertable]) # Se obtiene el id de la tabla
    query = f"SELECT * FROM `{big_query_table_ref}` WHERE FECHA = "
    if fecha is None:
        query = query+f"(SELECT MAX(FECHA) FROM `{big_query_table_ref}`)"
    else:
        query = query+f'DATE("{fecha}")'
    client = charge_serv(where_to_run=where_to_run,
                        project=project,
                        dataset_id=dataset_id,
                        tables_names=[])[0] # Se obtiene el cliente # Se obtiene el cliente y la referencia del dataset
    tabla_maestra = multiple_query(client=client,query_list=[query])[0] # Se obtiene la única base de datos que representa el mastertable
    return tabla_maestra.iloc[0,:]

def modificacion_tabla_maestra(Checker:pd.Series,list_to_true:list = []):
    '''
    Esta función recibe el checker y actualiza las entradas que se requieren a True. Práctico para hacer actualizaciones
    rápidas y concisas.
    inputs:
        Checker: pd.DataSeries que contiene la sección de la tabla maestra que se quiere obtener del día especificado.
        En general será el output de la función obtencion_tabla_maestra.
        list_to_true: list que contiene str correspondientes a los nombres de las variables de la tabla maestra que 
        serán True.
    output:
        pd.Series que contiene la sección de la tabla maestra que se quiere obtener del día especificado,
        pero en este caso actualizada.
        '''
    for variable in list_to_true:
        Checker[variable] = True
    return Checker

def obtener_registro_actual(where_to_run:str='cloud_run'):
    '''
    Esta función permite acceder al registro del día de la tabla maestra. Si este no ha sido creado,
    lo crea a partir del último registro en la tabla. De lo contrario, retorna el registro del día
    con las características que tiene.
    Input:
        where_to_run: (str) De donde se extrae la credencial de GCP.
    Output:
        Checker: (pd.Series) El registro que se entiende como el registro actual.
    '''
    fecha = datetime.strptime(fechas_relevantes('PAN')['f_corte'],'%Y-%m-%d') # Se obtiene la fecha del registro actual
    Checker = obtencion_tabla_maestra(where_to_run=where_to_run) # Se obtiene el registro con fecha más nueva en la tabla maestra.
    if Checker['FECHA'].date()!=fecha.date(): # Se revisa si las fechas anteriores difieren y se inicializa el checker del día
        Checker['FECHA']=fecha
        for id in Checker.index:
            if id!='FECHA':
                Checker[id] = False
    # Si el anterior if no se ejecuta, se devuelve el registro actual, que es el mismo al más antiguo. 
    # En caso contrario, devuelve el registro nuevo a subir.
    return Checker

# Estructura de flujo de tareas con la que se monta inicialmente este proyecto. Esta deberá ser cambiada cuando se modifique el flujo de tareas.
grafo_inicial = {'nodos':['Liquidez_H_Pan','Portafolio_H_Pan','Metricas_H_Pan',
                          'VaR_H_Pan','Metricas_IRL_H_Pan','Operaciones_H_Pan',
                          'Operac_Cerradas_H_Blotter','Operac_Abiertas_H_Blotter',
                          'Consumos_Pan_PP'],
                 'enlaces':[('Liquidez_H_Pan','Metricas_H_Pan'),('Portafolio_H_Pan','Metricas_H_Pan'),# A Metricas
                            ('Liquidez_H_Pan','Metricas_IRL_H_Pan'),('Portafolio_H_Pan','Metricas_IRL_H_Pan'),('Operaciones_H_Pan','Metricas_IRL_H_Pan'), # A IRL
                            ('VaR_H_Pan','Consumos_Pan_PP'),('Liquidez_H_Pan','Consumos_Pan_PP'),('Portafolio_H_Pan','Consumos_Pan_PP'),('Metricas_H_Pan','Consumos_Pan_PP') #
                            ]}

# RECOMENDACION:
# El ejecutable de este sub paquete es:

# Ejemplo de prueba. NO lo corra a menos de que esté seguro de que quiere modificar Tabla_Maestra en BigQuery

#-----------------------------------------------------------------------
# Ejemplo de creación y modificación de un registro de la tabla maestra. Se recomienda que luego de cada actualización 
# de la tabla maestra, se aseguren al menos 10 segundos antes de realizar la nueva consulta.

# Creación y cargue de la estructura base en una nueva tabla en BigQuery:

# nodos = grafo_inicial['nodos'] # Se crean los nodos.
# enlaces = grafo_inicial['enlaces'] # Se crean los enlaces.
# grafo,matriz=ejecutor_estructura(nodos=nodos,enlaces=enlaces) # Se crea el grafo y el pd.DataFrame de la tabla maestra
# cargador_estructura(matriz=matriz,job_type='create',where_to_run='local') # Se formatea la tabla maestra. 
# timer()

# Obtención del registro del día, modificación del mismo en el flujo de tareas y actualizacion en BigQuery

#Checker = obtencion_tabla_maestra(where_to_run='local')
#Checker = modificacion_tabla_maestra(Checker=Checker,list_to_true=['VaR_H_Pan','Consumos_Pan_PP'])
#cargador_estructura(matriz=Checker.to_frame().T,where_to_run='local')
#timer()

# Verificación de la actualización del registro

#Checker = obtener_registro_actual(where_to_run='local')

#-----------------------------------------------------------------------
# Otras pruebas
#grafo = creador_grafo(nodos=nodos,enlaces=enlaces)
#creador_estructura_condicionales(grafo=grafo,nube_local='local')
#import matplotlib.pyplot as plt
#nx.draw(grafo)
#plt.show()

# NO intente utilizar otras cosas a menos de que entienda bien la lógica del paquete.