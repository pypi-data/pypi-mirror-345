print('Módulo: TRANSVERSAL\nEste módulo contiene las funciones que son transversales a todos los procesos, así como las rutas más relevantes para el desarrollo de los mismos.')


import gcsfs
import pickle
import pandas as pd
import holidays
import time

from datetime import datetime, timedelta
from google.cloud import bigquery
from google.auth.transport.requests import Request
from google.oauth2 import service_account

# Requeridos gcsfs, pickle, google-cloud-bigquery, google-oauth2, google-auth-transport-requests

#-----------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------
# Sección de Objetos Fijos

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
#-----------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------
# Sección de Funciones

# Funcion que crea time.sleep() en caso de ser necesario

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
        "saldos_liq": "{Pan}:/Privada/Panama/Informes/Concentración por Emisor/Descarga/{year_corte_ayer}/{mes_corte_str}/{dia_corte_ayer} {mes_corte_str_ayer} {year_corte_ayer}.xlsx",
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
    bool = last_updated_date == shouldbe_last_updated_date

    return bool