# Esto irá a Cloud Run Function:
from .A_ESTRUCTURA import cargador_estructura,obtener_registro_actual
from .A_TRANSVERSAL import timer
from .MN_01_METRICAS import global_treatment_Metricas_H_Pan
from .MN_02_IRL import global_treatment_IRL_Pan
from .MN_03_INFOMERCADO import global_treatment_Infomercado_Pan

timer() # Se asegura el tiempo prudente del cargue de la información previa a la tabla maestra
Checker = obtener_registro_actual() # Se utiliza el mismo registro si es el de la fecha actual o se reinicia     

if (Checker['Liquidez_H_Pan']) & (Checker['Portafolio_H_Pan']) & (not Checker['Metricas_H_Pan']):
        try:
                #global_treatment_Metricas_H_Pan()
                global_treatment_Metricas_H_Pan(where_to_run='local')
                Checker['Metricas_H_Pan']=True
        except:
                raise Exception('Metricas Fallando')
elif (Checker['Liquidez_H_Pan']) & (Checker['Portafolio_H_Pan']) & (Checker['Operaciones_H_Pan']) & (not Checker['Metricas_IRL_H_Pan']):
        try:
                #global_treatment_IRL_Pan()
                global_treatment_IRL_Pan(where_to_run='local')
                Checker['Metricas_IRL_H_Pan']=True
        except:
                raise Exception('IRL Fallando')
elif (Checker['VaR_H_Pan']) & (Checker['Liquidez_H_Pan']) & (Checker['Portafolio_H_Pan']) & (Checker['Metricas_H_Pan']) & (not Checker['Consumos_Pan_PP']):
        try:
                #global_treatment_Infomercado_Pan()
                global_treatment_Infomercado_Pan(where_to_run='local')
                Checker['Consumos_Pan_PP']=True
        except:
                raise Exception('Consumos PP Fallando')

matriz = Checker.to_frame().T # Se pasa el pd.Series a un dataframe que puede ser concatenado a la tabla maestra
cargador_estructura(matriz=matriz) # Se concatena el registro a la tabla maestra
