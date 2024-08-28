
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
k=0.55
fig, ax =plt.subplots(ncols=1,nrows=1,figsize=(k*16,k*5))

caso=0
i=0
# axprime=ax.copy()
fstitle=18
fslabel=15
fslegend=12

#%%
ax.set_title(r"Ordered elements of the diagonal of the $\Omega$ matrix")
ax.semilogy(range(len(dfx1_smed)),dfx1_smed["dCov"],marker="d",color=colors[2],label="FACTS not monitored")
ax.semilogy(range(len(dfx1_cmed)),dfx1_cmed["dCov"],marker="o",color=colors[1],label="FACTS monitored")
ax.semilogy(range(len(dfx1_original)),dfx1_original["dCov"],marker="x",color=colors[0],label="Traditional IEEE 14")
ax.set_xlabel("Measurments")
ax.set_ylabel("Cov")
ax.grid()
ax.legend()

#%%



plt.tight_layout()
plt.savefig("plot_cov.pdf")
#%%