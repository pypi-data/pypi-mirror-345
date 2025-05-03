print('Módulo Nube: METRICAS\nEste módulo contiene la ejecución del cálculo en GCP de la hoja de METRICAS.')

import pandas as pd
import numpy as np
from google.cloud import bigquery

from .A_TRANSVERSAL import project,dataset_id # Se cargan objetos fijos relevantes
from .A_TRANSVERSAL import multiple_query,upload_table,charge_serv # Se cargan funciones relevantes

# Requeridos: db-dtypes, google-cloud-bigquery, google-cloud-storage,google-cloud-bigquery-storage

# Lo que va en __init__.py es lo siguiente:
# De este script solo se debe permitir el uso de los objetos: 
# De este script solo se debe permitir el uso de las funciones: global_treatment

def tratador(client,query_list):
  '''Esta función realiza TODO el tratamiento de las bases para una fecha dada. La fecha debe tener el formato: TIMESTAMP("2025-02-20 00:00:00+00")
  y ser un str. La fecha debe venir incluida en el query.
  Inputs:
    client: BigQuery client. Debe ser el client en el que se está trabajando.

    query_list: list. Sus entradas deben ser querys de SQL que carguen las tablas de las hojas de Portafolio y Liquidez. Deben ir en ese orden
    para que esta función se ejecute de forma correcta.

  Output:
    pd.Dataframe. Se retorna la tabla de métricas a la que se le realizará el append en BigQuery. Esta tendrá las variables:
    'NIT_PORTAFOLIO','PORTAFOLIO','FECHAPORTAFOLIO','VALORTOTAL','VALORAJUSTADOTOTAL','DURACIONMODIFICADA','DURACIONMACAULAY','DV01'
  '''
  # Cargue de las tablas de portafolio y liquidez
  table_portafolio,table_liquidez = multiple_query(client,query_list)
  # Se calcula el DV01 (esto es solo para hacer double-check)
  table_portafolio['DV01'] = ((table_portafolio['VALORMERCADO']*table_portafolio['DURACION_MODIFICADA'])/10000)
  dv01_to_use = 'DV01'

  #--------------------------------------------------------------------------
  # Arreglo dentro de las tablas a nivel de activo dentro del portafolio:

  # Se arregla el valor de la duración para los titulos en nan dentro de portafolio
  table_portafolio['DURACION_MODIFICADA'] = table_portafolio['DURACION_MODIFICADA'].apply(lambda x:0 if np.isnan(x) else x)
  # Valor mercado de los Renta Fija
  table_portafolio['VALORMERCADO_RF'] = table_portafolio['VALORMERCADO']*(table_portafolio['DURACION_MODIFICADA']!=0)
  # Se calcula el valor ponderado de cada activo del portafolio
  table_portafolio['VALORPONDERADO'] = table_portafolio['DV01']*10000
  # Se arreglan las TIR nulas
  table_portafolio['TIR'] = table_portafolio['TIR'].apply(lambda x: int(x) if not np.isnan(x) else 0)
  # Se calcula el valor de la duracion de Macaulay
  table_portafolio['DURACION_MACAULAY'] =  table_portafolio['DURACION_MODIFICADA']*(1+(table_portafolio['TIR']/100))
  # Se calcula el producto de Macaulay
  table_portafolio['PRODUCTO_MACAULAY'] = table_portafolio['DURACION_MACAULAY']*table_portafolio['VALORMERCADO']
  # Se calcula el valor normalizado de la liquidez (pendiente cambiar nombre)
  table_liquidez['VALORNORMALIZADO'] = table_liquidez['VALOR_MERCADO']/365

  #--------------------------------------------------------------------------
  # Colapso a nivel de los portafolios:

  # Variables relevantes por portafolio:
  TP = table_portafolio.groupby(['PORTAFOLIO'])[['VALORMERCADO','VALORPONDERADO','VALORMERCADO_RF','PRODUCTO_MACAULAY']].sum()
  TP.reset_index(inplace=True)
  TP.rename(columns={'VALORMERCADO':'VALORMERCADO_P','VALORPONDERADO':'VALORPONDERADO_P','VALORMERCADO_RF':'VALORMERCADO_P_RF'},inplace=True)
  # Variables relevantes por liquidez:
  TL = table_liquidez.groupby(['PORTAFOLIO'])[['VALOR_MERCADO','VALORNORMALIZADO']].sum()
  TL.reset_index(inplace=True)
  TL.rename(columns={'VALOR_MERCADO':'VALORMERCADO_L','VALORNORMALIZADO':'VALORPONDERADO_L'},inplace=True)

  #--------------------------------------------------------------------------
  # Generación de la Tabla definitiva:

  # Tabla definitiva
  T = pd.merge(TP,TL,on=['PORTAFOLIO'],how='outer')
  # Valor total del portafolio
  T['VALORTOTAL']=T['VALORMERCADO_P']+T['VALORMERCADO_L']
  # Valor ajustado total del portafolio
  T['VALORAJUSTADOTOTAL'] = T['VALORMERCADO_P_RF']+T['VALORMERCADO_L']
  # Duracion Modificada del portafolio
  T['DURACIONMODIFICADA'] = (T['VALORPONDERADO_P']+T['VALORPONDERADO_L'])/T['VALORAJUSTADOTOTAL']
  # Duracion De MACAULAY del portafolio
  T['DURACIONMACAULAY'] = T['PRODUCTO_MACAULAY']/T['VALORAJUSTADOTOTAL']
  # DV01 del portafolio
  T['DV01'] = (T['VALORAJUSTADOTOTAL']*T['DURACIONMODIFICADA'])/10000
  #--------------------------------------------------------------------------
  # Se generan los últimos cambios estéticos a la tabla:

  # Obtención de los identificadores de cada portafolio
  portafolios = pd.merge(table_portafolio[['NIT_PORTAFOLIO','PORTAFOLIO','FECHAPORTAFOLIO']].drop_duplicates(),
                        table_liquidez[['PORTAFOLIO']].drop_duplicates(),
                        how='outer',
                        on='PORTAFOLIO')
  # Relación de los identificadores con los portafolios en la tabla definitiva
  T = pd.merge(portafolios,T,how='inner',on='PORTAFOLIO')
  # Se extraen las variables relevantes para la presentación final
  T=T[['NIT_PORTAFOLIO','PORTAFOLIO','FECHAPORTAFOLIO','VALORTOTAL','VALORAJUSTADOTOTAL','DURACIONMODIFICADA','DURACIONMACAULAY','DV01']]# Incluyo NIT_Portafolio, Portafolio, Fecha, ValorPortafolio, ValorPortafolio Ajustado, Dur mod, durmacaulay,dv01.

  return T

def global_treatment_Metricas_H_Pan(dates=None,where_to_run = 'cloud_run'):
  '''Esta función corre todo el proceso de actualización de la tabla de Métricas de BigQuery.
  Inputs:

    dates: list, determina las fechas que se quieren cambiar dentro de la base de datos. Estas deben venir en formato timestamp, pues de lo
    contrario no se asegura que el código funcione. Si es None, se correrá la actualización observando cuales fechs existen en la hoja
    portafolio, pero no en métricas. El default acá es que esta variable sea None y en caso contrario solo debe darse cuando haya que hacer
    arreglos a la base por fallos en los inputs que sean corregidos o en actualizaciones a gran escala.

    where_to_run: str, determina el entorno en el que se corre.

  Output:
    No aplica.'''
  # Se obtienen las referencias de las Tablas a utilizar
  tables_names=['Portafolio_H_Pan','Liquidez_H_Pan','Metricas_H_Pan'] # Nombres de las tablas a usar
  client,dataset_ref,tables_ref = charge_serv(where_to_run=where_to_run,project=project,dataset_id=dataset_id,tables_names=tables_names) # Obtención de las referencias de las tablas
  table_portafolio_ref,table_liquidez_ref,table_metricas_ref = tables_ref
  # Cuidado
  #print('DELETE FROM {} WHERE 1=1'.format(table_metricas_ref))
  #DELETE FROM `gestion-financiera-334002.DataStudio_GRF_Panama.Metricas_H_Pan` WHERE FECHAPORTAFOLIO=TIMESTAMP("2025-04-08 00:00:00")
  #client.query('DELETE FROM {} WHERE 1=1'.format(table_metricas_ref))# Ojo, esto borra TODO en la tabla
  # Se obtienen las fechas a utilizar en el ejercicio si dates es None
  if dates is None:
    query_spec = "SELECT DISTINCT FECHAPORTAFOLIO FROM {} WHERE FECHAPORTAFOLIO NOT IN (SELECT FECHAPORTAFOLIO FROM {})" # Fijado del query generico que se envía a BigQuery
    query_list=[query_spec.format(table_portafolio_ref,table_metricas_ref)] # Obtención del listado de querys particulares
    dates_list=multiple_query(client,query_list) # Obtención de las fechas que están en la hoja portafolio y no en la hoja metricas
    dates = list(dates_list[0].iloc[:,0].unique()) # Obtención de las fechas en un formato de lista

  # Definición del esquema para el cargue
  esquema = [bigquery.SchemaField('NIT_PORTAFOLIO','STRING',mode = 'NULLABLE'),
            bigquery.SchemaField('PORTAFOLIO','STRING',mode = 'NULLABLE'),
            bigquery.SchemaField('VALORTOTAL','FLOAT',mode = 'NULLABLE'),
            bigquery.SchemaField('VALORAJUSTADOTOTAL','FLOAT',mode = 'NULLABLE'),
            bigquery.SchemaField('DURACIONMODIFICADA','FLOAT',mode = 'NULLABLE'),
            bigquery.SchemaField('DURACIONMACAULAY','FLOAT',mode = 'NULLABLE'),
            bigquery.SchemaField('DV01','FLOAT',mode = 'NULLABLE')]
  print(dates) # Impresión de las

  for d in list(dates):
    # Realización del query y tratamiento de la base de datos
    fecha = 'TIMESTAMP("{}")'.format(str(d))
    print(fecha)
    query_list = ["SELECT * FROM {} WHERE FECHAPORTAFOLIO={}".format(table_portafolio_ref,fecha),"SELECT * FROM {} WHERE FECHAPORTAFOLIO={}".format(table_liquidez_ref,fecha)]
    T = tratador(client,query_list)
    # Realización del cargue en BigQuery
    upload_table(client=client,big_query_table_ref=table_metricas_ref,table_to_append=T,schema=esquema)

# RECOMENDACION:
# El ejecutable de este sub paquete es:
#global_treatment_Metricas_H_Pan(where_to_run = 'service_account')
# NO intente utilizar otras cosas a menos de que entienda bien la lógica del paquete.