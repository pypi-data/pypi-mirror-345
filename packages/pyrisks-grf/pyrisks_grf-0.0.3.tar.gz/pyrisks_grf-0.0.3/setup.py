from setuptools import setup, find_packages

setup(
        name='pyrisks_grf', # Como se descargará el paquete, i.e. el nombre.
        version='0.0.3',# Version en la que va el paquete
        author='Gerencia de Riesgos Financieros Corredores Davivienda S.A.', #Autor-es del paquete
        author_email='gerenciaderiesgos@corredores.com', # Correo electronico de los autores del paquete
        description='This is the first version of GRF package for Panama.', # Descripción corta del paquete
        long_description=open("README.md").read(), # Descripción larga del paquete
        long_description_content_type='text/markdown', # Tipo del contenido del archivo de long description
        packages=find_packages(), # Cargue de los paquetes que están siendo usados en el interior del paquete
        install_requires=['datetime',
                          'gcsfs','google','google-auth','google-cloud','google-cloud-bigquery','google-cloud-storage', #'google-oauth2',
                          'holidays',
                          'IPython','ipywidgets',
                          'networkx','numpy',
                          'openpyxl',
                          'pandas',
                          'QuantLib',
                          'scipy',
                          'tk',
                          'xlrd'], # Listado de paquetes (armelo en orden alfabetico para el orden) que se requiere que estén instalados y que se forza instalación si no lo están.
        license_files=["LICENSE.txt"], # Archivo de licencia.
)