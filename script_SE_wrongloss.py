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



include_conv_nodes_in_graph(graph,ind_i, bran, convs_acdc)

dfDMEAS=create_DMEAS(sys,dfDMEAS_pf=dfDMEAS_pf)
#%%
np.random.seed(30)
dfDMEAS=insert_res(dfDMEAS)

dfState_ref=get_state(graph)
dfStatedc_ref=get_state_dc(graph_dc)
#%%
df_res=pd.DataFrame()
df_resEG=pd.DataFrame()
error_list= [0, 10, 20,30]  # Percentage errors to be introduced
for e in error_list:

    d_original_losses=introduce_error_converter_losses(convs_acdc, error_a=e, error_b=e, error_c=e)
    SE_WLS_acdc(graph, graph_dc, convs_acdc, dfDMEAS, ind_i, ind_i_dc, ind_id_conv,scale_virt=0.1)
    
    dfEG=renorm_acdc(graph, graph_dc, convs_acdc, dfDMEAS, ind_i, ind_i_dc, ind_id_conv, scale_virt=0.1)
    dfEG["sample"]=e
    df_resEG=pd.concat([df_resEG, dfEG])
    dfStateac_se= get_state(graph,df_ref=dfState_ref,sample=e)
    dfStatedc_se= get_state_dc(graph_dc,df_ref=dfStatedc_ref,sample=e)
    dfState_acdc=pd.concat([dfStateac_se, dfStatedc_se])
    dfState_acdc["error"]=np.abs(dfState_acdc["val"] - dfState_acdc["val_ref"])
    df_res=pd.concat([df_res, dfState_acdc])
    remove_error_converter_losses(d_original_losses, convs_acdc)

# %%



#%%

dvars = {"vdc": r"$Vdc$", "v": r"$V$", "t": r"$\theta$"}
k = 0.55

fig, axs = plt.subplots(1, len(dvars), figsize=(16*k, 5*k), sharey=True)

for i, var in enumerate(dvars.keys()):
    maskvar = df_res["type"] == var

    means = []
    labels = []

    for e in error_list:
        masksample = df_res["sample"] == e
        mask = maskvar & masksample

        # Mean error across all buses
        mean_error = df_res[mask]["error"].mean()
        means.append(mean_error)
        labels.append(f"{e}%")

    # Bar plot
    axs[i].bar(labels, means)

    axs[i].set_xlabel('Error level')
    axs[i].set_ylabel('Mean Error')
    axs[i].set_title(f'{dvars[var]}')
    axs[i].ticklabel_format(style='sci', axis='y', scilimits=(0,0))
    axs[i].grid(axis='y')

plt.tight_layout()
plt.savefig("SE_wrongloss.pdf", dpi=1200)
#%%

dvars = {"vdc": r"$Vdc$", "v": r"$V$", "t": r"$\theta$"}
k = 0.55

fig, ax = plt.subplots(figsize=(8*k, 5*k))

x = np.arange(len(error_list))  # positions for error levels
width = 0.25  # width of each bar

for i, (var, label) in enumerate(dvars.items()):
    means = []

    for e in error_list:
        mask = (df_res["type"] == var) & (df_res["sample"] == e)
        mean_error = df_res[mask]["error"].mean()
        means.append(mean_error)

    # shift bars for grouping
    ax.bar(x + i*width, means, width, label=label)

# Center x-ticks
ax.set_xticks(x + width)
ax.set_xticklabels([f"{e}%" for e in error_list])

ax.set_xlabel("Error level")
ax.set_ylabel("Mean Error")
ax.ticklabel_format(style='sci', axis='y', scilimits=(0,0))
ax.grid(axis='y')
ax.legend(title="Variable")

plt.tight_layout()
plt.savefig("SE_wrongloss.pdf", dpi=1200)
#%%

k = 0.55
fig, ax = plt.subplots(figsize=(6*k, 5*k))

x = np.arange(len(error_list))
width = 0.35

# -------- AC (V + theta combined) --------
means_ac = []
for e in error_list:
    mask = (
        (df_res["sample"] == e) &
        (df_res["type"].isin(["v", "t"]))
    )
    means_ac.append(df_res[mask]["error"].mean())

# -------- DC (Vdc) --------
means_dc = []
for e in error_list:
    mask = (
        (df_res["sample"] == e) &
        (df_res["type"] == "vdc")
    )
    means_dc.append(df_res[mask]["error"].mean())

# Plot bars
ax.bar(x - width/2, means_ac, width, label="AC")
ax.bar(x + width/2, means_dc, width, label="DC")

# Formatting
ax.set_xticks(x)
ax.set_xticklabels([f"{e}%" for e in error_list])
ax.set_xlabel("Error level")
ax.set_ylabel("Mean Error")
ax.ticklabel_format(style='sci', axis='y', scilimits=(0,0))
ax.grid(axis='y')
ax.legend()

plt.tight_layout()
plt.savefig("SE_wrongloss_noisy.pdf", dpi=1200)

#%%
# Plot scatter plot of gross errors by samples

plt.figure(figsize=(20, 6))
i=0
for e in error_list:
    mask = (df_resEG["sample"] == e)
    plt.scatter(np.array(df_resEG[mask].index+((i-len(error_list)/2)/len(error_list))), df_resEG[mask]["rn"], label=f"{e}%")
    i+=1
# Draw shaded areas between consecutive indexes for each sample

indices = np.array(df_resEG[mask].index.to_list()) - 0.5
for i in range(len(indices) - 1):
    if i%2 == 0:
        plt.axvspan(indices[i], indices[i+1], color='green', alpha=0.1)



df_resEG[mask].Type

d={0:"P", 1:"Q",2:"Pf",3:"Qf",4:"V",104:"Vdc", 244 :"M",299:"Ploss"}

meas_labels=[]

for (idx,row) in df_resEG[mask].iterrows():
    s=d[row["Type"]]
    s=s+str(row["fr"])
    if row["to"] != -1:
        s=s+"-"+str(row["to"])
    meas_labels.append(s)

plt.xticks(indices+0.5, meas_labels, rotation=90)


plt.xlabel("measurement")
plt.ylabel("Rn")

plt.xlim(-1, max(indices)+1)
plt.legend()
plt.grid(axis="y")
plt.show()

# %%
