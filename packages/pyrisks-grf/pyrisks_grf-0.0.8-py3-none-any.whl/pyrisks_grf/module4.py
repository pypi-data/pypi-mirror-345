#--------------------------------------------------------
#--------------------------------------------------------
# Cargues
#import functions_framework
import pandas as pd
import numpy as np

import gcsfs
import pickle
import holidays
import time
from datetime import datetime, timedelta

from google.cloud import bigquery
from google.auth.transport.requests import Request
from google.oauth2 import service_account



#--------------------------------------------------------
#--------------------------------------------------------
# Objetos generales

project = "gestion-financiera-334002" # Fijado de proyecto
dataset_id_col = "DataStudio_GRF"
dataset_id = "DataStudio_GRF_Panama" # Fijado de dataset
mastertable = "Tabla_Maestra"

RGB_F = 'K'
Riesgo_F = 'R'


ideas_querys = {'cargue_generico':"""
            SELECT DISTINCT {}
            FROM {}
            ORDER BY {}""",
   'extraccion':["SELECT * FROM `id_tabla` WHERE FECHA = (SELECT MAX(FECHA) FROM `id_tabla`)",
                              "SELECT DISTINCT FECHAPORTAFOLIO FROM {} WHERE FECHAPORTAFOLIO NOT IN (SELECT FECHAPORTAFOLIO FROM {})"],
                'borrado':["DELETE FROM `id_tabla` WHERE FECHAPORTAFOLIO=TIMESTAMP('2025-04-08 00:00:00')"]
                }

# Diccionario de objetos estáticos
dicc_static = {
    'dicc_month_map': {'01': 'Enero', '02': 'Febrero', '03': 'Marzo',
                       '04': 'Abril', '05': 'Mayo', '06': 'Junio', 
                       '07': 'Julio', '08': 'Agosto', '09': 'Septiembre',
                       '10': 'Octubre', '11': 'Noviembre', '12': 'Diciembre'},
    'tipo_activos_holdings':  ['CASH AND EQUIVALENTS','EQUITY','ETF','FIXED INCOME', 'MUTUAL FUND'],
    'tipo_producto_plano': ['Cash', 'Equity', 'ETF', 'FixedIncome', 'MutualFund'],
    'pp_titulosmanuales': ['PXG898019'],
    'dicc_nac_2_cont': {'ESTADOS UNIDOS': 'EEUU', 'LUXEMBURGO': 'EUROPA', 'GRAND CAYMAN': 'EUROPA',
                        'ALEMANIA': 'EUROPA', 'NEDERLAND': 'EUROPA', 'MEXICO': 'LATINOAMERICA', 
                        'PERU': 'LATINOAMERICA', 'COLOMBIA': 'LATINOAMERICA', 'SPAIN': 'EUROPA',
                        'FRANCIA': 'EUROPA', 'PANAMA': 'LATINOAMERICA', 'IRELAND': 'EUROPA', 
                        'IRLANDA': 'EUROPA'},
    'original_names_blotter': ['Trade Dt', 'Exec Time (GMT)', 'Qty (M)', 'BrkrName', 'Ord/Inq',
                               'Dlr Alias', 'Brkr', 'Seq#', 'SetDt', 'C/Firm', 
                               'Exec Time', 'SalesFirm', 'SetDt Real', 'Diferencia en días'],
    'new_names_blotter': ['Trade_Date','Execution_Time','Quantity_M','Contraparte_Name','Ord_Inq',
                          'Dlr_Alias', 'Contraparte_Code', 'Sec_Number', 'Settlement_Date', 'C_Firm',
                          'Exec_Time', 'Sales_Firm', 'Real_Settlement_Date', 'Days_Difference'],
    'original_names_incumplimientos': ['TRADE DATE','PRICE','NET CASH'],
    'new_names_incumplimientos': ['Trade_Date','Price','Net'],
    'dicc_ranking_calif': {
                            # Investment Grade
                            "AAA": 1, "Aaa": 1,            # Best possible rating
                            "AA+": 2, "Aa1": 2,
                            "AA": 3, "Aa2": 3,
                            "AA-": 4, "Aa3": 4,
                            "A+": 5, "A1": 5,
                            "A": 6, "A2": 6,
                            "A-": 7, "A3": 7,
                            "BBB+": 8, "Baa1": 8,
                            "BBB": 9, "Baa2": 9,
                            "BBB-": 10, "Baa3": 10,  # Lowest investment grade

                            # Speculative Grade (High Yield)
                            "BB+": 11, "Ba1": 11,
                            "BB": 12, "Ba2": 12,
                            "BB-": 13, "Ba3": 13,
                            "B+": 14, "B1": 14,
                            "B": 15, "B2": 15,
                            "B-": 16, "B3": 16,
                            "CCC+": 17, "Caa1": 17,
                            "CCC": 18, "Caa2": 18,
                            "CCC-": 19, "Caa3": 19,
                            "CC": 20, "Ca": 20,
                            "C": 21, "C": 21,
                            "D": 22, "D": 22,  # Default (worst rating)

                            # Short-Term Ratings
                            "F1+": 1, "P-1": 1,  # Best short-term rating
                            "F1": 2, "P-2": 2,
                            "F2": 3, "P-3": 3,
                            "F3": 4,
                            "B": 5,
                            "C": 6,
                            "D": 7  # Default for short-term debt
                        },
    'porta_map_biblia': {'REPUBLIC OF COLO': 'MINISTERIO DE HACIENDA', 'JPMORGAN CHASE & CO': 'J.P MORGAN CHASE BANK',
                     'SURA ASSET MANAGEMENT': 'GRUPO DE INVERSIONES SURAMERICANA (ANTES SURAMERICANA DE INVERSIONES)',
                     'Banco Davivienda Panama':'DAVIVIENDA PANAMA- FILIAL','Bladex YCD - NY Agency': 'BLADEX S.A. / PANAMA',
                     'BANCOLOMBIA SA':'B. BANCOLOMBIA'},
    'haircuts_IRL': [
    [0.07, 0.07, 0.07, 0.07],
    [0.15, 0.15, 0.15, 0.15],
    [0.04, 0.04, 0.04, 0.04]],
    'bandas_IRL': [
    [1, 3],
    [1, 7],
    [1, 30]],
    'prob_impago_terc': [[0.0401451612903226, 0.0533192071086808, 0.0871878211716342, 0.0971878211716342]],
    'gar_Pershing': 299980
    }

#--------------------------------------------------------
#--------------------------------------------------------
# Funciones generales

def timer(seconds:float=10):
   time.sleep(seconds)

# Funcion para correr con cloud_functions
def create_serv(project,path_to_json, service_name, version,
              SCOPES=["https://www.googleapis.com/auth/cloud-platform"]):
  '''Esta función permite hacer el ingreso a la información de BigQuery al crear el client cuando se quiere hacer usando el usuario de
  servicio en caso de correrse el proceso en automático.'''
  creds = None
  fs = gcsfs.GCSFileSystem(project = project)

  with fs.open(f'credenciales_api/{path_to_json}', 'rb') as token:
        creds = pickle.load(token)

  if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
      creds.refresh(Request())
  return bigquery.Client(project=project,credentials=creds)
  #return build(service_name, version, credentials=creds)


def charge_serv(where_to_run,project,dataset_id,tables_names):
  '''Esta función devuelve las referencias de las tablas a utilizar basado en su nombre.
  Inputs:
    where_to_run: str, determina el entorno en el que se corre.

    project: str. Nombre del proyecto a buscar en BigQuery.

    dataset_id: str. Nombre del conjunto de datos dentro del proyecto que se quiere usar.

    tables_names: list. Lista que contiene los nombres de las hojas que están dentro del conjunto de datos, que serán llamadas y para las
    que se entregarán referencias al usuario.

  Output:
    client: BigQuery client. Debe ser el client en el que se está trabajando.

    dataset_ref: BigQuery reference. Referencia que contiene la información (referencias) de las tablas dentro del conjunto de datos de interés.

    tables_ref: list. Contiene como entradas BigQuery references asociadas a las tablas que se quieren consultar.
  '''
  key_path = rf"{Riesgo_F}:\CONFIDENCIAL\Informes\Control Límites FICs\Automatizaciones\Herramienta APTs\gestion-financiera-334002-74adb2552cc5.json"
  # Cargue del proyecto de GCS
  if where_to_run == 'cloud_run':
    client = create_serv(project,'gcs_riesgos_2.pickle', 'bigquery', 'v2') # Creación del BigQuery.client
  elif 'local' in where_to_run:
    # Cargar credenciales
    credentials = service_account.Credentials.from_service_account_file(
        key_path,
        scopes = ["https://www.googleapis.com/auth/cloud-platform"],
    )
    client = bigquery.Client(credentials = credentials)
  #elif where_to_run == 'colab':
  #  from google.colab import auth
  #  auth.authenticate_user() # Se solicitan las credenciales para tener acceso a un usuario que tenga permisos en BigQuery
  #  client = bigquery.Client(project) # Creación del BigQuery.client
  dataset_ref = bigquery.DatasetReference(project, dataset_id)
  # Se obtienen las referencias de las Tablas a utilizar
  tables_ref = [dataset_ref.table(k) for k in tables_names]
  return client,dataset_ref,tables_ref

# Revisión de Fechas existentes. Se crea una función que hace multiples querys
def multiple_query(client,query_list):
  '''Esta función permite obtener un listado con las bases de datos obtenidas de un listado de querys que obtienen bases de datos.
  Abstenerse de utilizar querys distintos a estos, pues harán que la lista tenga vacios.
  Inputs:
    client: BigQuery client. Debe ser el client en el que se está trabajando.

    query_list: list. Sus entradas deben ser querys de SQL que carguen tablas, las cuales serán entregadas dentro de otra lista.

  Output:
    list. Contiene como entradas pd.Dataframe, los cuales contienen las tablas cargadas según el listado de querys.'''
  lista = [client.query(q).to_dataframe() for q in query_list]
  return lista

def simple_query_sender(client,query):
   client.query(query)

def upload_table(client,big_query_table_ref,table_to_append,schema,write_disposition:str='WRITE_APPEND'):
  '''Esta función permite hacer el append de la table_to_append a la tabla de big query con referencia big_query_table_ref, usando el esquema schema.
  Inputs:
    client: BigQuery client. Debe ser el client en el que se está trabajando.

    big_query_table_ref: BigQuery table reference de la tabla en la que se va a hacer el append. Esta debe estar dentro del client.

    table_to_append: pd.Dataframe que contiene la tabla (que hace match con el esquema a utilizar para realizar el append).

    schema: Listado cuyas entradas son objetos tipo BigQuery.SchemaField. Esquema a utilizar para el cargue de información.
    Debe coincidir con las variables y características de las mismas en la tabla de BigQuery.

    write_disposition: str que define el tipo de append a realizar. Hay dos opciones 'WRITE_APPEND', 'WRITE_TRUNCATE' y la primera es 
    el default. Tenga cuidado con usar 'WRITE_TRUNCATE' en tablas que no deban ser reescritas en su totalidad.

  Output:
    No aplica.'''
  # Configuración del cargue
  job_config = bigquery.LoadJobConfig(
              schema = schema,
              write_disposition = write_disposition  # Importante, no queremos sobreescribir.
              )
  # Ejecución del cargue
  job = client.load_table_from_dataframe(table_to_append,big_query_table_ref, job_config = job_config)
  print(job.result())
  



def create_schema(variables_characteristics):
   '''
   Esta función crea un esquema para bigquery a partir de un diccionario con variables y sus características:
   input:
        variables_characteristics: Diccionario que contiene en cada llave (que es un str con el nombre de la variable 
        a crear, i.e. el 'name') y el value de cada llave es un diccionario con las llaves 'type' y 'mode' que tendrán
        dentro estas características. Por ejemplo debe ser:
            {'var1':{'type':'STR','mode':'REQUIRED'},
            'var2':{'type':'BOOL','mode':'NULLABLE'}}
   '''
   if type(variables_characteristics) is dict:
    schema = [bigquery.SchemaField(j,variables_characteristics[j]['type'],
                                   mode = variables_characteristics[j]['mode']) for j in variables_characteristics]
    return schema
   else:
      raise Exception('Introduzca un diccionario.') 

def create_table(client,big_query_table_ref,table_to_append,schema):
   '''
   Esta función toma un pd.DataFrame y lo sube como una nueva tabla en BigQuery. Si la tabla ya existe, la elimina 
   y crea una nueva con la información deseada.
   inputs:
        client: cliente de BigQuery que realizará las modificaciones. Debe tener cuidado en configurarlo con permisos
        de modificación, pues de lo contrario esta función no se ejecutará correctamente. 
        big_query_table_ref: id de la tabla (exista o no). Este define el proyecto y dataset donde la nueva tabla 
        se creará.
        table_to_append: pd.DataFrame que contiene los registros que se subiran a una tabla de BigQuery.
        schema: Esquema de BigQuery que es consistente con las variables y estructura de table_to_append'''
   client.delete_table(big_query_table_ref, not_found_ok=True)  # Pide que la tabla se elimine si ya está creada. De lo contrario no pasa nada y se sigue con el resto del código
   print("Deleted table '{}'.".format(big_query_table_ref))
   table = bigquery.Table(big_query_table_ref) # Se propone la ruta de la tabla
   table = client.create_table(table) # Se crea la tabla
   print(f"Created table: {big_query_table_ref}")
   upload_table(client,big_query_table_ref,table_to_append,schema) # Se carga la información nueva a la tabla. 

# Función para encontrar el día hábil que está num_days antes o despues.
def search_business_day(fecha, festivos_dates,num_days:int,format:str="%d/%m/%Y"):

    """
    Encuentra el día hábil para Colombia/Panamá que está num_days antes o despues de fecha. Si num_days
    es psoitivo, va hacia adelante, en caso contrario hacia atras.

    Parámetros: 
        fecha: (str) Fecha base en formato compatible con format
        festivos_dates: (list) la lista con los festivos.
        num_days: (int) numero de dias antes o despues.
        format: (str) formato de la fecha a usar.

    Output: El día hábil anterior en formato 'DD-MM-YY'.
    """
    today = pd.to_datetime(fecha, dayfirst= True)
    if num_days>0:
        search_day = today + timedelta(days = num_days)
    elif num_days<0:
        search_day = today - timedelta(days = -num_days)
    else:
        search_day = today

    while search_day.weekday() in (5,6) or search_day.strftime(format) in festivos_dates:
        if num_days>0:
            search_day += timedelta(days= 1)
        elif num_days<0:
            search_day -= timedelta(days= 1)
        else:
           break # Cuando num_days es cero, no se debería hacer nada, pues se está forzando la aplicación a +0 dias.

    return search_day.strftime(format)


# Función para encontrar el día hábil anterior.
def previous_business_day(fecha, festivos_dates):

    """
    Encuentra el día anterior hábil para Colombia.

    Parámetros: Fecha base en formato 'DD-MM-YYYY' y la lista con los festivos.

    Output: El día hábil anterior en formato 'DD-MM-YY'.
    """
    today = pd.to_datetime(fecha, dayfirst= True)
    previous_day = today - timedelta(days = 1)

    while previous_day.weekday() in (5,6) or previous_day.strftime("%d/%m/%Y") in festivos_dates:
        previous_day -= timedelta(days= 1)

    return previous_day.strftime("%d/%m/%Y")

# Función para encontrar el día hábil siguiente.
def next_business_day(fecha, festivos_dates, days):

    """
    Encuentra el "days" dia hábil siguiente, con days siendo el número de días to move forward.

    Parámetros: Fecha base en formato 'DD-MM-YYYY' y la lista con los festivos.

    Output: El día hábil anterior en formato 'DD-MM-YY'.
    """
    today = pd.to_datetime(fecha, dayfirst= False)
    next_day = today + timedelta(days = days)

    while next_day.weekday() in (5,6) or next_day.strftime("%Y-%m-%d") in festivos_dates:
        next_day += timedelta(days= 1)

    return next_day.strftime("%Y-%m-%d")


def fechas_relevantes(pais, fecha_analisis = None):
    """
    Encuentra la fecha de análisis (fecha de corrida), fecha de corte (día hábil anterior) y 
    fecha de corte de ayer (día hábil anterior de fecha de corte). También retorna lo mismo pero 
    poniendo el día primero.

    Parámetros: 
    - pais(string): "PAN" para tomar en cuenta los festivos de Panamá.
                    "COL" para tomar en cuenta los festivos de Colombia.

    Output: Fecha de análisis, fecha de corte, fecha de corte ayer y las últimas dos con el día de primeras.
    En total, 5 fechas y la lista de festivos.
    """

    if fecha_analisis is None:
        fecha_analisis = datetime.today().strftime("%d/%m/%Y") # Fecha en la que se correrá la macro.
        
    current_year = datetime.today().year

    if pais == "PAN":
        festivos_dates = holidays.Panama(years = range(current_year - 1, current_year + 2))
    elif pais == "COL":
        festivos_dates = holidays.Colombia(years = range(current_year - 1, current_year + 2))
    
    festivos_dates = pd.to_datetime(list(festivos_dates), dayfirst= False).strftime("%d/%m/%Y")
    fecha_corte_d = previous_business_day(fecha_analisis, festivos_dates) # Fecha de consolidación de la información.
    fecha_corte_ayer_d = previous_business_day(fecha_corte_d, festivos_dates) # Fecha anterior al día de consolidación.

    # El formato para la lectura de exceles se debe manejar 'YYYY-MM-DD'.
    fecha_analisis = pd.to_datetime(fecha_analisis, dayfirst= True).strftime("%Y-%m-%d")
    fecha_corte = pd.to_datetime(fecha_corte_d, dayfirst= True).strftime("%Y-%m-%d")
    fecha_corte_ayer = pd.to_datetime(fecha_corte_ayer_d, dayfirst= True).strftime("%Y-%m-%d")

    print('Fecha analisis  :',fecha_analisis)
    print('Fecha corte     :',fecha_corte)
    print('Fecha corte ayer:',fecha_corte_ayer)

    diccionario = {'f_analisis':fecha_analisis, 
                   'f_corte':fecha_corte, 
                   'f_corte_ayer':fecha_corte_ayer, 
                   'f_corte_d':fecha_corte_d, 
                   'f_corte_ayer_d':fecha_corte_ayer_d,
                   'festivos':festivos_dates}
    return diccionario

def checker_fechas_cargue(fechas_list, nombre_fecha_GCP, fecha_corte_ayer):

    """
    Verifica si la última fecha cargada en GCP corresponde a t-2.
    Retorna un booleano.

    Parámetros: 
    - fechas_list(list): La lista con las fechas.
    -nombre_fecha_GCP: El nombre de la columna a extraer.


    Output: Un booleano si se procede a realizra la carga o no.
    """
         
    fechas_list = fechas_list[rf"{nombre_fecha_GCP}"].unique()
    fechas_list = [i.date() for i in fechas_list]
    fechas_list = pd.Series(fechas_list).dropna().tolist()
    
    last_updated_date = max(fechas_list)
    shouldbe_last_updated_date = datetime.strptime(fecha_corte_ayer, "%Y-%m-%d").date()
    booleano = last_updated_date == shouldbe_last_updated_date

    return booleano

def business_days_between(start_date, end_date, pais):
    """
    Calculate the number of business days between two dates,
    excluding weekends and Colombian holidays.

    Parameters:
    -----------
    start_date : datetime-like (e.g., pd.Timestamp, str, datetime.datetime)
        The start date of the range (inclusive).
   
    end_date : datetime-like
        The end date of the range (inclusive).
    
    pais(string): "PAN" para tomar en cuenta los festivos de Panamá.
                  "COL" para tomar en cuenta los festivos de Colombia.

    Returns:
    --------
    int
        Number of business days between start_date and end_date,
        excluding weekends and holidays in Colombia. Holidays are
        computed for the range [start_date.year - 1, start_date.year + 1].
    """

    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)
   
    year = start_date.year

    if pais == "PAN":
        festivos_dates = holidays.Panama(years=range(year - 1, year + 2))
    elif pais == "COL":
        festivos_dates = holidays.Colombia(years=range(year - 1, year + 2))

   
    all_dates = pd.date_range(start=start_date, end=end_date, freq='D')
   
    business_days = all_dates[
        (all_dates.weekday < 5) & (~pd.Series(all_dates.date).isin(festivos_dates))
    ]
   
    return len(business_days) - 1

def parse_date_parts(fecha: str):
    """
    Given a date string in 'YYYY-MM-DD' format, return its year, month, and day as strings.
   
    Parameters:
        fecha (str): Date string in the format 'YYYY-MM-DD'.

    Returns:
        dict: Dictionary with keys 'year', 'month', and 'day'.
    """
    return {
        "year": str(fecha[:4]),
        "month": str(fecha[5:7]),
        "day": str(fecha[8:10]),
        "year_month": str(fecha[:7])
    }

def all_path_dyncomp(fecha_corte, fecha_corte_ayer, RGB_F: str, Riesgo_F: str, month_map):
    """
    Compute all dynamic components used in file paths from a given date.

    Parameters:
        fecha_corte (str): Date string in format 'YYYY-MM-DD'.
        month_map (dict): Dictionary mapping 'YYYY-MM' to a human-readable month string (e.g. '2024-12' -> 'December').

    Returns:
        dict: Dictionary of dynamic components like year, month string, day, and previous day values.
    """
    # Calculate fecha corte.
    fecha_obj = datetime.strptime(fecha_corte, "%Y-%m-%d")
    fecha_corte_flat = fecha_obj.strftime("%Y%m%d")
    parts = parse_date_parts(fecha_corte)
    mes_corte_str = month_map[parts['month']]
    
    # Calculate for fecha corte ayer.
    ayer_parts = parse_date_parts(fecha_corte_ayer)
    mes_corte_str_ayer = month_map[ayer_parts['month']]

    # Modifications of format for fecha corte
    fecha_corted = fecha_obj.strftime("%d-%m-%Y")
    fecha_corteddot = fecha_obj.strftime("%d.%m.%Y")

    return {
        "fecha_corte": fecha_corte,
        "fecha_corte_flat": fecha_corte_flat,
        "year_corte": parts["year"],
        "mes_corte_str": mes_corte_str,
        "dia_corte": parts["day"],
        "yearmes_corte": parts["year_month"],
        "year_corte_ayer": ayer_parts["year"],
        "mes_corte_str_ayer": mes_corte_str_ayer,
        "dia_corte_ayer": ayer_parts["day"],
        "fecha_corted": fecha_corted,
        "fecha_corteddot": fecha_corteddot,
        "Pan": RGB_F,
        "Col": Riesgo_F
    }

def generate_paths(fecha_corte: str, fecha_corte_ayer: str, RGB_F: str, Riesgo_F: str, month_map):
    
    """
    Generate all required file paths using the dynamic components derived from a given date.

    Parameters:
        fecha_corte (str): Date string in format 'YYYY-MM-DD'.
        month_map (dict): Dictionary mapping 'YYYY-MM' to a human-readable month string.

    Returns:
        dict: Dictionary where keys are path names and values are formatted paths.
    """
    values = all_path_dyncomp(fecha_corte, fecha_corte_ayer, RGB_F, Riesgo_F, month_map)

    path_templates = {
        "pershing": "{Pan}:/Privada/Panama/Sistemas de Negociación/PERSHING/{year_corte}/{mes_corte_str}/Holdings Pershing {fecha_corte}.xlsx",
        "manual_data_plano": "{Pan}:/Privada/Panama/Planos Integrados Panamá/Automatización Plano Panamá/Auto_Plano_Panama/Input/Input_Manual.xlsx",
        "AKI_BG": "{Pan}:/Privada/Panama/Planos Integrados Panamá/Automatización Plano Panamá/Auto_Plano_Panama/Input/AKI.txt",
        "calificaciones": "{Pan}:/Privada/Panama/Planos Integrados Panamá/Base con calificaciones certificadas.xlsx",
        "assetclass": "{Pan}:/Privada/Panama/Planos Integrados Panamá/Asset_Class_ADPTS.xlsx",
        "ISIN": "{Pan}:/Privada/Panama/Planos Integrados Panamá/Automatización Plano Panamá/Auto_Plano_Panama/Input/ISIN.xlsx",
        "emisores": "{Pan}:/Privada/Panama/Planos Integrados Panamá/Isines en valores.xlsx",
        "TRM": "{Col}:/CONFIDENCIAL/CONTROL POSICION -CONFIDENCIAL-/5. AD's Mercado NP/Otros Análisis/Valoración/Archivos PiP/Monedas/PIPO{fecha_corte_flat}.xls",
        "saldos_liq": "{Pan}:/Privada/Panama/Informes/Concentración por Emisor/Descarga/{year_corte_ayer}/{mes_corte_str_ayer}/{dia_corte_ayer} {mes_corte_str_ayer} {year_corte_ayer}.xlsx",
        "output_folder_plano": "{Pan}:/Privada/Panama/Planos Integrados Panamá/{year_corte}/{yearmes_corte}",
        "nombre_plano": "Plano Corredores Davivienda Panamá {fecha_corte}.xlsx",
        "output_BG": "{Pan}:/Privada/Panama/Planos Integrados Panamá/Automatización Plano Panamá/Auto_Plano_Panama/Input/BG/Info_BG_{fecha_corte}.xlsx",
        "operaciones_blotter": "{Pan}:/Privada/Panama/Sistemas de Negociación/POSICION PROPIA/{fecha_corted}.xlsx",
        "incumplimientos_blotter": "D:/bloomberg10/Downloads/Cuadro Riesgo-Cumplimientos {fecha_corteddot}.xlsx",
        "nombres_parametros_blotter": "{Pan}:/Privada/Panama/Informes/Control Contrapartes/Auto_Control_Contraparte/Input/Nombres_Contraparte.xlsx",
        "VaR": "{Pan}:/Privada/Panama/Planos Integrados Panamá/VaR Histórico.xlsx",
        "operac_IRL": "{Pan}:/Privada/Panama/Sistemas de Negociación/PERSHING/{year_corte}/{mes_corte_str}/Operaciones - {mes_corte_str} {dia_corte}.xlsx"
    }

    return {name: template.format(**values) for name, template in path_templates.items()}

# Función para formatear el df antes de realizar su carga a GCP.
def Formateo_df2GCP(df, cols_to_datetime, cols_to_float64, cols_to_string, dayfirst):
    """
    Format specified columns in a DataFrame.

    Parameters:
    df : DataFrame to format
    cols_to_datetime : list of columns to convert to datetime (dayfirst=True)
    cols_to_float64 : list of columns to convert to float64
    cols_to_string : list of columns to convert to string
    dayfirst: Dummie if the date has the day first.

    Returns:
    The formatted DataFrame.
    """
    if not df.empty:

        if cols_to_datetime:
            df[cols_to_datetime] = df[cols_to_datetime].apply(pd.to_datetime, dayfirst=dayfirst, errors='coerce')

        if cols_to_float64:
            df[cols_to_float64] = df[cols_to_float64].apply(lambda x: pd.to_numeric(x, errors='coerce'))

        if cols_to_string:
            df[cols_to_string] = df[cols_to_string].astype(str)

    return df

#--------------------------------------------------------
#--------------------------------------------------------
# Estructura

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

#--------------------------------------------------------
#--------------------------------------------------------
# Metricas

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
  print('Metricas: Corrió Cargue de Cliente y referencias de tablas.')
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
  print('Metricas: Corrió la lista de dates\n\n',dates)

  # Definición del esquema para el cargue
  esquema = [bigquery.SchemaField('NIT_PORTAFOLIO','STRING',mode = 'NULLABLE'),
            bigquery.SchemaField('PORTAFOLIO','STRING',mode = 'NULLABLE'),
            bigquery.SchemaField('VALORTOTAL','FLOAT',mode = 'NULLABLE'),
            bigquery.SchemaField('VALORAJUSTADOTOTAL','FLOAT',mode = 'NULLABLE'),
            bigquery.SchemaField('DURACIONMODIFICADA','FLOAT',mode = 'NULLABLE'),
            bigquery.SchemaField('DURACIONMACAULAY','FLOAT',mode = 'NULLABLE'),
            bigquery.SchemaField('DV01','FLOAT',mode = 'NULLABLE')]
  print('Metricas: Se creó el esquema.')

  for d in list(dates):
    # Realización del query y tratamiento de la base de datos
    fecha = 'TIMESTAMP("{}")'.format(str(d))
    print(fecha)
    query_list = ["SELECT * FROM {} WHERE FECHAPORTAFOLIO={}".format(table_portafolio_ref,fecha),"SELECT * FROM {} WHERE FECHAPORTAFOLIO={}".format(table_liquidez_ref,fecha)]
    T = tratador(client,query_list)
    print(f'Metricas: Se ejecutó el tratador para la fecha {fecha}')
    # Realización del cargue en BigQuery
    upload_table(client=client,big_query_table_ref=table_metricas_ref,table_to_append=T,schema=esquema)
    print(f'Metricas: Se ejecutó el cargador de la tabla para la fecha {fecha}')

#--------------------------------------------------------
#--------------------------------------------------------
# IRL

def global_treatment_IRL_Pan(fecha:str=None,where_to_run:str='cloud_run'):
    # Objetos estáticos
    inputH, inputBandas, input_prob_impago_terceros, gar_Pershing = (dicc_static[k] for k in ('haircuts_IRL','bandas_IRL',
                                                                                            'prob_impago_terc', 'gar_Pershing'))
    #fecha = None
    fechas = fechas_relevantes(pais = "PAN", fecha_analisis= fecha)
    fecha_corte,fecha_corte_ayer,fecha_corte_d = [fechas[k] for k in ['f_corte','f_corte_ayer','f_corte_d']]
    #---------------------------------------------------------
    # Inputs Manuales: Haircuts, Bandas y Pr de Impago de Terceros

    # Definición de Haircuts
    tipo_Haircut = ['HC normal', 'HC Moderado', 'HC Severo', 'HC Severo Macroeconómico']
    activos_rows = ['Dólar', 'Acciones', 'Deuda Privada']

    # Algo así es inputH
    #inputH = [
    #    [0.07, 0.07, 0.07, 0.07],
    #    [0.15, 0.15, 0.15, 0.15],
    #    [0.04, 0.04, 0.04, 0.04]
    #]

    Haircuts = pd.DataFrame(inputH, index=activos_rows, columns=tipo_Haircut)
    print('-'*60+'\nEstos son los Haircuts: \n\n',Haircuts,'\n\n'+'-'*60)

    # Definición de días de las bandas
    cols_rangod = ['Desde', 'Hasta']
    numb_rows = ['Banda 1', 'Banda 2', 'Banda 3']

    # inputBandas es algo así:
    # inputBandas = [
    #     [1, 3],
    #     [1, 7],
    #    [1, 30]
    # ]

    Bandas = pd.DataFrame(inputBandas, index=numb_rows, columns=cols_rangod)
    print('-'*60+'\nEstas son las Bandas: \n\n',Bandas,'\n\n'+'-'*60)

    # Definición de probabilidad de impago de terceros
    cols_escenarios = ['Normal', 'Moderado', 'Severo', 'Severo Macroeconómico']
    P_row = ['Pr']
    
    # input_prob_impago_terceros es algoa sí:
    # input_prob_impago_terceros = [[0.0401451612903226, 0.0533192071086808, 0.0871878211716342, 0.0971878211716342]]

    Prob_Impago_Ter = pd.DataFrame(input_prob_impago_terceros, index=P_row, columns=cols_escenarios)
    print('-'*60+'\nEstas son las Probabilidades de Impago: \n\n',Prob_Impago_Ter,'\n\n'+'-'*60)
    

    #---------------------------------------------------------
    # Previos

    ## Lectura de Inputs

    # Crea el cliente
    client, dataset_ref, tables_ref = charge_serv(where_to_run=where_to_run, project = project, dataset_id = dataset_id, tables_names=[])
    #client, dataset_ref, tables_ref = charge_serv(where_to_run='local', project = project, dataset_id = dataset_id, tables_names=[])

    #table_ref = [f"{A_TRANSVERSAL.project}.{A_TRANSVERSAL.dataset_id}.{}"].format(k)for k in ['Operaciones_H_Pan','Portafolio_H_Pan','Liquidez_H_Pan']]
    table_ref = ["{}.{}.{}".format(project,dataset_id,k) for k in ['Operaciones_H_Pan','Portafolio_H_Pan','Liquidez_H_Pan']]

    # Definición de Queries
    query_list = [f"""
        SELECT*
        FROM {table_ref[0]}
        WHERE DATE(Settlement_Date) > '{fecha_corte}'
        """,
        f"""
        SELECT*
        FROM {table_ref[1]}
        WHERE DATE(FECHAPORTAFOLIO) = '{fecha_corte}'
        """,
        f"""
        SELECT PORTAFOLIO, NOMINAL_ACTUAL
        FROM {table_ref[2]}
        WHERE DATE(FECHAPORTAFOLIO) = '{fecha_corte}'
        """]

    # Importe de Input 1, 2, 3.
    # Operaciones para IRL, Portafolio de Plano y Liquidez de Plano.
    Operaciones, Portafolio, Liquidez = multiple_query(client = client, query_list = query_list)

    #---------------------------------------------------------
    # Contabilización de ALAC


    # Escenario Normal y Moderado van de la mano.
    # La única diferencia con los Escenarios Severo y Severo Macroneconómico es que 
    # a los segundos se les suma las garantías de Pershing.

    # Se diseña Moderado y posteriormente se agrega la diferencia.
    ALAC_dicc = {}
    suffixes = [k.replace('HC ','').title() for k in tipo_Haircut]
    gar_Pershing_escenarios = [gar_Pershing, gar_Pershing, 0, 0]
    conteo = 0
    
    for escenario in suffixes:

        gar_Pershing_es = gar_Pershing_escenarios[conteo]
        Haircut_es = tipo_Haircut[conteo]

        bandas_columns = ['Banda 1', 'Banda 2', 'Banda 3']
        activos_rows = ['Liquidez', 'Portafolio', 'Acciones']
        ALAC = pd.DataFrame(index=activos_rows, columns=bandas_columns)

        ALAC.loc['Liquidez'] = Liquidez.loc[Liquidez['PORTAFOLIO'] == 'POSICION PROPIA', 'NOMINAL_ACTUAL'].sum() - gar_Pershing_es
        ALAC.loc['Portafolio'] = Portafolio[(Portafolio['PORTAFOLIO'] == 'POSICION PROPIA') &
                                            (Portafolio['CLASIFICACION2'] != 'ACCIONES') & 
                                            (Portafolio['IF_TRADE'] == 1)]['VALORMERCADO'].sum() * (1 - Haircuts.at['Deuda Privada', Haircut_es])
        ALAC.loc['Acciones'] = Portafolio[(Portafolio['PORTAFOLIO'] == 'POSICION PROPIA') &
                                            (Portafolio['CLASIFICACION2'] == 'ACCIONES') & 
                                            (Portafolio['IF_TRADE'] == 1)]['VALORMERCADO'].sum() * (1  - Haircuts.at['Acciones', Haircut_es])
        
        ALAC.loc['Total'] = ALAC.sum()

        ALAC_dicc[f'ALAC_{escenario}'] = ALAC

        conteo += 1

    #---------------------------------------------------------
    # Salidas de efectivo netas totales

    # Necesitamos realizar el cálculo de nuevas columnas en operaciones.
    # Valoración final para cada título en operaciones
    renta_f_cond = Operaciones['Product_Type'] == "FIXED INCOME"
    Operaciones['VALOR_FINAL'] = (Operaciones['Number_Of_Shares'] * Operaciones['Execution_Price'])/(100 * renta_f_cond +~ renta_f_cond)

    # Días para la definición de bandas
    Operaciones['Trade_Date'] = pd.to_datetime(Operaciones['Trade_Date'])
    Operaciones['Settlement_Date'] = pd.to_datetime(Operaciones['Settlement_Date']).dt.date 
    Operaciones['Days'] =  Operaciones['Settlement_Date'].apply(lambda d: business_days_between(fecha_corte,d, pais= "PAN"))

    # Definición de banda a partir de días
    conditions_d = [
        (Operaciones['Days'] >= (Bandas.at['Banda 1', 'Desde'])) & (Operaciones['Days'] <= Bandas.at['Banda 1', 'Hasta']),
        (Operaciones['Days'] >= Bandas.at['Banda 2', 'Desde']) & (Operaciones['Days'] <= Bandas.at['Banda 2', 'Hasta']),
        (Operaciones['Days'] >= Bandas.at['Banda 3', 'Desde']) & (Operaciones['Days'] <= Bandas.at['Banda 3', 'Hasta'])
    ]
    bandas_nom = [1,2,3]

    Operaciones['Banda'] = np.select(conditions_d, bandas_nom, default=np.nan).astype(int)

    # Se crea la columna de portafolio para diferenciar posición propia de Terceros.
    Operaciones['PORTAFOLIO'] = np.where(Operaciones['Short_Name'] == "CORREDORES", "POSICION PROPIA", "TERCEROS")

    #---------------------------------------------------------
    # Salidas de efectivo: Posicion propia y terceros

    # Calculamos las entradas y salidas de efectivo.
    Req_PPyTer_dicc = {}
    activos_rows = ['Venta_in', 'Compra_in', 'Venta_out','Compra_out','Terceros']
    bandas_nom_py = [1,2,3]
    bandas_to_check = []
    conteo = 0

    # Iteración sobre los escenarios
    for escenario in suffixes:

        Haircut_es = tipo_Haircut[conteo]
        bandas_to_check = []
        Req_PPyTer = pd.DataFrame(index=activos_rows, columns=bandas_columns)

        # Dentro de cada escenario se itera
        for banda_i in bandas_nom_py: 

            bandas_to_check.append(banda_i)

            # Plata que me entra por vender un título.
            Req_PPyTer.iloc[Req_PPyTer.index.get_loc('Venta_in'), banda_i - 1] = Operaciones[(Operaciones['PORTAFOLIO'] == 'POSICION PROPIA') &
                                                                                    (Operaciones['Banda'].isin(bandas_to_check)) & 
                                                                                    (Operaciones['Buy_Sell'] == 'SELL')]['Total_Amount'].abs().sum()
            
            # Compra_in - Compra_out calcula la diferencia entre lo que vale en t-1 el título y lo que pague. Lo que
            # me entra de título se pondera por haircut.
            Req_PPyTer.iloc[Req_PPyTer.index.get_loc('Compra_in'), banda_i - 1] = Operaciones[(Operaciones['PORTAFOLIO'] == 'POSICION PROPIA') &
                                                                                    (Operaciones['Banda'].isin(bandas_to_check)) & 
                                                                                    (Operaciones['Buy_Sell'] == 'BUY')]['VALOR_FINAL'].abs().sum() * (1 - Haircuts.at['Dólar', Haircut_es])

            # Paralelamente, Venta_in - Venta_out, corresponde a lo que lo que le vendí menos lo que vale hoy.
            # No hay ponderación porque lo que me entra es efectivo líquido.
            
            Req_PPyTer.iloc[Req_PPyTer.index.get_loc('Venta_out'), banda_i - 1] = Operaciones[(Operaciones['PORTAFOLIO'] == 'POSICION PROPIA') &
                                                                        (Operaciones['Banda'].isin(bandas_to_check)) & 
                                                                        (Operaciones['Buy_Sell'] == 'SELL')]['VALOR_FINAL'].abs().sum()
            # Plata que sale por compra de un título.
            
            Req_PPyTer.iloc[Req_PPyTer.index.get_loc('Compra_out'), banda_i - 1] = Operaciones[(Operaciones['PORTAFOLIO'] == 'POSICION PROPIA') &
                                                                                    (Operaciones['Banda'].isin(bandas_to_check)) & 
                                                                                    (Operaciones['Buy_Sell'] == 'BUY')]['Total_Amount'].abs().sum() 
            # Cálculo para terceros
            Req_PPyTer.iloc[Req_PPyTer.index.get_loc('Terceros'), banda_i - 1] = Operaciones[(Operaciones['PORTAFOLIO'] == 'TERCEROS') &
                                                                                    (Operaciones['Banda'].isin(bandas_to_check))]['VALOR_FINAL'].abs().sum() * Prob_Impago_Ter[escenario].values[0]
        # Sumamos entradas - salidas.
        Req_PPyTer.loc['Total_PP'] = (Req_PPyTer.loc['Venta_out'] + Req_PPyTer.loc['Compra_out']) - (Req_PPyTer.loc['Venta_in'] + Req_PPyTer.loc['Compra_in'])
            
        # Si lo anterior es mayor a cero, entonces el requerimiento es cero y caso contrario el requirimiento es el valor.
        Req_PPyTer.loc['Final_PP'] = np.where(Req_PPyTer.loc['Total_PP'] < 0, 0, Req_PPyTer.loc['Total_PP'])


        Req_PPyTer_dicc[f'Req_{escenario}'] = Req_PPyTer
        
        conteo += 1

    #Req_PPyTer_dicc['Req_Moderado']
    #Req_PPyTer_dicc['Req_Severo Macroeconómico']

    #---------------------------------------------------------
    # Calculo de IRL e IRL%

    cols_IRL = bandas_columns
    rows_IRL = ['ALAC', 'REQ_PP','REQ_TERCEROS','IRL_absoluto','IRL_relativo']
    df_IRL_dicc = {}

    for escenario in suffixes:

        df_IRL = pd.DataFrame(0.1, index  = rows_IRL, columns= cols_IRL)

        for banda_i in bandas_columns: 
        
            Req_PPyTer = Req_PPyTer_dicc[f'Req_{escenario}']
            
            df_IRL.loc['ALAC', banda_i]  = ALAC_dicc[f'ALAC_{escenario}'].loc['Total', banda_i] # ALAC.
            df_IRL.at['REQ_PP', banda_i] = Req_PPyTer.at['Final_PP', banda_i] # Requerimientos de posición propia
            df_IRL.at['REQ_TERCEROS', banda_i]  = Req_PPyTer.at['Terceros', banda_i] # Requerimiento de Terceros

            # IRL Absoluto
            df_IRL.at['IRL_absoluto', banda_i] = df_IRL.at['ALAC', banda_i] - df_IRL.at['REQ_TERCEROS', banda_i] - df_IRL.at['REQ_PP', banda_i]
            
            # IRL Relativo
            df_IRL.at['IRL_relativo', banda_i] = df_IRL.at['ALAC', banda_i] /(df_IRL.at['REQ_TERCEROS', banda_i] + df_IRL.at['REQ_PP', banda_i])

            df_IRL_dicc[escenario] = df_IRL

    print('-'*60+'\nIRL Hoy Moderado:\n\n',df_IRL_dicc['Moderado'],'\n\n'+'-'*60)
    print('-'*60+'\nIRL Hoy Severo:\n\n',df_IRL_dicc['Severo'],'\n\n'+'-'*60)

    #---------------------------------------------------------
    # Crear Tabla para GCP y looker

    # Combinar la información de los cuatro escenarios en un solo df
    IRL_combined = pd.concat([df.T.reset_index().assign(source = key) for key, df in df_IRL_dicc.items()],
                            ignore_index=True)

    # Renombrar la columna de valores relevantes
    IRL_combined.rename(columns={'index':'BANDA'}, inplace=True)
    IRL_combined.rename(columns={'source':'ESCENARIO'}, inplace=True)

    # Meltear con base a banda para un único df de una sola columna también para todas las bandas.
    #df_IRL_long = df_combined.melt(id_vars=['VALOR','ESCENARIO'], var_name = 'BANDA', value_name = 'VALORNUM')
    IRL_combined['FECHA'] = fecha_corte

    #---------------------------------------------------------
    # Revisar tabla antes de cargar

    #IRL_combined
    # Querie para extraer la última fecha de IRL
    table_id = 'Metricas_IRL_H_Pan'
    table_ref = f"{project}.{dataset_id}.{table_id}"


    query = f"""
        SELECT*
        FROM {table_ref}
        WHERE FECHA = (SELECT MAX(FECHA) FROM {table_ref})
            """
    IRL_ayer = multiple_query(client=client,query_list=[query])[0] # Ultima fecha cargada
    # Ordenar IRL_ayer para que haga match con hoy
    IRL_ayer = IRL_ayer.set_index(['ESCENARIO','BANDA'])
    IRL_ayer = IRL_ayer.loc[IRL_combined.set_index(['ESCENARIO','BANDA']).index].reset_index()

    IRL_combined['VARIACIONP_IRL'] = (IRL_combined['IRL_absoluto']/IRL_ayer['IRL_absoluto']) - 1
    #IRL_combined['VARIACIONP_IRL'] = 0

    # IRL a cargar
    print('-'*60+'\nIRL a cargar:\n\n',IRL_combined.head(3),'\n\n'+'-'*60)
    # IRL de t-1.
    print('-'*60+'\nIRL de t-1:\n\n',IRL_ayer.head(3),'\n\n'+'-'*60)

    # El schema define cada uno de los formatos de las columnas que se carga. Operaciones
    schema_metr_IRL = [
        bigquery.SchemaField("BANDA", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("ALAC", "FLOAT64", mode="REQUIRED"),
        bigquery.SchemaField("REQ_PP", "FLOAT64", mode="REQUIRED"),
        bigquery.SchemaField("REQ_TERCEROS", "FLOAT64", mode="REQUIRED"),
        bigquery.SchemaField("IRL_absoluto", "FLOAT64", mode="REQUIRED"),
        bigquery.SchemaField("IRL_relativo", "FLOAT64", mode="REQUIRED"),
        bigquery.SchemaField("ESCENARIO", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("VARIACIONP_IRL", "FLOAT64", mode="NULLABLE"),
        bigquery.SchemaField("FECHA", "TIMESTAMP", mode="REQUIRED")
        ]

    # Formateo de la tabla antes de cargar
    IRL_combined['FECHA'] = pd.to_datetime(IRL_combined['FECHA'])

    nombre_fecha_GCP = 'FECHA'
    query = [ideas_querys['cargue_generico'].format(nombre_fecha_GCP,table_ref,nombre_fecha_GCP)]
    fechas_bq = multiple_query(client,query)[0]
    booleano = checker_fechas_cargue(fechas_bq,nombre_fecha_GCP,fecha_corte_ayer)
    if booleano:
        upload_table(client,big_query_table_ref=table_ref,table_to_append=IRL_combined,schema=schema_metr_IRL)
    else:
        print('No se cargó')

#--------------------------------------------------------
#--------------------------------------------------------
# Infomercado

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
    else:
        print('No se cargó')


#--------------------------------------------------------
#--------------------------------------------------------
# Ejecutor

# Triggered from a message on a Cloud Pub/Sub topic.
#@functions_framework.cloud_event
#def ejecutor(cloud_event):
def ejecutor(where_to_run = 'cloud_run'):
    Checker = obtener_registro_actual(where_to_run=where_to_run) # Se obtiene el registro actual de la tabla maestra    
    print(Checker)
    if (Checker['Liquidez_H_Pan']) & (Checker['Portafolio_H_Pan']) & (not Checker['Metricas_H_Pan']):
        print('Metricas Corriendo')
        global_treatment_Metricas_H_Pan(where_to_run=where_to_run)
        print('Función Metricas Ejecutada')
        Checker['Metricas_H_Pan']=True
    elif (Checker['Liquidez_H_Pan']) & (Checker['Portafolio_H_Pan']) & (Checker['Operaciones_H_Pan']) & (not Checker['Metricas_IRL_H_Pan']):
        print('Metricas IRL Corriendo')
        global_treatment_IRL_Pan(where_to_run=where_to_run)
        print('Función IRL Ejecutada')
        Checker['Metricas_IRL_H_Pan']=True
    elif (Checker['VaR_H_Pan']) & (Checker['Liquidez_H_Pan']) & (Checker['Portafolio_H_Pan']) & (Checker['Metricas_H_Pan']) & (not Checker['Consumos_Pan_PP']):
        print('Consumos PP Corriendo')
        global_treatment_Infomercado_Pan(where_to_run=where_to_run)
        print('Función Consumos PP Ejecutada')
        Checker['Consumos_Pan_PP']=True
    matriz = Checker.to_frame().T # Se pasa el pd.Series a un dataframe que puede ser concatenado a la tabla maestra
    print('Matriz Actualizada')
    try:
        cargador_estructura(matriz=matriz,where_to_run=where_to_run) # Se concatena el registro a la tabla maestra
        print('Matriz Cargada en GCP')
    except:
        raise Exception('Cargue de Registro en Tabla Maestra Fallando')

ejecutor()