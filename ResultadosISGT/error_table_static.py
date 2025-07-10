#%%
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
#%%
dfstate=pd.read_csv('state_IEEE14_rakp2009x1SemMedidasesta.csv',index_col=None)
dfstate_FACTS=pd.read_csv('state_FACTS_IEEE14_rakp2009x1SemMedidasesta.csv',index_col=None)

#%%
MAE_WLS_V=np.mean(dfstate[(dfstate["method"]=="WLS")&(dfstate["tipo"]=="v")].error)
MAE_WLS_theta=np.mean(dfstate[(dfstate["method"]=="WLS")&(dfstate["tipo"]=="theta")].error)


MAE_MAP_1_V=np.mean(dfstate[(dfstate["method"]=="MAP_SCADA")&(dfstate["tipo"]=="v")].error)
MAE_MAP_1_theta=np.mean(dfstate[(dfstate["method"]=="MAP_SCADA")&(dfstate["tipo"]=="theta")].error)

MAE_MAP_2_V=np.mean(dfstate[(dfstate["method"]=="MAP_PMU")&(dfstate["tipo"]=="v")].error)
MAE_MAP_2_theta=np.mean(dfstate[(dfstate["method"]=="MAP_PMU")&(dfstate["tipo"]=="theta")].error)

#%%

MAE_WLS_UPFC=np.mean(dfstate_FACTS[(dfstate_FACTS["method"]=="WLS")& dfstate_FACTS["tipo"].str.match("UPFC*")].error)
MAE_WLS_TCSC=np.mean(dfstate_FACTS[(dfstate_FACTS["method"]=="WLS")& dfstate_FACTS["tipo"].str.match("x_tcsc")].error)
MAE_WLS_SVC=np.mean(dfstate_FACTS[(dfstate_FACTS["method"]=="WLS")& dfstate_FACTS["tipo"].str.match("B_svc")].error)
#%%
MAE_MAP_1_UPFC=np.mean(dfstate_FACTS[(dfstate_FACTS["method"]=="MAP_SCADA")& dfstate_FACTS["tipo"].str.match("UPFC*")].error)
MAE_MAP_1_TCSC=np.mean(dfstate_FACTS[(dfstate_FACTS["method"]=="MAP_SCADA")& dfstate_FACTS["tipo"].str.match("x_tcsc")].error)
MAE_MAP_1_SVC=np.mean(dfstate_FACTS[(dfstate_FACTS["method"]=="MAP_SCADA")& dfstate_FACTS["tipo"].str.match("B_svc")].error)
#%%

MAE_MAP_2_UPFC=np.mean(dfstate_FACTS[(dfstate_FACTS["method"]=="MAP_PMU")& dfstate_FACTS["tipo"].str.match("UPFC*")].error)
MAE_MAP_2_TCSC=np.mean(dfstate_FACTS[(dfstate_FACTS["method"]=="MAP_PMU")& dfstate_FACTS["tipo"].str.match("x_tcsc")].error)
MAE_MAP_2_SVC=np.mean(dfstate_FACTS[(dfstate_FACTS["method"]=="MAP_PMU")& dfstate_FACTS["tipo"].str.match("B_svc")].error)

#%%
