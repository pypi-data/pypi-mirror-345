print('Módulo Nube: INFOMERCADO\nEste módulo contiene la ejecución del cálculo en GCP de la hoja de INFOMERCADO.')

#-----------------------------------------------------------------
# Librerías

import pandas as pd

# Librerías de Gooogle
# Para instalar: pip install google-cloud-bigquery-storage
# Para instalar bidq: pip install google-cloud-bigquery pandas-gbq
from google.cloud import bigquery

from .A_TRANSVERSAL import dicc_static,project,dataset_id,dataset_id_col,ideas_querys
from .A_TRANSVERSAL import fechas_relevantes,charge_serv,multiple_query,checker_fechas_cargue,upload_table

def global_treatment_Infomercado_Pan(fecha:str=None,where_to_run='cloud_run'):
    # Diccionario de calificaciones
    rating_map = dicc_static['dicc_ranking_calif']
    #-----------------------------------------------------------------
    # Calculo de Fechas Relevantes
    #fecha = None
    fechas = fechas_relevantes(pais = "PAN", fecha_analisis= fecha)
    fecha_corte,fecha_corte_ayer = [fechas[k] for k in ['f_corte','f_corte_ayer']]
    
    ## Lectura de Inputs

    # Crea el cliente
    client, dataset_ref, tables_ref = charge_serv(where_to_run=where_to_run, project = project, dataset_id = dataset_id, tables_names=[])
    client_col, dataset_ref_col, tables_ref_col = charge_serv(where_to_run=where_to_run, project = project, dataset_id = dataset_id_col, tables_names=[])
    #client, dataset_ref, tables_ref = charge_serv(where_to_run='local', project = project, dataset_id = dataset_id, tables_names=[])
    #client_col, dataset_ref_col, tables_ref_col = charge_serv(where_to_run='local', project = project, dataset_id = dataset_id_col, tables_names=[])

    #table_ref = [f"{A_TRANSVERSAL.project}.{A_TRANSVERSAL.dataset_id}.{}"].format(k)for k in ['Operaciones_H_Pan','Portafolio_H_Pan','Liquidez_H_Pan']]
    table_ref = ["{}.{}.{}".format(project,dataset_id,k) for k in ['Portafolio_H_Pan','VaR_H_Pan','Metricas_H_Pan']]
    table_ref.append("{}.{}.{}".format(project,dataset_id_col,'Biblia_H'))

    # Definición de Queries
    query_list = [
        f"""
        SELECT*
        FROM {table_ref[0]}
        WHERE DATE(FECHAPORTAFOLIO) = '{fecha_corte}'
        """,
        f"""
        SELECT*
        FROM {table_ref[1]}
        WHERE DATE(FECHA) = '{fecha_corte}'
        """,
        f"""
        SELECT*
        FROM {table_ref[2]}
        WHERE DATE(FECHAPORTAFOLIO) = '{fecha_corte}'
        """,
        f"""
        SELECT FECHA, COMPANIA,  TIPO_LIMITE, LIMITE_NUM, FIJO
        FROM {table_ref[3]}
        WHERE (PRODUCTO = 'CORREDORES PANAMA' AND TIPO_LIMITE = 'LIMITE DE INVERSION PP %  (95%)' AND FIJO = 'CORREDORES PANAMA')
        OR (PRODUCTO = 'CORREDORES PANAMA' AND TIPO_LIMITE = 'PLAZO INVERSION TITULOS' AND FIJO = 'CORREDORES PANAMA')
        """]

    # Importe de Input 1, 2, 3, 4
    # Portafolio de Plano, VaR, Metricas_Panama y Biblia
    Portafolio, VaR, Metricas= multiple_query(client = client, query_list = query_list[0:3])
    Biblia = multiple_query(client = client_col, query_list = query_list[3:])[0]
    #-----------------------------------------------------------------
    # Carpintería: Calcular Valores Tabla

    # Consumo Mercado
    # Nominal Porta
    Pos_Max = Portafolio.loc[Portafolio['PORTAFOLIO'] == 'POSICION PROPIA', 'VALORMERCADO'].sum()
    # DV01
    Tot_DV01 = Portafolio.loc[Portafolio['PORTAFOLIO'] == 'POSICION PROPIA', 'DV1'].sum()
    # VaR
    Tot_VaR = VaR.loc[VaR['PORTAFOLIO'] == 'POSICION PROPIA PANAMA', 'VaR_95'].sum()
    # Duración
    Tot_Dur = Metricas.loc[Metricas['PORTAFOLIO'] == 'POSICION PROPIA', 'DURACIONMACAULAY'].iloc[0]

    # Consumo Límites de Inversión
    Pos_PP = pd.DataFrame(Portafolio.loc[Portafolio['PORTAFOLIO'] == 'POSICION PROPIA'].groupby('EMISOR')['VALORMERCADO'].sum()).reset_index(drop=False)
    # Calificación
    worst_rating = Portafolio['CALIF'].loc[Portafolio['CALIF'].map(rating_map).idxmax()]
    # Tipo de Activo
    tipo_activo = Portafolio.loc[Portafolio['PORTAFOLIO'] == 'POSICION PROPIA']['TIPO_ACTIVO']
    consumo_tipo_activo = ", ".join(map(str, set(tipo_activo)))

    # Consumo de Plazo
    # Se debe realizar un promedio ponderado de duraciones 
    Porta_PP = Portafolio[Portafolio['PORTAFOLIO'] == 'POSICION PROPIA']
    # weighted_avg_dur = Porta_PP.groupby('EMISOR').apply(lambda g: (g['DUR_MACA'] * g['VALORMERCADO']).sum() / g['VALORMERCADO'].sum()).reset_index(name = 'DURXEMISOR') # Easier to read but deprecated
    weighted_avg_dur = Porta_PP.groupby('EMISOR').agg(WEIGHTED_AVG = ('DUR_MACA', lambda x: (x * Porta_PP.loc[x.index, 'VALORMERCADO']).sum() / Porta_PP.loc[x.index, 'VALORMERCADO'].sum())).reset_index(drop=False)

    # Límites de Biblia
    # Se encuentran los límites 
    Biblia = Biblia[(Biblia['LIMITE_NUM'] != 0) & (Biblia['FECHA'] == Biblia['FECHA'].max())]

    # Mapeo de Formateo entre Biblia y Portafolio
    porta_map_biblia = {'REPUBLIC OF COLO': 'MINISTERIO DE HACIENDA', 'JPMORGAN CHASE & CO': 'J.P MORGAN CHASE BANK',
                        'SURA ASSET MANAGEMENT': 'GRUPO DE INVERSIONES SURAMERICANA (ANTES SURAMERICANA DE INVERSIONES)',
                        'Banco Davivienda Panama':'DAVIVIENDA PANAMA- FILIAL','Bladex YCD - NY Agency': 'BLADEX S.A. / PANAMA',
                        'BANCOLOMBIA SA':'B. BANCOLOMBIA'}
    biblia_map_porta = {v: k for k,v in porta_map_biblia.items()}
    emisores_biblia = Portafolio.loc[Portafolio['PORTAFOLIO'] == 'POSICION PROPIA', 'EMISOR'].map(porta_map_biblia)
    emisores_porta = emisores_biblia.map(biblia_map_porta)


    # Tabla de Límites Generales
    Tabla_riesgomercado = pd.DataFrame({'VALOR': ['Posición Máxima USD (USD MM)', 'VaR (USD)', 'DV01 Renta Fija (USD)', 'Duración (Años)']})
    

    # Tabla de Límites de Duración
    Tabla_limites_inversion = pd.DataFrame({'VALOR': emisores_porta.unique()})
    Tabla_limites_inversion['LIMITE'] = Tabla_limites_inversion['VALOR'].map(porta_map_biblia).map(Biblia[Biblia['TIPO_LIMITE'] == 'LIMITE DE INVERSION PP %  (95%)'].set_index('COMPANIA')['LIMITE_NUM'])

    # Tabla de Límites de Plazo
    Tabla_limites_plazo = pd.DataFrame({'VALOR': emisores_porta.unique()})
    Tabla_limites_plazo['LIMITE'] = Tabla_limites_plazo['VALOR'].map(porta_map_biblia).map(Biblia[Biblia['TIPO_LIMITE'] == 'PLAZO INVERSION TITULOS'].set_index('COMPANIA')['LIMITE_NUM'])

    # Tablas Finales
    # Tabla 1 Los Límites Principales Generales
    Tabla_riesgomercado['CONSUMO'] = [Pos_Max, Tot_VaR, Tot_DV01, Tot_Dur]
    #Tabla_riesgomercado['CONSUMOPOR'] = Tabla_riesgomercado['CONSUMO']/Tabla_riesgomercado['LIMITE']

    # Tabla 2 Los Límites de Inversión
    Tabla_limites_inversion['CONSUMO'] = Tabla_limites_inversion['VALOR'].map(Pos_PP.set_index('EMISOR')['VALORMERCADO'])/1e6 # MM USD
    Tabla_limites_inversion['CONSUMOPOR'] = Tabla_limites_inversion['CONSUMO']/Tabla_limites_inversion['LIMITE']

    # Se incluye las filas adicionales
    #limite_cal = pd.Series(['Calificación Mínima']).map(Limites_PP.set_index('VALOR')['LIMITE'])[0]
    calificacion_row_df = pd.DataFrame([{'VALOR': 'Calificación Mínima', 'CONSUMO2': worst_rating, 'TABLA': 2.1}])
    #limite_tipo = pd.Series(['Tipo de Activo']).map(Limites_PP.set_index('VALOR')['LIMITE'])[0]
    Tipo_de_activorow_df = pd.DataFrame([{'VALOR': 'Tipo de Activo', 'CONSUMO2': consumo_tipo_activo, 'TABLA': 2.1}])

    Tabla_limites_inversion_str = pd.concat([calificacion_row_df, Tipo_de_activorow_df], ignore_index= True)

    #Tabla 3 Los Límites de Plazo
    Tabla_limites_plazo['CONSUMO'] = Tabla_limites_plazo['VALOR'].map(weighted_avg_dur.set_index('EMISOR')['WEIGHTED_AVG'])
    Tabla_limites_plazo['CONSUMOPOR'] = Tabla_limites_plazo['CONSUMO']/Tabla_limites_plazo['LIMITE']
    # Realizar merge de las tablas para LookerStudio.
    Tabla_riesgomercado['TABLA'] = 1
    Tabla_limites_inversion['TABLA'] = 2
    Tabla_limites_plazo['TABLA'] = 3

    # Looker
    looker_df = pd.concat([Tabla_riesgomercado, Tabla_limites_inversion, Tabla_limites_inversion_str, Tabla_limites_plazo], ignore_index=True)
    looker_df['FECHA'] = fecha_corte
    looker_df['FECHA'] = pd.to_datetime(looker_df['FECHA'], dayfirst= False)

    #-----------------------------------------------------------------
    # Carga a GCP

    # El schema define cada uno de los formatos de las columnas que se carga. Portafolio
    schema_looker = [
        bigquery.SchemaField("VALOR", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("LIMITE", "FLOAT64", mode="NULLABLE"),
        bigquery.SchemaField("CONSUMO", "FLOAT64", mode="NULLABLE"),
        bigquery.SchemaField("CONSUMOPOR", "FLOAT64", mode="NULLABLE"),
        bigquery.SchemaField("TABLA", "FLOAT64", mode="NULLABLE"),
        bigquery.SchemaField("CONSUMO2", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("FECHA", "TIMESTAMP", mode="NULLABLE")
        ]
    
    # Se realiza la carga de información vía APPEND a GCP
    table_ref = "{}.{}.{}".format(project,dataset_id,'Consumos_Pan_PP')
    nombre_fecha_GCP = 'FECHA'
    query = [ideas_querys['cargue_generico'].format(nombre_fecha_GCP,table_ref,nombre_fecha_GCP)]
    fechas_bq = multiple_query(client,query)[0]
    booleano = checker_fechas_cargue(fechas_bq,nombre_fecha_GCP,fecha_corte_ayer)
    if booleano:
        upload_table(client,big_query_table_ref=table_ref,table_to_append=looker_df,schema=schema_looker)