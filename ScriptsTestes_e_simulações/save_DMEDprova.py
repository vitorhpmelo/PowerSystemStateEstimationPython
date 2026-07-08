#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#%%
from src.classes import *
from src.readfiles import *
from src.networkstruc import *
from src.SE import *
from src.meas_sampl import *
import pandas as pd
import numpy as np
from src.networkcalc import *
from src.BadData import *
import numpy.linalg as liang
import scipy.sparse.linalg as sliang 




lst=["A","B","C","D"]
sys="IEEE14_provaJB"
#%%


for item in lst:

    dfDMED=pd.read_csv(sys+"/DMED_"+item+".csv")
        

    dfDMED["medida"]=""
    for idx, row in dfDMED.iterrows():
        if row["type"]==0:
            dfDMED.at[idx,"medida"]="P"+str(int(row["fr"]))
        elif row["type"]==1:
            dfDMED.at[idx,"medida"]="Q"+str(int(row["fr"]))
        elif row["type"]==4:
            dfDMED.at[idx,"medida"]="V"+str(int(row["fr"]))
        elif row["type"]==2:
            dfDMED.at[idx,"medida"]="P"+str(int(row["fr"]))+"-"+str(int(row["to"]))
        elif row["type"]==3:
            dfDMED.at[idx,"medida"]="Q"+str(int(row["fr"]))+"-"+str(int(row["to"]))


    dfDMED[["medida","zmed","sigma"]].to_csv("DMED_prova"+item+".csv",sep="\t",index=None,decimal=",",float_format="%.7f")
#%%