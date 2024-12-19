from classes import *
import numpy as np
import pandas as pd
from readfiles import *
import scipy.sparse.linalg as sliang 
import scipy.sparse as sparse 
from networkcalc import *
import numpy.linalg as liang
import time as tm
from SS import *


def create_x_z_priori(graph,dfDMED_sl_ant,ind_i,flag_PMU_teta_prx=0):


    z_sl_ant=[]
    var_t={}
    var_v={}
    i=0
    j=0
    for item in graph:
        if (item.bar.type==1 or item.bar.type==2) or flag_PMU_teta_prx==1:
            var_t[item.id]=i
            i=i+1
        var_v[item.id]=j
        j=j+1
    
    for idx,row in dfDMED_sl_ant.iterrows():
        if (int(row["type"])==0) or (int(row["type"])==1) or  (int(row["type"])==4) or  (int(row["type"])==5) or  (int(row["type"])==6) or  (int(row["type"])==7)  or (int(row["type"])==11) :
            mes=meas(ind_i[int(row["de"])],-1,int(row["type"]),row["zmed"],row["prec"])
        else:  
            mes=meas(ind_i[int(row["de"])],ind_i[int(row["para"])],int(row["type"]),row["zmed"],row["prec"])
        z_sl_ant.append(mes)


    var_x=create_x_TCSC(graph)
    var_svc=create_x_SVC(graph)
    [var_UPFC,c_upfc]=create_c_x_UPFC(graph)

    return z_sl_ant,var_t,var_v,var_x,var_svc,var_UPFC,c_upfc
    

def calc_priori(graph,dfDMED_sl_ant,dfDMED_sl_atual,indi):



    flag_PMU_teta_prx=len(dfDMED_sl_atual[dfDMED_sl_atual["type"]==5])>0

    z_sl_ant,var_t,var_v,var_x,var_svc,var_UPFC,c_upfc=create_x_z_priori(graph,dfDMED_sl_ant,indi,flag_PMU_teta_prx=flag_PMU_teta_prx)



    Htrad=np.zeros((len(z_sl_ant),len(var_t)+len(var_v)))
    HTCSC=np.zeros((len(z_sl_ant),len(var_x)))
    HSVC=np.zeros((len(z_sl_ant),len(var_svc)))
    UPFC=np.zeros((len(z_sl_ant),4*len(var_UPFC)))
    n_teta=len(var_t)
    n_v=len(var_v)
    n_TCSC=len(var_x)
    n_SVC=len(var_svc)
    n_UPFC=len(var_UPFC)
    nvar=n_teta+n_v+n_TCSC+n_SVC+4*n_UPFC
    W=create_W(z_sl_ant+list(c_upfc),flag_ones=2) #expandir W para caber as c_FACTS
        
    C_UPFC=np.zeros((len(c_upfc),nvar))


    calc_H_EE(z_sl_ant,var_t,var_v,graph,Htrad) 
    calc_H_EE_TCSC(z_sl_ant,var_x,graph,HTCSC) 
    calc_H_EE_SVC(z_sl_ant,var_svc,graph,HSVC) 
    calc_H_EE_UPFC(z_sl_ant,var_UPFC,graph,UPFC)
    calc_C_EE_UPFC(var_t,var_v,var_x,var_svc,var_UPFC,graph,C_UPFC)
    
    Hx=np.concatenate((Htrad,HTCSC,HSVC,UPFC),axis=1)
    H=np.concatenate((Hx,C_UPFC),axis=0)

    priori=prioriMAP(graph,var_x,var_svc,var_UPFC,flag_priori=1,H=H,W=W)

    return priori





def calc_dx_sl(dx_sl,graph,priori,var_t,var_v,var_x,var_svc,var_UPFC):


    
    for key,item in var_t.items():
        dx_sl[item]=graph[key].teta-priori.no[key].teta
    n_var=len(var_t)
    for key,item in var_v.items():
        dx_sl[item+n_var]=graph[key].V-priori.no[key].V

    n_var=n_var+len(var_v)
    for key,item in var_x.items():
        k=int(key.split("-")[0])
        dx_sl[item+n_var]=graph[k].adjk[key].xtcsc-priori.tcsc[key]

    n_var=n_var+len(var_x)
    for key,item in var_svc.items():
        dx_sl[item+n_var]=graph[key].SVC.BSVC-priori.svc[key]
    
    n_var=n_var+len(var_svc)
    n_upfc=len(var_UPFC)
    for key,item in var_UPFC.items():
        p,s = key.split("-")
        p=int(p)
        dx_sl[item+n_var]=graph[p].bUFPC_adjk[key].t_se-priori.upfc_tse[key]
        dx_sl[n_var+n_upfc+item]=graph[p].bUFPC_adjk[key].t_sh-priori.upfc_tsh[key]
        dx_sl[n_var+2*n_upfc+item]=graph[p].bUFPC_adjk[key].Vse-priori.upfc_Vse[key]
        dx_sl[n_var+3*n_upfc+item]=graph[p].bUFPC_adjk[key].Vsh-priori.upfc_Vsh[key]

        



def ini_var_MAP(graph,priori,mode=0):

    #priori_estimate
    if mode==1:
        i=0
        for no in priori.no:
            graph[i].V=no.V
            graph[i].teta=no.teta
            if graph[i].FlagTCSC==1:
                for key in graph[i].bFACTS_adjk.keys():
                    graph[i].bFACTS_adjk[key].xtcsc=priori.tcsc[key]
                    graph[i].bFACTS_adjk[key].AttY()

            if graph[i].FlagSVC==1:
                graph[i].SVC.BSVC=priori.svc[i]
                graph[i].SVC.attYk()  
            if graph[i].FlagUPFC==1:
                for  key in graph[i].bUFPC_adjk.keys():
                    graph[i].bUFPC_adjk[key].Vse=priori.upfc_Vse[key]
                    graph[i].bUFPC_adjk[key].Vsh=priori.upfc_Vsh[key]
                    graph[i].bUFPC_adjk[key].t_se=priori.upfc_tse[key]
                    graph[i].bUFPC_adjk[key].t_sh=priori.upfc_tsh[key]
            i=i+1



    elif mode==0:

        tetaini=0
        for no in graph:
            if no.bar.type == 0:
                tetaini=no.bar.teta
                break
        
        for i in range(len(graph)):
            graph[i].V=1
            graph[i].teta=tetaini
            if graph[i].FlagTCSC==1:
                for key in graph[i].bFACTS_adjk.keys():
                    graph[i].bFACTS_adjk[key].xtcsc=graph[i].bFACTS_adjk[key].xtcsc_ini
                    graph[i].bFACTS_adjk[key].AttY()
                    key=key.split("-")
                    m=int(key[1])
                    graph[m].V=graph[m].V-0.05
            if graph[i].FlagSVC==1:
                graph[i].SVC.BSVC=graph[i].SVC.Bini
                graph[i].SVC.attYk()  
            if graph[i].FlagUPFC==1:
                for  key in graph[i].bUFPC_adjk.keys():
                    graph[i].bUFPC_adjk[key].Vse= graph[i].bUFPC_adjk[key].Vse_ini
                    graph[i].bUFPC_adjk[key].Vsh=graph[i].bUFPC_adjk[key].Vsh_ini
                    graph[i].bUFPC_adjk[key].t_se=graph[i].bUFPC_adjk[key].t_se_ini
                    graph[i].bUFPC_adjk[key].t_sh=graph[i].bUFPC_adjk[key].t_sh_ini


    elif mode==2:

        tetaini=0
        for no in graph:
            if no.bar.type == 0:
                tetaini=no.bar.teta
                break

        for i in range(len(graph)):
            graph[i].V=graph[i].bar.V
            graph[i].teta=tetaini.bar.teta
            if graph[i].FlagTCSC==1:
                for key in graph[i].bFACTS_adjk.keys():
                    graph[i].bFACTS_adjk[key].xtcsc=graph[i].bFACTS_adjk[key].xtcsc_ini
                    graph[i].bFACTS_adjk[key].AttY()
            if graph[i].FlagSVC==1:
                graph[i].SVC.BSVC=graph[i].SVC.Bini
                graph[i].SVC.attYk()  
            if graph[i].FlagUPFC==1:
                for  key in graph[i].bUFPC_adjk.keys():
                    graph[i].bUFPC_adjk[key].Vse= graph[i].bUFPC_adjk[key].Vse_ini
                    graph[i].bUFPC_adjk[key].Vsh=graph[i].bUFPC_adjk[key].Vsh_ini
                    graph[i].bUFPC_adjk[key].t_se=graph[i].bUFPC_adjk[key].t_se_ini
                    graph[i].bUFPC_adjk[key].t_sh=graph[i].bUFPC_adjk[key].t_sh_ini
    
    if mode==3:
        i=0
        for no in priori.no:
            graph[i].V=no.V+np.random.normal(0,0.01)
            graph[i].teta=no.teta+np.random.normal(0,0.01)
            if graph[i].FlagTCSC==1:
                for key in graph[i].bFACTS_adjk.keys():
                    graph[i].bFACTS_adjk[key].xtcsc=priori.tcsc[key]+np.random.normal(0,0.01)
                    graph[i].bFACTS_adjk[key].AttY()

            if graph[i].FlagSVC==1:
                graph[i].SVC.BSVC=priori.svc[i]+np.random.normal(0,0.001)
                graph[i].SVC.attYk()  
            if graph[i].FlagUPFC==1:
                for  key in graph[i].bUFPC_adjk.keys():
                    graph[i].bUFPC_adjk[key].Vse=priori.upfc_Vse[key]+np.random.normal(0,0.001)
                    graph[i].bUFPC_adjk[key].Vsh=priori.upfc_Vsh[key]+np.random.normal(0,0.001)
                    graph[i].bUFPC_adjk[key].t_se=priori.upfc_tse[key]+np.random.normal(0,0.001)
                    graph[i].bUFPC_adjk[key].t_sh=priori.upfc_tsh[key]+np.random.normal(0,0.001)
            i=i+1








def SS_MAP_FACTS_noBC(graph,priori,dfDMED,ind_i,tol=1e-7,tol2=1e-7,solver="QR",prec_virtual=1e-5,printgrad=1,printres=1,printcond=0,printmat=0,printits=0,prinnormgrad=0,flatstart=-1):
    
    '''
    WLS state estimator with FACTS devices (only TCSC implemented yet)

    @param graph with the informations of the network
    @param prt param indicating if it is printing everyting or not
    @param tol tolerance for the dx atualization of the variables
    @param tol2 tolerance for the gradiente reduction
    @param solver only gain matrix implemented yet
    @param prec_virtual standard deviation of virtual measurements
    @param printcond flag for calculating and printing condition number
    @param printmat flag for calculating and printing the matrix for calculationg the descend direction
    @param flat start, initialization of the state variables, if -1 uses the DC state estimator to intialize the angles and the X, 0 it ujses
    the flat start, 1 it uses the DBAR
    '''
    conv=0
    c1=1e-4 #constant for backintracking
    FACTSini(graph)

    Vinici(graph,flatStart=flatstart,dfDMED=dfDMED,ind_i=ind_i)

    [z,var_t,var_v]=create_z_x(graph,dfDMED,ind_i)
    var_x=create_x_TCSC(graph)
    var_svc=create_x_SVC(graph)
    [var_UPFC,c_upfc]=create_c_x_UPFC(graph)
    #create var UPFC

    if flatstart==2:
        for key in var_x.keys():
            key=key.split("-")
            m=int(key[1])
            graph[m].V=graph[m].V-0.01



    Htrad=np.zeros((len(z),len(var_t)+len(var_v)))
    HTCSC=np.zeros((len(z),len(var_x)))
    HSVC=np.zeros((len(z),len(var_svc)))
    UPFC=np.zeros((len(z),4*len(var_UPFC)))
    n_teta=len(var_t)
    n_v=len(var_v)
    n_TCSC=len(var_x)
    n_SVC=len(var_svc)
    n_UPFC=len(var_UPFC)
    nvar=n_teta+n_v+n_TCSC+n_SVC+4*n_UPFC
    dz=np.zeros(len(z))
    dx_sl=np.zeros(nvar)
    
    W=create_W(z+list(c_upfc),flag_ones=0,prec_virtual=prec_virtual) #expandir W para caber as c_FACTS
    
    C_UPFC=np.zeros((len(c_upfc),nvar))

    it=0
    it2=0
    itmax=2
    lstdx=[]
    lstdz=[]
    lstc_upfc=[]



    while(it <30):
        a=1
        calc_dz(z,graph,dz)


        calc_cUPFC(graph,var_UPFC,c_upfc)
        calc_H_EE(z,var_t,var_v,graph,Htrad) 
        calc_H_EE_TCSC(z,var_x,graph,HTCSC) 
        calc_H_EE_SVC(z,var_svc,graph,HSVC) 
        calc_H_EE_UPFC(z,var_UPFC,graph,UPFC)
        calc_C_EE_UPFC(var_t,var_v,var_x,var_svc,var_UPFC,graph,C_UPFC)
        

        calc_dx_sl(dx_sl,graph,priori,var_t,var_v,var_x,var_svc,var_UPFC)
        
        Hx=np.concatenate((Htrad,HTCSC,HSVC,UPFC),axis=1)
        H=np.concatenate((Hx,C_UPFC),axis=0)
        b=np.append(dz,c_upfc)
            
        gradWLS=-np.matmul(np.matmul(H.T,W),b)

        gradMAP=gradWLS+priori.P_inv@dx_sl


        try: 
            dx=NormalEQ_MAP(H,W,gradMAP,priori.P_inv,printcond=printcond,printmat=printmat)
        except:
            conv=0
            it=30
            break

        Jxk=np.matmul(np.matmul(b,W),b)
        if it==0:
            norminicial=liang.norm(gradMAP)

        new_X(graph,var_t,var_v,a*dx)
        new_X_TCSC(graph,len(var_t)+len(var_v),var_x,a*dx)
        new_X_SVC(graph,len(var_t)+len(var_v)+len(var_x),var_svc,a*dx)
        new_X_EE_UPFC(graph,len(var_t)+len(var_v)+len(var_x)+len(var_svc),var_UPFC,a*dx)
        calc_dz(z,graph,dz)
        calc_cUPFC(graph,var_UPFC,c_upfc)
        b=np.append(dz,c_upfc)
        Jxn=np.matmul(np.matmul(b,W),b)

        if printgrad==True:
            print("{:e},{:e}".format( liang.norm(gradMAP)/norminicial,liang.norm(a*dx)))
        gradredux=liang.norm(gradMAP)/norminicial
        maxdx= liang.norm(a*dx)
        lstdx.append(maxdx)
        lstdz.append(gradredux)
        if maxdx>1e3:
            conv=0
            it=30
            break
        if gradredux <tol2 and maxdx<tol:
            txt="Convergiu em {:d} iteracoes".format(it)
            upfc_angle(graph)
            if printres==True:
                print(liang.norm(gradMAP)/norminicial)
                print(txt)
                prt_state(graph)
                prt_state_FACTS(graph,var_x,var_svc,var_UPFC)
            conv=1
            break

        it=it+1


    if printits==1:
        iterdict={"dx":lstdx,"dz":lstdz}
        dfits = pd.DataFrame(iterdict)

        # Save the DataFrame to a CSV file
        dfits.to_csv('conv_GN.csv', index=False)
    elif printits==2:
        iterdict={"dx":lstdx,"dz":lstdz}
        dfits = pd.DataFrame(iterdict)
    else:
        dfits=[]
    return conv,it,dfits



def SS_MAP_FACTS_noBC(graph,priori,dfDMED,ind_i,tol=1e-7,tol2=1e-7,solver="QR",prec_virtual=1e-5,printgrad=1,printres=1,printcond=0,printmat=0,printits=0,prinnormgrad=0,flatstart=-1):
    
    '''
    WLS state estimator with FACTS devices (only TCSC implemented yet)

    @param graph with the informations of the network
    @param prt param indicating if it is printing everyting or not
    @param tol tolerance for the dx atualization of the variables
    @param tol2 tolerance for the gradiente reduction
    @param solver only gain matrix implemented yet
    @param prec_virtual standard deviation of virtual measurements
    @param printcond flag for calculating and printing condition number
    @param printmat flag for calculating and printing the matrix for calculationg the descend direction
    @param flat start, initialization of the state variables, if -1 uses the DC state estimator to intialize the angles and the X, 0 it ujses
    the flat start, 1 it uses the DBAR
    '''
    conv=0
    c1=1e-4 #constant for backintracking
    FACTSini(graph)

    Vinici(graph,flatStart=flatstart,dfDMED=dfDMED,ind_i=ind_i)

    [z,var_t,var_v]=create_z_x(graph,dfDMED,ind_i)
    var_x=create_x_TCSC(graph)
    var_svc=create_x_SVC(graph)
    [var_UPFC,c_upfc]=create_c_x_UPFC(graph)
    #create var UPFC

    if flatstart==2:
        for key in var_x.keys():
            key=key.split("-")
            m=int(key[1])
            graph[m].V=graph[m].V-0.01



    Htrad=np.zeros((len(z),len(var_t)+len(var_v)))
    HTCSC=np.zeros((len(z),len(var_x)))
    HSVC=np.zeros((len(z),len(var_svc)))
    UPFC=np.zeros((len(z),4*len(var_UPFC)))
    n_teta=len(var_t)
    n_v=len(var_v)
    n_TCSC=len(var_x)
    n_SVC=len(var_svc)
    n_UPFC=len(var_UPFC)
    nvar=n_teta+n_v+n_TCSC+n_SVC+4*n_UPFC
    dz=np.zeros(len(z))
    dx_sl=np.zeros(nvar)
    
    W=create_W(z+list(c_upfc),flag_ones=0,prec_virtual=prec_virtual) #expandir W para caber as c_FACTS
    
    C_UPFC=np.zeros((len(c_upfc),nvar))

    it=0
    it2=0
    itmax=2
    lstdx=[]
    lstdz=[]
    lstc_upfc=[]



    while(it <30):
        a=1
        calc_dz(z,graph,dz)


        calc_cUPFC(graph,var_UPFC,c_upfc)
        calc_H_EE(z,var_t,var_v,graph,Htrad) 
        calc_H_EE_TCSC(z,var_x,graph,HTCSC) 
        calc_H_EE_SVC(z,var_svc,graph,HSVC) 
        calc_H_EE_UPFC(z,var_UPFC,graph,UPFC)
        calc_C_EE_UPFC(var_t,var_v,var_x,var_svc,var_UPFC,graph,C_UPFC)
        

        calc_dx_sl(dx_sl,graph,priori,var_t,var_v,var_x,var_svc,var_UPFC)
        
        Hx=np.concatenate((Htrad,HTCSC,HSVC,UPFC),axis=1)
        H=np.concatenate((Hx,C_UPFC),axis=0)
        b=np.append(dz,c_upfc)
            
        gradWLS=-np.matmul(np.matmul(H.T,W),b)

        gradMAP=gradWLS+priori.P_inv@dx_sl


        try: 
            dx=NormalEQ_MAP(H,W,gradMAP,priori.P_inv,printcond=printcond,printmat=printmat)
        except:
            conv=0
            it=30
            break

        Jxk=np.matmul(np.matmul(b,W),b)
        if it==0:
            norminicial=liang.norm(gradMAP)

        new_X(graph,var_t,var_v,a*dx)
        new_X_TCSC(graph,len(var_t)+len(var_v),var_x,a*dx)
        new_X_SVC(graph,len(var_t)+len(var_v)+len(var_x),var_svc,a*dx)
        new_X_EE_UPFC(graph,len(var_t)+len(var_v)+len(var_x)+len(var_svc),var_UPFC,a*dx)
        calc_dz(z,graph,dz)
        calc_cUPFC(graph,var_UPFC,c_upfc)
        b=np.append(dz,c_upfc)
        Jxn=np.matmul(np.matmul(b,W),b)

        if printgrad==True:
            print("{:e},{:e}".format( liang.norm(gradMAP)/norminicial,liang.norm(a*dx)))
        gradredux=liang.norm(gradMAP)/norminicial
        maxdx= liang.norm(a*dx)
        lstdx.append(maxdx)
        lstdz.append(gradredux)
        if maxdx>1e3:
            conv=0
            it=30
            break
        if gradredux <tol2 and maxdx<tol:
            txt="Convergiu em {:d} iteracoes".format(it)
            upfc_angle(graph)
            if printres==True:
                print(liang.norm(gradMAP)/norminicial)
                print(txt)
                prt_state(graph)
                prt_state_FACTS(graph,var_x,var_svc,var_UPFC)
            conv=1
            break

        it=it+1


    if printits==1:
        iterdict={"dx":lstdx,"dz":lstdz}
        dfits = pd.DataFrame(iterdict)

        # Save the DataFrame to a CSV file
        dfits.to_csv('conv_GN.csv', index=False)
    elif printits==2:
        iterdict={"dx":lstdx,"dz":lstdz}
        dfits = pd.DataFrame(iterdict)
    else:
        dfits=[]
    return conv,it,dfits



def SS_MAP_FACTS_withBC(graph,priori,dfDMED,ind_i,tol=1e-7,tol2=1e-7,solver="QR",prec_virtual=1e-5,printgrad=1,printres=1,printcond=0,printmat=0,printits=0,prinnormgrad=0,flatstart=0):
    
    '''
    WLS state estimator with FACTS devices (only TCSC implemented yet)

    @param graph with the informations of the network
    @param prt param indicating if it is printing everyting or not
    @param tol tolerance for the dx atualization of the variables
    @param tol2 tolerance for the gradiente reduction
    @param solver only gain matrix implemented yet
    @param prec_virtual standard deviation of virtual measurements
    @param printcond flag for calculating and printing condition number
    @param printmat flag for calculating and printing the matrix for calculationg the descend direction
    @param flat start, initialization of the state variables, if -1 uses the DC state estimator to intialize the angles and the X, 0 it ujses
    the flat start, 1 it uses the DBAR
    '''
    conv=0
    c1=1e-4 #constant for backintracking


    ini_var_MAP(graph,priori,mode=flatstart)

    [z,var_t,var_v]=create_z_x(graph,dfDMED,ind_i)
    var_x=create_x_TCSC(graph)
    var_svc=create_x_SVC(graph)
    [var_UPFC,c_upfc]=create_c_x_UPFC(graph)
    #create var UPFC




    Htrad=np.zeros((len(z),len(var_t)+len(var_v)))
    HTCSC=np.zeros((len(z),len(var_x)))
    HSVC=np.zeros((len(z),len(var_svc)))
    UPFC=np.zeros((len(z),4*len(var_UPFC)))
    n_teta=len(var_t)
    n_v=len(var_v)
    n_TCSC=len(var_x)
    n_SVC=len(var_svc)
    n_UPFC=len(var_UPFC)
    nvar=n_teta+n_v+n_TCSC+n_SVC+4*n_UPFC
    dz=np.zeros(len(z))
    dx_sl=np.zeros(nvar)
    
    W=create_W(z+list(c_upfc),flag_ones=2,prec_virtual=prec_virtual) #expandir W para caber as c_FACTS
    
    C_UPFC=np.zeros((len(c_upfc),nvar))

    it=0
    it2=0
    itmax=10
    lstdx=[]
    lstdz=[]
    lstc_upfc=[]



    while(it <30):
        a=1
        calc_dz(z,graph,dz)

        calc_cUPFC(graph,var_UPFC,c_upfc)
        calc_H_EE(z,var_t,var_v,graph,Htrad) 
        calc_H_EE_TCSC(z,var_x,graph,HTCSC) 
        calc_H_EE_SVC(z,var_svc,graph,HSVC) 
        calc_H_EE_UPFC(z,var_UPFC,graph,UPFC)
        calc_C_EE_UPFC(var_t,var_v,var_x,var_svc,var_UPFC,graph,C_UPFC)
        

        calc_dx_sl(dx_sl,graph,priori,var_t,var_v,var_x,var_svc,var_UPFC)


        
        Hx=np.concatenate((Htrad,HTCSC,HSVC,UPFC),axis=1)
        H=np.concatenate((Hx,C_UPFC),axis=0)
        b=np.append(dz,c_upfc)
            
        gradWLS=-np.matmul(np.matmul(H.T,W),b)

        gradMAP=gradWLS+priori.P_inv@dx_sl


        try: 
            dx=NormalEQ_MAP(H,W,gradMAP,priori.P_inv,printcond=printcond,printmat=printmat)
            # dx=NormalEQ_MAP_QR(H,W,priori,b,dx_sl)
            
        except:
            conv=0
            it=30
            break



        Jxk=np.matmul(np.matmul(b,W),b) + np.matmul(np.matmul(dx_sl,priori.P_inv),dx_sl)


        if it==0:
            norminicial=liang.norm(gradMAP)
        it2=0
        while it2<itmax:
            
            new_X(graph,var_t,var_v,a*dx)
            new_X_TCSC(graph,len(var_t)+len(var_v),var_x,a*dx)
            new_X_SVC(graph,len(var_t)+len(var_v)+len(var_x),var_svc,a*dx)
            new_X_EE_UPFC(graph,len(var_t)+len(var_v)+len(var_x)+len(var_svc),var_UPFC,a*dx)
            calc_dz(z,graph,dz)
            calc_cUPFC(graph,var_UPFC,c_upfc)
            calc_dx_sl(dx_sl,graph,priori,var_t,var_v,var_x,var_svc,var_UPFC)

            b=np.append(dz,c_upfc)
            Jxn=np.matmul(np.matmul(b,W),b)  + np.matmul(np.matmul(dx_sl,priori.P_inv),dx_sl)
            it2=it2+1
            if it2==itmax:
                break
            if Jxn < Jxk + c1*a*np.dot(gradMAP,dx):
                break
            else:
                new_X(graph,var_t,var_v,-a*dx)
                new_X_TCSC(graph,len(var_t)+len(var_v),var_x,-a*dx)
                new_X_SVC(graph,len(var_t)+len(var_v)+len(var_x),var_svc,-a*dx)
                new_X_EE_UPFC(graph,len(var_t)+len(var_v)+len(var_x)+len(var_svc),var_UPFC,-a*dx)
                a=a/2
        if printgrad==True:   
            print("{:e},{:e},{:e}".format( liang.norm(gradMAP)/norminicial,liang.norm(dx),Jxk))
        gradredux=liang.norm(gradMAP)/norminicial
        maxdx= liang.norm(dx)

        lstdx.append(maxdx)
        lstdz.append(gradredux)
        if maxdx>1e100:
            conv=0
            it=30
            break
        if gradredux <tol2 and maxdx<tol:
            txt="Convergiu em {:d} iteracoes".format(it)
            upfc_angle(graph)
            if printres==True:
                print(liang.norm(gradMAP)/norminicial)
                print(txt)
                prt_state(graph)
                prt_state_FACTS(graph,var_x,var_svc,var_UPFC)
            conv=1
            break

        it=it+1


    if printits==1:
        iterdict={"dx":lstdx,"dz":lstdz}
        dfits = pd.DataFrame(iterdict)

        # Save the DataFrame to a CSV file
        dfits.to_csv('conv_GN.csv', index=False)
    elif printits==2:
        iterdict={"dx":lstdx,"dz":lstdz}
        dfits = pd.DataFrame(iterdict)
    else:
        dfits=[]
    return conv,it,dfits