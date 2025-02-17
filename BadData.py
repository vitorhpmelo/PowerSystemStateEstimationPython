"""
Arquivo com as funções utilizadas para cálculos de BadData/Erros Grosseiros 
"""

from classes import *
import numpy as np
import pandas as pd
from readfiles import *
import scipy as scy
import scipy.sparse.linalg as sliang 
import scipy.sparse as sparse 
from networkcalc import *
import numpy.linalg as liang




def calcCovRes(graph,dfDMED,ind_i):
    """
    Baseado nos resultados convergidos do EE realiza-se o calculo da matriz de convariâncias, a partir das medidas e do ultimo valor no graph
    """

    [z,var_t,var_v]=create_z_x(graph,dfDMED,ind_i) #cria os vetores z e x
    
    H=np.zeros((len(z),len(var_t)+len(var_v))) # cria a matriz jacobiana
    W=create_W(z,flag_ones=0,prec_virtual=1e-5) # cria a matriz de ponderação
    calc_H_EE(z,var_t,var_v,graph,H) # calcula o valor da matriz Jacobiana, o valor das variáveis tem q estar no graph
    G=np.matmul(np.matmul(H.T,W),H) # calcula a matriz Ganho
    Ginv=liang.inv(G) #inverte a matriz ganho
    S=np.matmul(np.matmul(H,Ginv),H.T) # Calcula a matriz S 
    Winv=np.diag(1/np.diag(W)) # calcula a matriz S
    Cov=Winv-S # calcula a cov

    return Cov





def renorm(graph,dfDMED,ind_i,cov):
    [z,var_t,var_v]=create_z_x(graph,dfDMED,ind_i) # cria o vetor z e os dicionários das variáveis
    W=create_W(z,flag_ones=0,prec_virtual=1e-5) # cria a matriz W
    dz=np.zeros(len(z)) #aloca o dz
    calc_dz(z,graph,dz) #caclula o dz
    Rn=np.abs(dz)/np.sqrt(np.diag(cov)) #calcula o Rn
    bhat=np.sqrt(1/np.diag(W))*Rn*(1/np.sqrt(np.diag(cov))) #calcula o b chapeu 
    
    zT=[]
    zde=[]
    zpara=[]
    for m in z:
        zT.append(m.type)
        zde.append(graph[m.k].bar.id)
        if m.type ==2 or m.type ==3 or  m.type ==10:
            zpara.append(graph[m.m].bar.id)
        else:
            zpara.append(-1) # cria listas
    d={"Tipo":zT,"de":zde,"para":zpara,"Res":dz,"Rn":Rn,"bhat":bhat} # salva dataframe com resultados
    dfRes=pd.DataFrame(d)
    return dfRes




def calcCovRes_com_FACTS(graph,dfDMED,ind_i):


    
    [z,var_t,var_v]=create_z_x(graph,dfDMED,ind_i) #cria os vetores z e x

    var_x=create_x_TCSC(graph) # cria o dicionário com as variáveis dos TCSCs
    var_svc=create_x_SVC(graph) # cria o dicionário com as variáveis dos SVCs
    [var_UPFC,c_upfc]=create_c_x_UPFC(graph) # cria o dicionário com as variáveis dos UPFC e o vetor c dos upfcs (restrições de igualdade)


    n_teta=len(var_t)
    n_v=len(var_v)
    n_TCSC=len(var_x)
    n_SVC=len(var_svc)
    n_UPFC=len(var_UPFC)
    nvar=n_teta+n_v+n_TCSC+n_SVC+4*n_UPFC


    Htrad=np.zeros((len(z),len(var_t)+len(var_v))) # cria a matriz Jacobiana da parte tradicional 
    HTCSC=np.zeros((len(z),len(var_x))) # cria submatriz Jacbiana para os TCSCs
    HSVC=np.zeros((len(z),len(var_svc))) # cria a submatriz Jacobiana para os SVCs
    UPFC=np.zeros((len(z),4*len(var_UPFC))) # cria a submatriz Jacobiana para os UPFCs
    C_UPFC=np.zeros((len(c_upfc),nvar)) # cria a submatriz das Jacobianas para as restrições dos UPFCs


    W=create_W(z+list(c_upfc),flag_ones=0,prec_virtual=1e-5) #expandir W para caber as c_FACTS
    Whalf=np.diag(np.sqrt(np.diag(W)))
    
    calc_H_EE(z,var_t,var_v,graph,Htrad) #calcula matriz submatriz Jacobiana da parte tradicional
    calc_H_EE_TCSC(z,var_x,graph,HTCSC) #calcula matriz submatriz Jacobiana da parte dos TCSCs
    calc_H_EE_SVC(z,var_svc,graph,HSVC) #calcula matriz submatriz Jacobiana da parte dos SVCs
    calc_H_EE_UPFC(z,var_UPFC,graph,UPFC) #calcula matriz submatriz Jacobiana da parte dos UPFCs
    calc_C_EE_UPFC(var_t,var_v,var_x,var_svc,var_UPFC,graph,C_UPFC) #calcula matriz Jacobiana das restrições de igualdade dos UPFCs
        
    Hx=np.concatenate((Htrad,HTCSC,HSVC,UPFC),axis=1) #concatenta
    H=np.concatenate((Hx,C_UPFC),axis=0)

    A=np.matmul(Whalf,H)

    Q,R =scy.linalg.qr(A,mode="full")
    Rpinv=scy.linalg.pinv(R)
    RTpinv=scy.linalg.pinv(R.T)

    

    G=np.matmul(np.matmul(H.T,W),H) # calcula a matriz Ganho
    Ginv=liang.inv(G) #inverte a matriz ganho
    S=np.matmul(np.matmul(H,Ginv),H.T) # Calcula a matriz S 
    Winv=np.diag(1/np.diag(W)) # calcula a matriz S
    
    

    S2=np.matmul(H,np.matmul(Rpinv,np.matmul(RTpinv,H.T)))
    Cov2=Winv -S2 # a partir da pseudo inversa
    Cov=Winv-S # calcula a cov
    
    return Cov2



def renorm_com_FACTS(graph,dfDMED,ind_i,cov):
    [z,var_t,var_v]=create_z_x(graph,dfDMED,ind_i) # cria o vetor z e os dicionários das variáveis
    
    [var_UPFC,c_upfc]=create_c_x_UPFC(graph) # cria o dicionário com as variáveis dos UPFC e o vetor c dos upfcs (restrições de igualdade)


    
    W=create_W(z+list(c_upfc),flag_ones=0,prec_virtual=1e-5) #expandir W para caber as c_FACTS

    dz=np.zeros(len(z)) #aloca o dz
    calc_dz(z,graph,dz) #caclula o dz
    calc_cUPFC(graph,var_UPFC,c_upfc)
    b=np.append(dz,c_upfc)


    
    Rn=np.abs(b)/np.sqrt(np.abs(np.diag(cov))) #calcula o Rn
    D=np.abs(np.diag(cov))
    for i in range(len(b)):
        if (np.abs(b[i])<1e-5) & (D[i]<1e-18) :
            Rn[i]=0

    bhat=np.sqrt(1/np.diag(W))*(1/np.sqrt(np.abs(np.diag(cov))))*Rn #calcula o b chapeu 
    
    zT=[]
    zde=[]
    zpara=[]
    for m in z:
        zT.append(m.type)
        zde.append(graph[m.k].bar.id)
        if m.type ==2 or m.type ==3 or  m.type ==8 or m.type ==9 or m.type ==10:
            zpara.append(graph[m.m].bar.id)
        else:
            zpara.append(-1) # cria listas
    for m in  var_UPFC.keys(): # restrição de igualdade UPFC
        p,s=m.split("-")
        zT.append(-1)
        zde.append(graph[int(p)].bar.id)
        zpara.append(graph[int(p)].bar.id)

    d={"Tipo":zT,"de":zde,"para":zpara,"Res":b,"Rn":Rn,"bhat":bhat,"dCov":np.diag(cov)} # salva dataframe com resultados
    dfRes=pd.DataFrame(d)
    return dfRes