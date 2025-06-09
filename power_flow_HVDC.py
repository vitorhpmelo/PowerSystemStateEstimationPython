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
from networkcalc_dc import *
from BadData import *
import numpy.linalg as liang
import scipy.sparse.linalg as sliang 

sys="case5_2grids_MC"


dfDBAR_dc, dfDBRAN_dc= read_files_DC(sys)

# %%


[bus_dc,nbus_dc,slack,ind_id_dc]=create_bus_dc(dfDBAR_dc)
#%%
[bran_dc,nbran_dc]=create_bran_dc(dfDBRAN_dc,ind_id_dc)

#%%

graph_dc=create_graph_dc(bus_dc,bran_dc)

#%%
power_flow_dc(graph_dc,prt=1,tol=1e-12,inici=1,itmax=20,printgrad=1,printres=1)

# %%
