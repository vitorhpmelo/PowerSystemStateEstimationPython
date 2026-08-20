#%% Simulações de monte carlo
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#versao com amostragem assincrona entre SCADA e PMU

from src.classes import *
from src.readfiles import *
from src.networkstruc import *
from src.SE import *
from src.meas_sampl import *
from src.io import *
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
import csv
import os

sys="IEEE14_rakp2009"





dfDBAR,dfDBRAN,dfDMED,dfDFACTS=read_files(sys) # lê arquivos
#%%

[bars,nbars,pv,pq,ind_i]=create_bus(dfDBAR)
[bran,nbran]=create_bran(dfDBRAN,ind_i)


[branTCSC,nbranTCSC]=create_TCSC(dfDFACTS,ind_i)

[busSVC,BUS_SVC]=create_SVC(dfDFACTS,ind_i)

[branUPFC,nbranUPFC]=create_UPFC(dfDFACTS,ind_i)




graph=create_graph(bars,bran)


addTCSCingraph(graph,branTCSC)

addSVCingraph(graph,busSVC)

addUPFCingraph(graph,branUPFC)


#%%
bran.update(branTCSC)

power_flow_FACTS(graph,inici=1,prt=1,itmax=20,printgrad=0,printres=1)


#%%
df_DMEAS=save_DMEAS_ac_pf(graph,bran,sys,branUPFC,flag_save_csv=False)

#%%
H=save_se_inner_matrices(graph,df_DMEAS,ind_i,flatstart=False,filename="python_se_all_meas_cv",output_dir="tmp")
# %%

SE_WLS_FACTS_noBC(graph,df_DMEAS,ind_i,flatstart=2,prec_virtual=1e-5)
# %%
