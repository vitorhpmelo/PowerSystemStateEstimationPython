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

sys="IEEE14"


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





prec={"SCADAPF":0.02,"SCADAPI":0.02,"SCADAV":0.01,"SMP":0.01,"SMP":0.01,"SMV":0.01,"PSEUDO":0.01,"VIRTUAL":0.01,"PMU_If":0.001,"PMU_Iinj":0.001,"PMUs_V":0.001}


#%%
dfDMED=create_DMED(sys,prec,graph,ram)


prec_PMUs=0.001
prec_SCADAc=0.01

#%%

dfDMEDSCADA=dfDMED[(dfDMED["prec"]>prec_PMUs)]

#%%

dfDMEDPMU=dfDMED[(dfDMED["prec"]<prec_SCADAc)]

#%%



#%%
conv_noBC,nits_noBC,dfITsGN=SS_WLS_FACTS_noBC(graph,dfDMEDSCADA,ind_i,flatstart=2,pirntits=1,tol2=1e-1,tol=1e-4,prec_virtual=1e-4)


#%%
priori=calc_priori(graph,dfDMEDSCADA,dfDMEDPMU,ind_i)

#%%


SS_MAP_FACTS_withBC(graph,priori,dfDMEDPMU,ind_i,tol2=7,tol=1e-3,flatstart=3,prec_virtual=1e-4)
# %%
