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




sys="case24_3zones_acdc_test"

dfDBUS,dfDBRAN,dfDMEAS,dfDFACTS=read_files(sys)




[bus,nbus,pv,pq,ind_i]=create_bus(dfDBUS)
[bran,nbran]=create_bran(dfDBRAN,ind_i)




graph=create_graph(bus,bran)


#%%
power_flow(graph)



#


print("AC Bus Voltages:")
for node in graph:
    V = getattr(node, 'V', None)
    theta = getattr(node, 'theta', None)
    print(f"  {node.bus.id}, {V},{theta}")
print("\nDC Bus Voltages:")

# %%
