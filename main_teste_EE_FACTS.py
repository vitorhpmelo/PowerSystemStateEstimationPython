#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script executing SE with different solution methods
"""


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


#%% Lê arquivos e constroi a estrutura da rede

data_files="network_data/"
sys=data_files+"IEEE118_rakp2009"


dfDBAR,dfDBRAN,dfDMED,dfDFACTS=read_files(sys)


[bars,nbars,pv,pq,ind_i]=create_bus(dfDBAR)
[ram,nbran]=create_bran(dfDBRAN,ind_i)
#%%
[ramTCSC,nbranTCSC]=create_TCSC(dfDFACTS,ind_i)

[busSVC,BUS_SVC]=create_SVC(dfDFACTS,ind_i)

[ramUPFC,nbranUPFC]=create_UPFC(dfDFACTS,ind_i)




graph=create_graph(bars,ram)

addTCSCingraph(graph,ramTCSC)

addSVCingraph(graph,busSVC)

addUPFCingraph(graph,ramUPFC)


#%%
print("EE - GN")
it1=SE_WLS_FACTS_noBC(graph,dfDMED,ind_i,flatstart=2,printits=1,printcond=1,tol=1e-5,tol2=1e-4)

#%%
print("EE - GNbc")
it2=SE_WLS_FACTS_withBC(graph,dfDMED,ind_i,flatstart=2,printits=1,printcond=1,tol=1e-5,tol2=1e-4)


#%%

print("EE - LM")
it3=SE_WLS_FACTS_LM_BC(graph,dfDMED,ind_i,flatstart=2,printits=1,printcond=1,tol=1e-5,tol2=1e-4)
# it2=SE_WLS_FACTS_grad(graph,dfDMED,ind_i,flatstart=2,pirntits=1,printcond=1,tol=1e-5,tol2=1e-4)

# %%

