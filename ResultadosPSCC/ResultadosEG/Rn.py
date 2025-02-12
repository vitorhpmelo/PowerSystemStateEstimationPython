
#%%
# -*- coding: utf-8 -*-



import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.lines as mlines
import numpy as np

def label_df(df):
    for idx, row in df.iterrows():
        if row["Tipo"]==0:
            de=row["de"]
            if de==200:
                de="tcsc"
            df.at[idx,"label"]=r"$P_{"+"{}".format(de)+"}$"
        if row["Tipo"]==1:
            de=row["de"]
            if de==200:
                de="tcsc"
            df.at[idx,"label"]=r"$Q_{"+"{}".format(de)+"}$"
        if row["Tipo"]==2:
            de=row["de"]
            para=row["para"]
            if para == 200:
                para = 3
            if para == 600:
                para = 12
            df.at[idx,"label"]=r"$P_{"+"{:d}-{:d}".format(de,para)+"}$"
        if row["Tipo"]==3:
            de=row["de"]
            para=row["para"]
            if para == 200:
                para = 3
            if para == 600:
                para = 12
            df.at[idx,"label"]=r"$Q_{"+"{:d}-{:d}".format(de,para)+"}$"
        if row["Tipo"]==4:
            de=row["de"]
            df.at[idx,"label"]=r"$V_{:d}$".format(de)
        if row["Tipo"]==10:
            de=row["de"]
            para=3
            df.at[idx,"label"]=r"$X_{"+"{:d}-{:d}".format(de,para)+"}$"
        if row["Tipo"]==11:
            de=row["de"]
            df.at[idx,"label"]=r"$B_{:d}$".format(de)
        if row["Tipo"]==12:
            de=row["de"]
            para=12
            df.at[idx,"label"]=r"$Vsh_{"+"{:d}-{:d}".format(de,para)+"}$"
        if row["Tipo"]==13:
            de=row["de"]
            para=12
            df.at[idx,"label"]=r"$\theta sh_{"+"{:d}-{:d}".format(de,para)+"}$"
        if row["Tipo"]==14:
            de=row["de"]
            para=12
            df.at[idx,"label"]=r"$Vse_{"+"{:d}-{:d}".format(de,para)+"}$"
        if row["Tipo"]==15:
            de=row["de"]
            para=12
            df.at[idx,"label"]=r"$\theta se_{"+"{:d}-{:d}".format(de,para)+"}$"
    return df





dsys={"IEEE14":"14 bus"}
colors=["#D6870D","#099358","#D60D0D","#291C95"]

dfDATA={}

dfx1_cmed=pd.read_csv("dresComMedidas_idx_0.csv")
dfx1_smed=pd.read_csv("dresSemMedidas_idx_0.csv")

#%%
dfx1_cmed.sort_values(by="Rn",ascending=False,inplace=True)
dfx1_smed.sort_values(by="Rn",ascending=False,inplace=True)

#%%
dfx1_cmed["label"]=""
dfx1_smed["label"]=""

#(0-Active Power Injection (p.u.), 1-Reactive Power Injection (p.u.), 2-Active Power flow (p.u.), 3-Reactive Power Flow (p.u.), 4-Voltage Magnitude (p.u.),10 - X TCSC (p.u.),11 - B SVC (p.u.),
# 12 - Voltage Magnitude sh UPFC, 13 - Voltage angle p-sh UPFC,14 - Voltage Magnitude se UPFC, 15 - Voltage angle p-se UPFC )

dfx1_cmed=label_df(dfx1_cmed)
dfx1_smed=label_df(dfx1_smed)


# %%
k=0.55
fig, ax =plt.subplots(ncols=2,nrows=1,figsize=(k*16,k*6))

caso=0
i=0
axprime=ax.copy()
d={0:"a) ",1:"b) "}
fstitle=16
fslabel=16
fslegend=12

xmax=[14,9]

dfx1_cmed=dfx1_cmed[0:10]
dfx1_cmed["med"]=1
dfx1_smed=dfx1_smed[0:10]
dfx1_smed["med"]=0
dfDATA=pd.concat([dfx1_smed,dfx1_cmed])
#%%
for med in [0,1]:

    tit=[r"without $Z_{FACTS}$", r"with $Z_{FACTS}$"]

    ax[i].set_title(d[i]+tit[i],fontsize=fstitle)
    mask1=(dfDATA["med"]==med)
    ax[i].bar(range(len(dfDATA[mask1])),dfDATA[(mask1)]["Rn"],color=colors[1])
    ax[i].set_xticks(range(len(dfDATA[mask1])),labels=dfDATA[(mask1)]["label"],rotation=90)

    ax[i].set_xlabel("Measurement",fontsize=fslabel)
    ax[i].set_ylabel(r"$r^{N}$",fontsize=fslabel,rotation=0)
    ax[i].grid()

    i=i+1
# %%




plt.tight_layout()
plt.savefig("bar_EG.pdf")
#%%