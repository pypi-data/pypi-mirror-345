print('Módulo Local: Operaciones para IRL (Operaciones_H_Pan)\nEste módulo contiene la ejecución del cálculo local de las Operaciones del Hist de Pershing para así subirlo a GCP.')

#-----------------------------------------------------------------
# Librerias

import pandas as pd
from datetime import datetime, timedelta
import warnings

# Para BigQuery
# pip install google-cloud-bigquery-storage
from google.cloud import bigquery

from .A_TRANSVERSAL import Riesgo_F,RGB_F,dicc_static,project,dataset_id,ideas_querys
from .A_TRANSVERSAL import fechas_relevantes,generate_paths,multiple_query,checker_fechas_cargue,upload_table,charge_serv

def global_treatment_Operaciones_H_Pan(fecha:str=None,where_to_run:str='local'):
    #-----------------------------------------------------------------
    # OPeraciones para IRL

    #-----------------------------------------------------------------
    # Calculo de Fechas Relevantes
    #fecha = None
    fechas = fechas_relevantes(pais = "PAN", fecha_analisis= fecha)
    fecha_corte,fecha_corte_ayer = [fechas[k] for k in ['f_corte','f_corte_ayer']]

    # Objetos estáticos
    month_map = dicc_static['dicc_month_map']

    # Generación de Fechas y Paths
    #
    all_paths = generate_paths(fecha_corte= fecha_corte, fecha_corte_ayer=fecha_corte_ayer, RGB_F=RGB_F, Riesgo_F=Riesgo_F, month_map=month_map)

    # Desagregacióon Paths Locales
    Operac_day_path = all_paths['operac_IRL']

    # Se leen las información de operaciones del día que viene de Pershing
    warnings.filterwarnings("ignore", message="Workbook contains no default style")
    Operac_day = pd.read_excel(Operac_day_path, skiprows= 7, engine='openpyxl')

    # Se eliminan las dos últimas filas que son vacías
    Operac_day = Operac_day.iloc[:-2]

    # Carpintería
    # Se deben definir en primera instancia los nombres de la columna, pues el archivo no los trae en un formato aceptable.
    nombres_cols_operac = ['Trade_Date', 'Process_Date', 'Account', 'Short_Name', 'Office', 'IP', 'Symbol', 'Product_Type',
                        'Source_of_input', 'Buy_Sell', 'Number_Of_Shares', 'Execution_Price', 'Total_Amount', 'Cusip_Number',
                        'Security_Name',    'Account_Type', 'Commission_Amount', 'Issue_Currency', 'Order_Quantity', 'Principal_Amount',
                        'Trade_Ref', 'Trade_Type', 'Settlement_Date']

    Operac_day.columns = nombres_cols_operac

    # Incluir la fecha por completitud, aunque este archivo se va a reemplazar todos los días
    Operac_day['FECHA'] = fecha_corte

    # Formateo de columnas previo a GCP
    # Formateo para fechas
    Operac_day['Trade_Date'] = pd.to_datetime(Operac_day['Trade_Date'], format='%m/%d/%Y')
    Operac_day['Process_Date'] = pd.to_datetime(Operac_day['Process_Date'], format='%m/%d/%Y')
    Operac_day['Settlement_Date'] = pd.to_datetime(Operac_day['Settlement_Date'], format='%m/%d/%Y')
    Operac_day['FECHA'] =  pd.to_datetime(Operac_day['FECHA'])

    # Formateo de strings
    cols_to_string = ['Account', 'Short_Name', 'Office', 'IP', 'Symbol', 'Product_Type',
                    'Source_of_input', 'Buy_Sell', 'Cusip_Number', 'Security_Name',
                    'Account_Type', 'Issue_Currency', 'Trade_Ref', 'Trade_Type']
    Operac_day[cols_to_string] = Operac_day[cols_to_string].astype(str)

    # Formateo de valores numéricos
    cols_to_float = ['Number_Of_Shares', 'Execution_Price', 'Total_Amount', 'Commission_Amount',
                    'Order_Quantity', 'Principal_Amount']
    Operac_day[cols_to_float] = Operac_day[cols_to_float]

    #-----------------------------------------------------------------
    # Cargue a GCP

    # El schema define cada uno de los formatos de las columnas que se carga. Operaciones
    schema_operac = [
        bigquery.SchemaField("Trade_Date", "TIMESTAMP", mode="NULLABLE"),
        bigquery.SchemaField("Process_Date", "TIMESTAMP", mode="NULLABLE"),
        bigquery.SchemaField("Account", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("Short_Name", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("Office", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("IP", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("Symbol", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("Product_Type", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("Source_of_input", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("Buy_Sell", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("Number_Of_Shares", "FLOAT64", mode="NULLABLE"),
        bigquery.SchemaField("Execution_Price", "FLOAT64", mode="NULLABLE"),
        bigquery.SchemaField("Total_Amount", "FLOAT64", mode="NULLABLE"),
        bigquery.SchemaField("Cusip_Number", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("Security_Name", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("Account_Type", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("Commission_Amount", "FLOAT64", mode="NULLABLE"),
        bigquery.SchemaField("Issue_Currency", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("Order_Quantity", "FLOAT64", mode="NULLABLE"),
        bigquery.SchemaField("Principal_Amount", "FLOAT64", mode="NULLABLE"),
        bigquery.SchemaField("Trade_Ref", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("Trade_Type", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("Settlement_Date", "TIMESTAMP", mode="NULLABLE"),
        bigquery.SchemaField("FECHA", "TIMESTAMP", mode="NULLABLE")
        ]
    # Se realiza la carga de información vía TRUNCATE a GCP

    # Se realiza la carga de información vía APPEND a GCP
    client, dataset_ref, tables_ref = charge_serv(where_to_run=where_to_run,project=project, dataset_id = dataset_id, tables_names=[])
    #client, dataset_ref, tables_ref = charge_serv(where_to_run='local',project=project, dataset_id = dataset_id, tables_names=[])
    table_ref = "{}.{}.{}".format(project,dataset_id,'Operaciones_H_Pan')
    nombre_fecha_GCP = 'FECHA'
    query = [ideas_querys['cargue_generico'].format(nombre_fecha_GCP,table_ref,nombre_fecha_GCP)]
    fechas_bq = multiple_query(client,query)[0]
    booleano = checker_fechas_cargue(fechas_bq,nombre_fecha_GCP,fecha_corte_ayer)
    if booleano:
        upload_table(client,big_query_table_ref=table_ref,table_to_append=Operac_day,schema=schema_operac)