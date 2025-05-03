print('Módulo Local: VaR\nEste módulo contiene la ejecución del cálculo local del VaR para así subirlo a GCP.')

#-----------------------------------------------------------------
# Librerias

import pandas as pd
import numpy as np

# Para BigQuery
# pip install google-cloud-bigquery-storage
from google.cloud import bigquery

from .A_TRANSVERSAL import Riesgo_F,RGB_F,dicc_static,project,dataset_id,ideas_querys
from .A_TRANSVERSAL import fechas_relevantes,generate_paths,multiple_query,checker_fechas_cargue,upload_table,charge_serv

# Los valores con 0 son portafolios inactivos, con lo cual no se desea incluir la información a GCP.
# También se elimina la segunda columna que no tiene información alguna 
def format_VaR_excel(df, var_conf):

    df.replace(0, np.nan, inplace= True)
    df.drop(df.columns[1], axis = 1, inplace = True)

    # Formateo de las fechas
    df.iloc[0,1:]
    dates = pd.to_datetime(df.columns[1:])
    df.columns = [df.columns[0]] + dates.strftime("%Y-%m-%d").tolist()

    # Carpintería
    VaR_df= df.melt(id_vars=df.columns[0], var_name="FECHA", value_name= var_conf)
    VaR_df = VaR_df.dropna().reset_index(drop= True)

    # Formateo
    VaR_df.rename(columns={VaR_df.columns[0]: "PORTAFOLIO"}, inplace= True)
    VaR_df['PORTAFOLIO'] = VaR_df['PORTAFOLIO'].astype(str)
    VaR_df['FECHA'] = pd.to_datetime(VaR_df['FECHA'])
    VaR_df[var_conf] = VaR_df[var_conf].astype(float)

    return(VaR_df)

def global_treatment_VaR_Pan(fecha:str=None,where_to_run:str='local'):
    #-----------------------------------------------------------------
    # Calculo de Fechas Relevantes
    #fecha = None
    fechas = fechas_relevantes(pais = "PAN", fecha_analisis= fecha)
    fecha_corte,fecha_corte_ayer = [fechas[k] for k in ['f_corte','f_corte_ayer']]

    # Objetos estáticos
    month_map = dicc_static['dicc_month_map']

    # Generación de Fechas y Paths
    all_paths = generate_paths(fecha_corte= fecha_corte, fecha_corte_ayer=fecha_corte_ayer, RGB_F=RGB_F, Riesgo_F=Riesgo_F, month_map=month_map)

    # Desagregacióon Paths Locales
    VaR_path, manual_data_path = (all_paths[k] for k in ('VaR','manual_data_plano'))
    #-----------------------------------------------------------------
    # Path
    # Se leen las dos hojas de VaR, al 95 y al 99.
    VaR95_excel = pd.read_excel(VaR_path, sheet_name="VaR EWMA (95%)", skiprows= 1)
    VaR99_excel = pd.read_excel(VaR_path, sheet_name="VaR EWMA (99%)", skiprows= 1)

    #-----------------------------------------------------------------
    # Carpinteria

    VaR95 = format_VaR_excel(VaR95_excel, var_conf= "VaR_95")
    VaR99 = format_VaR_excel(VaR99_excel, var_conf= "VaR_99")
    VaR = VaR95.merge(VaR99[['PORTAFOLIO', 'FECHA', 'VaR_99']], on=['PORTAFOLIO', 'FECHA'], how='left')

    # Filtrar únicamente para la fecha de corte
    #VaR_carga = VaR[VaR['FECHA'] == fecha_corte].copy()
    VaR_carga = VaR.copy()
    
    Porta_df = pd.read_excel(manual_data_path, sheet_name="Input", usecols=list(range(5)), skiprows= 1, dtype={'NUMERO':str})
    Porta_df = Porta_df.dropna(how = "all")

    VaR_carga['PERFIL'] = VaR_carga['PORTAFOLIO'].map(Porta_df.drop_duplicates(subset= 'PORTAFOLIO').set_index('PORTAFOLIO')['PERFIL'])
    VaR_carga = VaR_carga[VaR_carga['PORTAFOLIO'] != 'TOTAL ADPT']

    #-----------------------------------------------------------------
    # Revisar antes de cargar

    print(rf"El VaR que se cargará tiene el siguiente shape: {VaR_carga.shape}")

    # El schema define cada uno de los formatos de las columnas que se carga. Portafolio
    schema_Var = [
        bigquery.SchemaField("PORTAFOLIO", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("FECHA", "TIMESTAMP", mode="REQUIRED"),
        bigquery.SchemaField("VaR_95", "FLOAT64", mode="REQUIRED"),
        bigquery.SchemaField("VaR_99", "FLOAT64", mode="REQUIRED"),
        bigquery.SchemaField("PERFIL", "STRING", mode="NULLABLE")
        ]
    # Se carga el VaR
    client, dataset_ref, tables_ref = charge_serv(where_to_run=where_to_run,project=project, dataset_id = dataset_id, tables_names=[])
    #client, dataset_ref, tables_ref = charge_serv(where_to_run='local',project=project, dataset_id = dataset_id, tables_names=[])
    table_ref = "{}.{}.{}".format(project,dataset_id,'VaR_H_Pan')
    nombre_fecha_GCP = 'FECHA'
    query = [ideas_querys['cargue_generico'].format(nombre_fecha_GCP,table_ref,nombre_fecha_GCP)]
    fechas_bq = multiple_query(client,query)[0]
    booleano = checker_fechas_cargue(fechas_bq,nombre_fecha_GCP,fecha_corte_ayer)
    if booleano:
        upload_table(client,big_query_table_ref=table_ref,table_to_append=VaR_carga,schema=schema_Var)
    # Se realiza la carga de información vía APPEND a GCP
