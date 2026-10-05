#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#%%
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

sys=data_files+"IEEE14"


dfDBUS,dfDBRAN,dfDMEAS,dfDFACTS=read_files(sys)



[bus,nbus,pv,pq,ind_i]=create_bus(dfDBUS)
[bran,nbran]=create_bran(dfDBRAN,ind_i)
#%%


graph=create_graph(bus,bran)



#%%
conv=power_flow(graph,inici=1,prt=1,itmax=20)
#%%

dfDMEAS_pf=save_DMEAS_pf(graph,bran,sys)

#%%
prec={"SCADAPF":0.02,"SCADAPI":0.02,"SCADAV":0.01,"SMP":0.01,"SMP":0.01,"SMV":0.01,"PSEUDO":0.01,"VIRTUAL":0.01,"PMU_If":0.001,"PMU_Iinj":0.001,"PMUs_V":0.001}

dfDMEAS_nnois=create_DMEAS(sys,prec,graph,bran,dfDMEASpf=dfDMEAS_pf)
#%%

dfDMEAS=insert_res(dfDMEAS_nnois)
#%%
conv_noWLS,nits_noWLS,dfITsWLS=SE_WLS(graph,dfDMEAS,ind_i,flatstart=2,printits=1,tol2=1e-1,tol=1e-4,prec_virtual=1e-4)
#%%


dState=get_state(graph,1)
#%%s