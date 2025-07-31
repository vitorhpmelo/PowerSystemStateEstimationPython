#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#%%
"""
This script performs AC/DC power flow calculations for hybrid power systems with HVDC links.
It reads system data, builds network structures for both AC and DC grids,
runs iterative power flow calculations, saves measurement data, and executes weighted least squares
state estimation. The script supports bad data detection and loss calculations for converters.
"""
from classes import *
from readfiles import *
from networkstruc import *
from SE import *
from meas_sampl import *
import pandas as pd
import numpy as np
from networkcalc import *
from networkcalc_dc import *
from BadData import *
import numpy.linalg as liang
import scipy.sparse.linalg as sliang 
import numpy as np
import matplotlib.pyplot as plt

def introduce_error_converter_losses(convs_acdc,conv_list=[], error_a=10, error_b=10, error_c=10 ):
    if not conv_list:
        conv_list = range(len(convs_acdc))

    
    error_a = error_a / 100
    error_b = error_b / 100
    error_c = error_c / 100
    d_original_losses={}

    for i in conv_list:
        conv = convs_acdc[i]
        d_original_losses[i] = (conv.a, conv.b, conv.c)
        conv.a = conv.a * (1 + error_a)
        conv.b = conv.b * (1 + error_b)
        conv.c = conv.c * (1 + error_c)

    return d_original_losses


def remove_error_converter_losses(d_original_losses, convs_acdc):

    for key in d_original_losses.keys():
        conv = convs_acdc[key]
        conv.a = d_original_losses[key][0]
        conv.b = d_original_losses[key][1]
        conv.c = d_original_losses[key][2]


sys="case5_2grids"

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



include_conv_nodes_in_graph(graph,ind_i, bran, convs_acdc)

dfDMEAS=create_DMEAS(sys,dfDMEAS_pf=dfDMEAS_pf)
#%%
np.random.seed(42)
# dfDMEAS=insert_res(dfDMEAS)

dfState_ref=get_state(graph)
dfStatedc_ref=get_state_dc(graph_dc)
#%%
df_res=pd.DataFrame()
error_list= [0, 5, 10, 15, 20,25,30]  # Percentage errors to be introduced
for e in error_list:

    d_original_losses=introduce_error_converter_losses(convs_acdc, error_a=e, error_b=e, error_c=e)


    SE_WLS_acdc(graph, graph_dc, convs_acdc, dfDMEAS, ind_i, ind_i_dc, ind_id_conv,scale_virt=0.1)

    remove_error_converter_losses(d_original_losses, convs_acdc)
    dfStateac_se= get_state(graph,df_ref=dfState_ref,sample=e)
    dfStatedc_se= get_state_dc(graph_dc,df_ref=dfStatedc_ref,sample=e)
    dfState_acdc=pd.concat([dfStateac_se, dfStatedc_se])
    dfState_acdc["error"]=np.abs(dfState_acdc["val"] - dfState_acdc["val_ref"])
    df_res=pd.concat([df_res, dfState_acdc])

# %%



#%%

dvars = {"vdc": r"$Vdc$", "v": r"$V$", "t": r"$\theta$"}

fig, axs = plt.subplots(1, len(dvars), figsize=(15, 5), sharey=True)
for i, var in enumerate(dvars.keys()):
    maskvar = df_res["type"] == var
    for e in error_list:
        masksample = df_res["sample"] == e
        mask = maskvar & masksample
        axs[i].plot(df_res[mask]["bus"], df_res[mask]["error"], marker='o', label=f"{e}%")
        axs[i].set_xticks(range(len(df_res[mask])))
    axs[i].set_xlabel('bus')
    axs[i].set_ylabel('Value')
    axs[i].set_title(f'{dvars[var]}')
    axs[i].grid()
    axs[i].legend()
plt.tight_layout()
plt.show()



# %%
