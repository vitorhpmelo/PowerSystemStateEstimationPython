#%% Simulações de monte carlo
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#versao com amostragem assincrona entre SCADA e PMU

from src.classes import *
from src.readfiles import *
from src.networkstruc import *
from src.SE import *
from src.meas_sampl import *
import pandas as pd
import numpy as np
from src.networkcalc import *
from src.BadData import *
import numpy.linalg as liang
import scipy.sparse.linalg as sliang 
from src.SE_Bayesian import *
from tqdm.notebook import tqdm
import matplotlib.pyplot as plt
import timeit 

#%% Lê arquivos e constroi a estrutura da rede

sys="IEEE14"





dfDBAR,dfDBRAN,dfDMED,dfDFACTS=read_files(sys) # lê arquivos
#%%

[bars,nbars,pv,pq,ind_i]=create_bus(dfDBAR)
[bran,nbran]=create_bran(dfDBRAN,ind_i)


graph=create_graph(bars,bran)



#%%
power_flow_FACTS(graph,inici=1,prt=1,itmax=20,printgrad=0,printres=1)




df_DMEAS=save_DMEAS_ac_pf(graph,bran,sys,dUPFC={},flag_save_csv=True)
#%%

df_DMEAS=df_DMEAS[df_DMEAS["type"].isin([0,1,2,3,4])]


SE_WLS_FACTS_noBC(graph,df_DMEAS,ind_i)
# %%

t=timeit.timeit('SE_WLS_FACTS_noBC(graph,df_DMEAS,ind_i)', globals=globals(), number=10)
t=t/10
print("Tempo médio de execução do fluxo de potência com FACTS: ",t," segundos")
#%%