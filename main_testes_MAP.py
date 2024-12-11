#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#%%
from classes import *
from readfiles import *
from networkstruc import *
from SS import *
from meas_sampl import *
import pandas as pd
import numpy as np
from networkcalc import *
from BadData import *
import numpy.linalg as liang
import scipy.sparse.linalg as sliang 
from SS_Bayesian import *

#%% Lê arquivos e constroi a estrutura da rede

sys="IEEE14_rakp2009"


dfDBAR,dfDBRAN,dfDMED,dfDFACTS=read_files(sys)


[bars,nbars,pv,pq,ind_i]=creat_bar(dfDBAR)
[ram,nbran]=create_bran(dfDBRAN,ind_i)
#%%
[ramTCSC,nbranTCSC]=create_TCSC(dfDFACTS,ind_i)

[busSVC,BUS_SVC]=create_SVC(dfDFACTS,ind_i)

[ramUPFC,nbranUPFC]=create_UPFC(dfDFACTS,ind_i)




graph=create_graph(bars,ram)

addTCSCingraph(graph,ramTCSC)

addSVCingraph(graph,busSVC)

addUPFCingraph(graph,ramUPFC)





prec={"SCADAPF":0.01,"SCADAPI":0.01,"SCADAV":0.01,"SMP":0.01,"SMP":0.01,"SMV":0.01,"PSEUDO":0.01,"VIRTUAL":0.01,"PMU_If":0.001,"PMU_Iinj":0.001,"PMUs_V":0.001}

#%%

#%%


medidas_virtuais_P=list(set(dfDMED[(dfDMED["type"]==0)&(dfDMED["zmed"]==0)]["de"].to_list()).intersection(dfDMED[(dfDMED["type"]==1)&(dfDMED["zmed"]==0)]["de"].to_list())) 

#%%

dfDMEDSCADA=dfDMED[(dfDMED["type"]<=4)]

#%%

dfDMEDPMU=dfDMED[(dfDMED["type"]>=4)]

dfDMEDSCADA["prec"]=0.02

dfDMEDPMU["prec"]=0.001
#%%



#%%
conv_noBC,nits_noBC,dfITsGN=SS_WLS_FACTS_noBC(graph,dfDMEDSCADA,ind_i,flatstart=2,pirntits=1,tol2=1e-1,tol=1e-4)


#%%
priori=calc_priori(graph,dfDMEDSCADA,dfDMEDPMU,ind_i)

#%%


SS_MAP_FACTS_withBC(graph,priori,dfDMEDPMU,ind_i,flatstart=2,tol2=1,tol=1e-4)
# %%
