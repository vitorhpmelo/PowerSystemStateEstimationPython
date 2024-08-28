
#%%
# -*- coding: utf-8 -*-



import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.lines as mlines
import numpy as np


dsys={"IEEE14":"14 bus"}
colors=["#D6870D","#099358","#D60D0D","#291C95"]

dfDATA={}

dfx1_cmed=pd.read_csv("taxa_de_convEGx1ComMedidasv2.csv")
dfx1_smed=pd.read_csv("taxa_de_convEGx1SemMedidasv2.csv")
dfx2_cmed=pd.read_csv("taxa_de_convEGx2ComMedidasv2.csv")
dfx2_smed=pd.read_csv("taxa_de_convEGx2SemMedidasv2.csv")
#%%
dfx1_cmed["ini"]=1
dfx1_smed["ini"]=1
dfx2_cmed["ini"]=2
dfx2_smed["ini"]=2

dfx1_cmed["med"]=1
dfx1_smed["med"]=0
dfx2_cmed["med"]=1
dfx2_smed["med"]=0
dfDATA=pd.concat([dfx1_cmed,dfx1_smed,dfx2_cmed,dfx2_smed])


# %%
k=0.55
fig, ax =plt.subplots(ncols=2,nrows=1,figsize=(k*16,k*6))

caso=0
i=0
axprime=ax.copy()
d={0:"a) ",1:"b) "}
fstitle=18
fslabel=15
fslegend=12

xmax=[14,9]
for med in [0,1]:

    tit=["FACTS not measured", "FACTS measured"]

    ax[i].set_title(d[i]+tit[i],fontsize=fstitle)
    mask1=(dfDATA["caso"]==caso)&(dfDATA["ini"]==1) & (dfDATA["med"]==med)
    mask2=(dfDATA["method"]=="LM")
    ax[i].semilogy(range(len(dfDATA[mask1&mask2])),dfDATA[(mask1)&(mask2)]["dx"],color=colors[1],label="LM",marker="o")
    mask1=(dfDATA["caso"]==caso)&(dfDATA["ini"]==1) & (dfDATA["med"]==med)
    mask2=(dfDATA["method"]=="GN")
    ax[i].semilogy(range(len(dfDATA[mask1&mask2])),dfDATA[(mask1)&(mask2)]["dx"],color=colors[2],label="GN",marker="o")
    mask1=(dfDATA["caso"]==caso)&(dfDATA["ini"]==1) & (dfDATA["med"]==med)
    mask2=(dfDATA["method"]=="GNbc")
    ax[i].semilogy(range(len(dfDATA[mask1&mask2])),dfDATA[(mask1)&(mask2)]["dx"],color=colors[3],label="GNbc",marker="o")
    mask1=(dfDATA["caso"]==caso)&(dfDATA["ini"]==2) & (dfDATA["med"]==med)
    mask2=(dfDATA["method"]=="LM")
    ax[i].semilogy(range(len(dfDATA[mask1&mask2])),dfDATA[(mask1)&(mask2)]["dx"],color=colors[1],label="LM",ls="--",marker="x")
    mask1=(dfDATA["caso"]==caso)&(dfDATA["ini"]==2) & (dfDATA["med"]==med)
    mask2=(dfDATA["method"]=="GN")
    ax[i].semilogy(range(len(dfDATA[mask1&mask2])),dfDATA[(mask1)&(mask2)]["dx"],color=colors[2],label="GN",ls="--",marker="x")
    mask1=(dfDATA["caso"]==caso)&(dfDATA["ini"]==2) & (dfDATA["med"]==med)
    mask2=(dfDATA["method"]=="GNbc")
    
    ax[i].semilogy(range(len(dfDATA[mask1&mask2])),dfDATA[(mask1)&(mask2)]["dx"],color=colors[3],label="GNbc",ls="--",marker="x")
    ax[i].set_xlabel("Iteration",fontsize=fslabel)
    ax[i].set_ylabel(r"$\vert \vert \Delta x \vert \vert$",fontsize=fslabel)
    ax[i].set_xlim(xmin=0,xmax=xmax[i])
    ax[i].set_ylim(ymin=1e-5,ymax=1e1)
    ax[i].grid()
    LM_patch=mpatches.Patch(color=colors[1],label="LM")
    
    GN_patch=mpatches.Patch(color=colors[2],label="GN")
    GNbc_patch=mpatches.Patch(color=colors[3],label="GNbc")
    x1line=mlines.Line2D([],[],color="k",marker="o",label=r"$x^1_0$")
    x2line=mlines.Line2D([],[],color="k",marker="x",ls="--",label=r"$x^2_0$")
    ax[i].legend(handles=[LM_patch,GNbc_patch,GN_patch],loc=3,title=r"$\bf{Method}$",fancybox=False,fontsize=fslegend)
    
    axprime[i]=ax[i].twinx()
    axprime[i].legend(handles=[x1line,x2line],loc=1,title=r"$\bf{Ini}$",fancybox=False,fontsize=fslegend)
    ax[i].get_shared_y_axes().join(ax[i], axprime[i])
    axprime[i].axes.get_yaxis().set_visible(False)
    i=i+1
# %%




plt.tight_layout()
plt.savefig("conv_EG_14_barras.pdf")
#%%