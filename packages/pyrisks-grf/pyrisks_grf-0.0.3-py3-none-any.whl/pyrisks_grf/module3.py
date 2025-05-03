# Esto se ejecuta en el local
from pyrisks_grf.A_ESTRUCTURA import cargador_estructura,obtener_registro_actual
from pyrisks_grf.A_TRANSVERSAL import timer
from pyrisks_grf.ML_01_VaR import global_treatment_VaR_Pan
from pyrisks_grf.ML_02_PLANO import global_treatment_Plano_Pan
from pyrisks_grf.ML_03_OPERACIONES_H_PAN import global_treatment_Operaciones_H_Pan
from pyrisks_grf.ML_04_OPERACIONES_BLOTTER import global_treatment_Operaciones_Blotter_Pan

# Ojo el orden de ejecución acá propuesto es acorde al flujo de tareas y a la hora (i.e. orden) en el que aproximadamente
# se disponibilizan los insumos necesarios para cada proceso.

timer()
Checker = obtener_registro_actual(where_to_run='local') # Se utiliza el mismo registro si es el de la fecha actual o se reinicia     
# Se ejecuta la hoja de Operaciones de Pershing
global_treatment_Operaciones_H_Pan()
# Actualiza la tabla maestra
Checker['Operaciones_H_Pan'] = True

# Se ejecutan las Hojas de Operaciones Blotter
global_treatment_Operaciones_Blotter_Pan()
# Actualiza la tabla maestra
Checker['Operac_Cerradas_H_Blotter'] = True
Checker['Operac_Abiertas_H_Blotter'] = True

# Se ejecuta el plano. 
global_treatment_Plano_Pan()
# Actualiza la tabla maestra
Checker['Liquidez_H_Pan'] = True
Checker['Portafolio_H_Pan'] = True

# Se ejecuta el VaR
global_treatment_VaR_Pan()
# Actualiza la tabla maestra
Checker['VaR_H_Pan'] = True

matriz = Checker.to_frame().T # Se pasa el pd.Series a un dataframe que puede ser concatenado a la tabla maestra
cargador_estructura(matriz=matriz,where_to_run='local') # Se concatena el registro a la tabla maestra