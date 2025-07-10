#%%
import pandas as pd
import matplotlib.pyplot as plt



# casos_ler=["v2cargas"+str(i) for i in range(1,6)]
casos_ler=["v2facts"+str(i) for i in [2,5]]
# casos_ler=casos_ler+["v3cargas1"]
#%%
# casos_ler=["v2cargas5","v2degrau5","v2rampa5","v2facts5"]

#%%

dfV={}
dftheta={}
dfFACTS={}

casos_plot=["caso"+str(i) for i in [2,5]]


for i in range(len(casos_plot)):
    dfV[casos_plot[i]]=pd.read_csv("errosV_compilados"+casos_ler[i]+".csv")
    dftheta[casos_plot[i]]=pd.read_csv("errostheta_compilados"+casos_ler[i]+".csv")
    dfFACTS[casos_plot[i]]=pd.read_csv("errosFACTS_compilados"+casos_ler[i]+".csv")
#%%


dlambda={}
for i in range(len(casos_plot)):
    if casos_plot[i]=="caso5":
        dlambda[casos_plot[i]]=r" $var$"
    else:
        dlambda[casos_plot[i]]="10^-{}".format(i+1)
fig, ax = plt.subplots(nrows=3,ncols=1,figsize=(16,8))

ax[0].set_xlabel("tempo (s)")
ax[0].set_ylabel("MAE")

ax[0].set_title("V")

ax[0].semilogy(dfV["caso2"].index/10,dfV["caso2"].WLS.values,label="WLS",ls=":",marker="s",zorder=2)

ax[1].set_xlabel("tempo (s)")
ax[1].set_ylabel("MAE")

ax[1].set_title(r"$\theta$")
ax[1].semilogy(dftheta["caso2"].index/10,dftheta["caso2"].WLS,label="WLS",ls=":",marker="s",zorder=2)


ax[2].set_xlabel("tempo (s)")
ax[2].set_ylabel("MAE")
ax[2].set_title("FACTS")
ax[2].semilogy(dfFACTS["caso2"].index/10,dfFACTS["caso2"].WLS,label="WLS",ls=":",marker="s",zorder=2)


marker=["d","x","o","+","X"]

dmark={}
i=0
for caso in casos_plot:
    dmark[caso]=marker[i]
    i=i+1



for caso in casos_plot:
    i=1
    ax[0].semilogy(dfV[caso].index/10,dfV[caso].MAP_PMU.values,label=r"$\lambda$ ="+dlambda[caso],ls="--",marker=dmark[caso],zorder=1)
    ax[1].semilogy(dftheta[caso].index/10,dftheta[caso].MAP_PMU,label=r"$\lambda$="+dlambda[caso],ls="--",marker=dmark[caso],zorder=1)
    ax[2].semilogy(dfFACTS[caso].index/10,dfFACTS[caso].MAP_PMU,label=r"$\lambda=$"+dlambda[caso],ls="--",marker=dmark[caso],zorder=1)
    i=i+1

ax[0].legend()
ax[1].legend()
ax[2].legend()

ax[0].grid()
ax[1].grid()
ax[2].grid()

fig.tight_layout()


# %%
