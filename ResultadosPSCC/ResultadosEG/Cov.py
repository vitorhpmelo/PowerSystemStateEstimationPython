
#%%
# -*- coding: utf-8 -*-

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.lines as mlines
import numpy as np

def label_df(df):
    for idx, row in df.iterrows():
        if row["type"]==0:
            fr=row["fr"]
            if fr==200:
                fr="tcsc"
            df.at[idx,"label"]=r"$P_{"+"{}".format(fr)+"}$"
        if row["type"]==1:
            fr=row["fr"]
            if fr==200:
                fr="tcsc"
            df.at[idx,"label"]=r"$Q_{"+"{}".format(fr)+"}$"
        if row["type"]==2:
            fr=row["fr"]
            to=row["to"]
            if to == 200:
                to = 3
            if to == 600:
                to = 12
            df.at[idx,"label"]=r"$P_{"+"{:d}-{:d}".format(fr,to)+"}$"
        if row["type"]==3:
            fr=row["fr"]
            to=row["to"]
            if to == 200:
                to = 3
            if to == 600:
                to = 12
            df.at[idx,"label"]=r"$Q_{"+"{:d}-{:d}".format(fr,to)+"}$"
        if row["type"]==4:
            fr=row["fr"]
            df.at[idx,"label"]=r"$V_{:d}$".format(fr)
        if row["type"]==10:
            fr=row["fr"]
            to=3
            df.at[idx,"label"]=r"$X_{"+"{:d}-{:d}".format(fr,to)+"}$"
        if row["type"]==11:
            fr=row["fr"]
            df.at[idx,"label"]=r"$B_{:d}$".format(fr)
        if row["type"]==12:
            fr=row["fr"]
            to=12
            df.at[idx,"label"]=r"$Vsh_{"+"{:d}-{:d}".format(fr,to)+"}$"
        if row["type"]==13:
            fr=row["fr"]
            to=12
            df.at[idx,"label"]=r"$\theta sh_{"+"{:d}-{:d}".format(fr,to)+"}$"
        if row["type"]==14:
            fr=row["fr"]
            to=12
            df.at[idx,"label"]=r"$Vse_{"+"{:d}-{:d}".format(fr,to)+"}$"
        if row["type"]==15:
            fr=row["fr"]
            to=12
            df.at[idx,"label"]=r"$\theta se_{"+"{:d}-{:d}".format(fr,to)+"}$"
    return df



dsys={"IEEE14":"14 bus"}
colors=["#D6870D","#099358","#D60D0D","#291C95"]

dfDATA={}

dfx1_cmed=pd.read_csv("dresComMedidas_idx_0_Cov.csv")
dfx1_smed=pd.read_csv("dresSemMedidas_idx_0_Cov.csv")
dfx1_original=pd.read_csv("dresSemMedidas_idx_Original.csv")
#%%
dfx1_cmed.sort_values(by="dCov",ascending=True,inplace=True)
dfx1_smed.sort_values(by="dCov",ascending=True,inplace=True)

dfx1_original.sort_values(by="dCov",ascending=True,inplace=True)

#%%
dfx1_cmed["label"]=""
dfx1_smed["label"]=""
dfx1_original["label"]=""

#(0-Active Power Injection (p.u.), 1-Reactive Power Injection (p.u.), 2-Active Power flow (p.u.), 3-Reactive Power Flow (p.u.), 4-Voltage Magnitude (p.u.),10 - X TCSC (p.u.),11 - B SVC (p.u.),
# 12 - Voltage Magnitude sh UPFC, 13 - Voltage angle p-sh UPFC,14 - Voltage Magnitude se UPFC, 15 - Voltage angle p-se UPFC )


dfx1_cmed=label_df(dfx1_cmed)
dfx1_smed=label_df(dfx1_smed)
dfx1_original=label_df(dfx1_original)





# %%
k=0.57
fig, ax =plt.subplots(ncols=1,nrows=1,figsize=(k*16,k*5.5))

caso=0
i=0
# axprime=ax.copy()
fstitle=14
fslabel=14
fslegend=13

#%%
ax.set_title(r"Ordered elements of the diagonal of the $\Omega$ matrix",fontsize=fstitle)
ax.semilogy(range(len(dfx1_smed)),dfx1_smed["dCov"],marker="d",color=colors[2],label=r"without $Z_{FCATS}$")
ax.semilogy(range(len(dfx1_cmed)),dfx1_cmed["dCov"],marker="o",color=colors[1],label=r"with $Z_{FCATS}$")
ax.semilogy(range(len(dfx1_original)),dfx1_original["dCov"],marker="x",color=colors[0],label="Traditional IEEE 14")
ax.set_xlabel("Measurements",fontsize=fslabel)
ax.set_ylabel("Cov",fontsize=fslabel)
ax.tick_params(axis="both",labelsize=fslegend)
ax.grid()
ax.legend(fontsize=fslegend)

#%%



plt.tight_layout()
plt.savefig("plot_cov.pdf")
#%%