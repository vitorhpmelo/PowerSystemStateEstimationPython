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




data_files="network_data/"
sys=data_files+"IEEE14_rakp2009"





dfDBAR,dfDBRAN,dfDMED,dfDFACTS=read_files(sys) # lê arquivos
#%%

[bars,nbars,pv,pq,ind_i]=create_bus(dfDBAR)
[bran,nbran]=create_bran(dfDBRAN,ind_i)


[ramTCSC,nbranTCSC]=create_TCSC(dfDFACTS,ind_i)

[busSVC,BUS_SVC]=create_SVC(dfDFACTS,ind_i)

[ramUPFC,nbranUPFC]=create_UPFC(dfDFACTS,ind_i)




graph=create_graph(bars,bran)


addTCSCingraph(graph,ramTCSC)

addSVCingraph(graph,busSVC)

addUPFCingraph(graph,ramUPFC)


#%%
power_flow_FACTS(graph,inici=1,prt=1,itmax=20,printgrad=0,printres=1)

#%%

for i in range(len(graph)):
    print("{i} => ({g.V},{g.theta}),".format(i=i+1,g=graph[i]))
#%%
for keys, value in busSVC.items():
    print("{i} => ({g.BSVC})".format(i=value.id,g=value))
#%%
for key, value in ramTCSC.items():
    print("{i} =>  ({g.xtcsc})".format(i=value.id,g=value))
#%%
for i in ramUPFC.items():
    print("{i} => ({g.Vse},{g.t_se},{g.Vsh},{g.t_sh})".format(i=i[1].id,g=i[1]))

#%%
zPf,var_x = create_z_x_loadflow_TCSC(graph)#create z and dinctionary with the variables for the FACTS devices
[z,var_t,var_v]=create_z_x_loadflow(graph)#create z and var_v and var_t for the traditional load flow
var_svc=create_x_loadflow_SVC(graph,var_v)
[z_PUFPC,var_UPFC,var_UPFC_vsh]=create_x_loadflow_UPFC(graph,var_v)
#%%

z=z+zPf+z_PUFPC
#%%

#%%
h=np.zeros(len(z))
calc_h(z,graph,h)
#%%


H=np.zeros((len(z),len(var_t)+len(var_v)))
HTCSC=np.zeros((len(z),len(var_x)))
HSVC=np.zeros((len(z),len(var_svc)))
HUPFC=np.zeros((len(z),3*len(var_UPFC)))
HUPFC_sh=np.zeros((len(z),len(var_UPFC_vsh)))
nvar=len(var_v)+len(var_t)+len(var_x)+len(var_svc)+3*len(var_UPFC)+len(var_UPFC_vsh)
c_UPFC=np.zeros(len(var_UPFC))
C_UPFC=np.zeros((len(var_UPFC),nvar))



calc_H_fp(z,var_t,var_v,graph,H)
calc_H_fp_TCSC(z,var_x,graph,HTCSC)
calc_H_fp_SVC(z,var_svc,graph,HSVC)
calc_H_fp_UPFC(z,var_UPFC,var_UPFC_vsh,graph,HUPFC,HUPFC_sh)
calc_C_fp_UPFC(var_t,var_v,var_x,var_svc,var_UPFC,var_UPFC_vsh,graph,C_UPFC)



Hx=np.concatenate((H,HTCSC,HSVC,HUPFC,HUPFC_sh),axis=1)
Hx=np.concatenate((Hx,C_UPFC),axis=0)

#%%

save_matrix(Hx,"tmp/facts_fp_Hx.csv")

save_measurement_facts_order(z, var_UPFC, filename="tmp/facts_fp_z_order.csv")

save_variable_facts_order(var_t,var_v,var_x,var_svc,var_UPFC,var_UPFC_vsh, filename="tmp/facts_fp_var_order.csv")
# %%
