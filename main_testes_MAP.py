#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de excução simples do Estimador Bayesiano para fusão de informação em comparação com o EE WLS tradicional
"""


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
import matplotlib.pyplot as plt 



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





prec={"SCADAPF":0.02,"SCADAPI":0.02,"SCADAV":0.01,"SMP":0.01,"SMP":0.01,"SMV":0.01,"PSEUDO":0.01,"VIRTUAL":0.01,"PMU_If":0.005,"PMU_Iinj":0.005,"PMUs_V":0.005}


#%%
dfDMEDsr=create_DMED(sys,prec,graph,ram)


prec_PMUs=0.007
prec_SCADAc=0.01

#%%

dfDMED=insert_res(dfDMEDsr)


#%%



dfDMEDSCADA=dfDMED[(dfDMED["prec"]>prec_PMUs)]


#%%

dfDMEDPMU=dfDMED[(dfDMED["prec"]<prec_SCADAc)]

#%%



#%%
conv_WLS_SCADA,nits_WLS_SCADA,dfITsWLS_SCADA=SS_WLS_FACTS_noBC(graph,dfDMEDSCADA,ind_i,flatstart=2,printits=1,tol2=1e-1,tol=1e-4,prec_virtual=1e-4)
#%%


#%%
priori=calc_priori(graph,dfDMEDSCADA,dfDMEDPMU,ind_i)

#%%

conv_MAP,nits_MAP,dfITsMAP=SS_MAP_FACTS_withBC(graph,priori,dfDMEDPMU,ind_i,tol2=7,tol=1e-4,flatstart=1,prec_virtual=1e-4,printits=1)
# %%


conv_noWLS,nits_noWLS,dfITsWLS=SS_WLS_FACTS_noBC(graph,dfDMED,ind_i,flatstart=2,printits=1,tol2=1e-1,tol=1e-4,prec_virtual=1e-4)


# %%



fig, ax = plt.subplots(nrows=1,ncols=1,figsize=(6,4))

fig.tight_layout()


ax.set_ylim([1e-7,2])


ax.set_xticks(range(0,10))


ax.set_xlim([0,9])

ax.grid()

ax.set_title("Convergence charcateristics")

ax.set_xlabel("Iteration")
ax.set_ylabel(r"$\vert \vert \Delta x \vert \vert$")

ax.semilogy(dfITsWLS_SCADA.index,dfITsWLS_SCADA["dx"],marker='d',label="MAP SCADA")
ax.semilogy(dfITsMAP.index,dfITsMAP["dx"],marker='o',label="MAP PMU")
ax.semilogy(dfITsWLS.index,dfITsWLS["dx"],marker='x',label="WLS SCADA+PMU")
ax.legend()
# %%
