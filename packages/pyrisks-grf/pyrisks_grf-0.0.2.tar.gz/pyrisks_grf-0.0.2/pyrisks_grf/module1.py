import pandas as pd
import numpy as np
import networkx as nx

grafo = nx.star_graph(20)
df = pd.DataFrame({k:[False] for k in grafo.nodes})

def hola():
    print('hola mundo')

def suma(a,b):
    return a+b



