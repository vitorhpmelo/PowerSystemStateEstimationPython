#%%
import pandas as pd
import matplotlib.pyplot as plt



casos_ler=["cargas"+str(i) for i in range(1,5)]
#%%


#%%

dfV={}
dfteta={}
dfFACTS={}

casos_plot=["caso"+str(i) for i in range(1,5)]
for i in range(len(casos_ler)):
    dfV[casos_plot[i]]=pd.read_csv("errosV_compilados"+casos_ler[i]+".csv")
    dfteta[casos_plot[i]]=pd.read_csv("errosteta_compilados"+casos_ler[i]+".csv")
    dfFACTS[casos_plot[i]]=pd.read_csv("errosFACTS_compilados"+casos_ler[i]+".csv")
#%%

dlambda={}
for i in range(len(casos_ler)):
    dlambda[casos_plot[i]]="10^-{}".format(i)
fig, ax = plt.subplots(nrows=1,ncols=3,figsize=(16,4))

ax[0].set_xlabel("tempo (s)")
ax[0].set_ylabel("MAE")

ax[0].set_title("V")

ax[0].semilogy(dfV["caso1"].index/10,dfV["caso1"].WLS.values,label="WLS",ls=":")

ax[1].set_xlabel("tempo (s)")
ax[1].set_ylabel("MAE")

ax[1].set_title(r"$\theta$")
ax[1].semilogy(dfteta["caso1"].index/10,dfteta["caso1"].WLS,label="WLS",ls=":")


ax[2].set_xlabel("tempo (s)")
ax[2].set_ylabel("MAE")
ax[2].set_title("FACTS")
ax[2].semilogy(dfFACTS["caso1"].index/10,dfFACTS["caso1"].WLS,label="WLS",ls=":")


marker=["d","x","o","+"]

dmark={}
i=0
for caso in casos_plot:
    dmark[caso]=marker[i]
    i=i+1



for caso in casos_plot:
    i=1
    ax[0].semilogy(dfV[caso].index/10,dfV[caso].MAP_PMU.values,label=r"$\lambda$ ="+dlambda[caso],ls="--",marker=dmark[caso])
    ax[1].semilogy(dfteta[caso].index/10,dfteta[caso].MAP_PMU,label=r"$\lambda$="+dlambda[caso],ls="--",marker=dmark[caso])
    ax[2].semilogy(dfFACTS[caso].index/10,dfFACTS[caso].MAP_PMU,label=r"$\lambda=$"+dlambda[caso],ls="--",marker=dmark[caso])
    i=i+1

ax[0].legend()
ax[1].legend()
ax[2].legend()

ax[0].grid()
ax[1].grid()
ax[2].grid()



# %%
