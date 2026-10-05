#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#%%
"""
This script performs AC/DC power flow calculations for hybrid power systems with HVDC links.
It reads system data, builds network structures for both AC and DC grids,
runs iterative power flow calculations, saves measurement data, and executes weighted least squares
state estimation. The script supports bad data detection and loss calculations for converters.
"""
from src.classes import *
from src.readfiles import *
from src.networkstruc import *
from src.SE import *
from src.meas_sampl import *
import pandas as pd
import numpy as np
from src.networkcalc import *
from src.networkcalc_dc import *
from src.BadData import *
import numpy.linalg as liang
import scipy.sparse.linalg as sliang 
import numpy as np
import matplotlib.pyplot as plt


data_files="network_data/"
sys=data_files+"case5_2grids"

dfDBUS,dfDBRAN,dfDMEAS,dfDFACTS=read_files(sys)

dfDBUS_dc, dfDBRAN_dc, dfDCONV_acdc= read_files_DC(sys)




#%% network building
[bus,nbus,pv,pq,ind_i]=create_bus(dfDBUS)
[bran,nbran]=create_bran(dfDBRAN,ind_i)


[bus_dc,nbus_dc,slack,ind_i_dc]=create_bus_dc(dfDBUS_dc)

[bran_dc,nbran_dc]=create_bran_dc(dfDBRAN_dc,ind_i_dc)


[convs_acdc,nconv,ind_id_conv]=create_conv_acdc(dfDCONV_acdc,ind_i_dc,ind_i)

graph=create_graph(bus,bran)
graph_dc=create_graph_dc(bus_dc,bran_dc)

add_conv_acdc_ingraph(graph,graph_dc,convs_acdc)
#%%

power_flow_iterative(graph,graph_dc,convs_acdc)
#%%


dfDMEAS_pf=save_DMEAS_acdc(graph,bran, graph_dc, bran_dc, convs_acdc, sys)


#%%
include_conv_nodes_in_graph(graph,ind_i, bran, convs_acdc)

dfDMEASsr=create_DMEAS(sys,dfDMEAS_pf=dfDMEAS_pf)
#%%
# dfDMEAS=insert_res(dfDMEASsr)

dfState_ref=get_state(graph)
dfStatedc_ref=get_state_dc(graph_dc)
#%%
SE_WLS_acdc(graph, graph_dc, convs_acdc, dfDMEAS_pf, ind_i, ind_i_dc, ind_id_conv,scale_virt=0.1,printmat=True)
# %%
dfStateac_se= get_state(graph,df_ref=dfState_ref,sample="SE")
dfStatedc_se= get_state_dc(graph_dc,df_ref=dfStatedc_ref,sample="SE")
#%%
dfState_acdc=pd.concat([dfStateac_se, dfStatedc_se])

#%%
MAE={}

for var in list(set(dfState_acdc["type"].values)):
    MAE[var]=np.mean(np.abs(dfState_acdc[dfState_acdc["type"]==var]["val"] - dfState_acdc[dfState_acdc["type"]==var]["val_ref"]))

# %%
dvars = {"vdc": r"$Vdc$", "V": r"$V$", "t": r"$\theta$"}

plt.figure(figsize=(8, 5))
plt.bar([dvars.get(k, k) for k in MAE.keys()], MAE.values())
plt.xlabel('Variable')
plt.ylabel('Mean Absolute Error (MAE)')
plt.title('MAE per Variable')
plt.tight_layout()
plt.show()
# %%
