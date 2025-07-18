#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#%%
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





sys="case5_2grids"

dfDBUS,dfDBRAN,dfDMEAS,dfDFACTS=read_files(sys)

dfDBUS_dc, dfDBRAN_dc, dfDCONV_acdc= read_files_DC(sys)




#%% network building
[bus,nbus,pv,pq,ind_i]=create_bus(dfDBUS)
[bran,nbran]=create_bran(dfDBRAN,ind_i)


[bus_dc,nbus_dc,slack,ind_i_dc]=create_bus_dc(dfDBUS_dc)

[bran_dc,nbran_dc]=create_bran_dc(dfDBRAN_dc,ind_i_dc)


[conv_acdc,nconv,ind_id_conv]=create_conv_acdc(dfDCONV_acdc,ind_i_dc,ind_i)

graph=create_graph(bus,bran)
graph_dc=create_graph_dc(bus_dc,bran_dc)

addACDCconv_ingraph(graph,graph_dc,conv_acdc)
#%%



power_flow_iterative(graph,graph_dc,conv_acdc)

#%% printing results
print_converter_info(conv_acdc)
print_ac_bus_voltages(graph)
print_dc_bus_voltages(graph_dc)
print_converter_internal_node_voltages(conv_acdc)

# %%


dfDMEAS=save_DMEAS_ac_pf(graph,bran,sys)
#%%

dfDMEAS_dc=save_DMEAS_dc_pf(graph_dc,bran_dc,sys)

# %%
save_DMEAS_dc_pf(conv_acdc)