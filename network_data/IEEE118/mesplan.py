#%%
import pandas as pd



DMEDJulio=pd.read_csv("DMEDJulio.csv",header=None)
DMEDJulio.columns=['dump',"sentido","dump2","ram","dump3","val","val2","prec"]
# %%

dfRam=pd.read_csv("ram.csv",header=None)
dfRam.columns=["fr","to"]
dfRam["ID"]=dfRam.index
# %%
flows=[]
for idx, row in DMEDJulio.iterrows():
    k=int(dfRam[dfRam["ID"]==row["ram"]]["fr"])
    m=int(dfRam[dfRam["ID"]==row["ram"]]["to"])
    if "Pkm" in row["sentido"]:
        flows.append(str(k)+"-"+str(m))
    elif "Pmk" in row["sentido"]:
        flows.append(str(m)+"-"+str(k))
# %%
