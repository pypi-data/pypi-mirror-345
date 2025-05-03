print('Módulo Nube: IRL\nEste módulo contiene la ejecución del cálculo en GCP de la hoja de IRL.')

#---------------------------------------------------------
# Librerías

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
# Para BigQuery
# pip install google-cloud-bigquery-storage
from google.cloud import bigquery #storage
from google.oauth2 import service_account

from .A_TRANSVERSAL import dicc_static,RGB_F,Riesgo_F,project,dataset_id,ideas_querys
from .A_TRANSVERSAL import business_days_between,upload_table,charge_serv,fechas_relevantes,multiple_query,checker_fechas_cargue

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