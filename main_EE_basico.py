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


#%% Lê arquivos e constroi a estrutura da rede

sys="IEEE14"


dfDBAR,dfDBRAN,dfDMED,dfDFACTS=read_files(sys)



[bars,nbars,pv,pq,ind_i]=creat_bar(dfDBAR)
[ram,nbran]=create_bran(dfDBRAN,ind_i)
#%%


graph=create_graph(bars,ram)



#%%
conv=load_flow_FACTS(graph,inici=1,prt=1,itmax=20)
#%%




dfDMED_fp=save_DMED_fp(graph,ram,sys)

prec={"SCADAPF":0.02,"SCADAPI":0.02,"SCADAV":0.01,"SMP":0.01,"SMP":0.01,"SMV":0.01,"PSEUDO":0.01,"VIRTUAL":0.01,"PMU_If":0.001,"PMU_Iinj":0.001,"PMUs_V":0.001}

dfDMED_sr=create_DMED(sys,prec,graph,ram,dfDMEDfp=dfDMED_fp)


dfDMED=insert_res(dfDMED_sr,100)

conv_noWLS,nits_noWLS,dfITsWLS=SS_WLS_FACTS_noBC(graph,dfDMED,ind_i,flatstart=2,printits=1,tol2=1e-1,tol=1e-4,prec_virtual=1e-4)
#%%



dState=get_state(graph,1)
#%%s