#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Classes used in the SE
"""


import numpy as np

class bus():
    def __init__(self,id,type,counter):
        self.id=id
        self.type=type
        self.i=counter
        self.V=1
        self.theta=0
        self.Sbase=100
        self.Vbase=138
        self.Pg=0
        self.Qg=0
        self.Pd=0
        self.Qd=0
        self.Bs=0
        self.nloads=0
        self.nshunts=0
        self.ngds=0


class bus_dc():
    def __init__(self,id,type,counter):
        self.id=id
        self.type=type
        self.i=counter
        self.Vdc=1
        self.Pbase=100
        self.Vbase=345
        self.Pdc_conv=0
        self.Pdc_load=0
        self.Pdc_gen=0
        self.area=1

class conv_acdc():
    def __init__(self,id,islcc,counter):
        self.id=id #converter id
        self.islcc=islcc #converter type, 1 for LCC, 2 for VSC and 3 for MMC 
        self.i=counter #converter number 
        self.id_busac=-1 #external name bus ac grid connected to the converter
        self.id_busdc=-1 #external name bus dc grid connected to the converter
        self.i_busac=-1 # internal (graph) bus ac grid connected to the converter
        self.i_busdc=-1 # internal (graph) bus dc grid connected to the converter
        self.i_busconv=-1
        self.i_busfilter=-1
        self.key_tf=""
        self.key_rc=""
        self.type_ac=1 # type of the ac bus (defines the controll of the VSC ) 
        self.type_dc=1 # type of the dc bus which is connected to
        self.P_grid=0 # set point of the active powers injected in the grid
        self.Q_grid=0 # set point of the reactiva powers injected in the grid 
        self.Vac_grid=1 #set point of the DC grid voltage
        self.flag_trans=1 # informs if there is a transformer
        self.xtf=0.01 # transformer reactance 
        self.rtf=0.01 # transformer resistence
        self.tap=1 # transformer tap ratio
        self.flag_filter=1 # informs existence of the filter 
        self.bf=0.01 # filter susceptance
        self.flag_reactor=1 # informs existence of reactor 
        self.xc=0.01 # reactor reactance  
        self.rc=0.01 # reactor resistance
        self.Vdc=1 # voltage in the DC bus
        self.Pbase=100 #active power base
        self.Vbase=345         # Base voltage for DC side (kV)
        self.a=0               # Losses constant intercept
        self.b=0               # Losses constant linear
        self.crec=0            # Losses constant quadratic reactor
        self.cinv=0            # Losses constant quadratic inverter
        self.c=0               # Losses constant c
        self.Pdc=0             # DC power
        self.Iconv=0           # Converter current
        self.Ploss=0           # Converter losses
        self.Pconv_ac=0        # Converter AC side active power
        self.Qconv_ac=0        # Converter AC side reactive power
        self.Pgrid=0           # Converter Injection to the grid
        self.Qgrid=0           # Converter Injection to the grid 
        self.Pgset=0         # Set points of the active and reactive power in the converter
        self.Qgset=0         # Set points of the active and reactive power in the converter
        self.d_inter_nodes={} #list of the internal nodes created by the converter
        self.d_inter_bran={} #list of the internal branches created by the converter        
    def create_internal_network(self,graph):
        if (self.flag_trans==0) & (self.flag_reactor==0):
            OSError("Error: transformer or filter must be present in the converter") #TODO implement converter without transformer or filter
    
        i_bus_conv=2 #converter bus 
        i_bus_filter=1 #converter filter bus 
        i_bus_grid=0 # converter grid bus
        
        bus_conv=bus(id=str(self.id)+"_"+str(i_bus_conv),type=4,counter=0) #TODO formal definition of the bus type 4 (converter bus)
        
        #get the node of the ac grid connected to the converter    
        
        node_conv=node_graph(i_bus_conv,bus_conv)
        self.d_inter_nodes.update({i_bus_conv:node_conv})
        # graph.append(node_conv) #TODO see if it is necessary to append the node in the graph
        

        if (self.flag_trans==1) & (self.flag_reactor==1):
    
            bus_filt=bus(id=str(self.id)+"_"+str(i_bus_filter),type=5,counter=i_bus_filter)  #TODO formal definition of the bus type 4 (filter bus)
           
            node_filt=node_graph(i_bus_filter,bus_filt)

            if self.flag_filter==1:
                bus_filt.Bs=self.bf #set the filter susceptance
                node_filt.FlagBS=1 #set the flag of the filter bus
                node_filt.Bs=self.bf #set the filter susceptance in the filter bus
                        
            # graph.append(node_filt) #TODO see if it is necessary to append the node in the graph
            self.d_inter_nodes.update({i_bus_filter:node_filt})

        else:
            if self.flag_filter==1:
                bus_conv.Bs=self.bf #set the filter susceptance in the converter bus
                node_conv.FlagBS=1 #set the flag of the converter bus
                node_conv.Bs=self.bf #set the filter susceptance in the converter bus


        self.d_inter_nodes.update({i_bus_grid:graph[self.i_busac]}) #inserts the grid bus in the internal ac network of the converter 


        if (self.flag_trans==1) & (self.flag_reactor==1):
            
            tr=branch(0,i_bus_grid,i_bus_filter,2,0)

            tr.x=self.xtf
            tr.r=self.rtf
            tr.bsh=0 #divides the shunt suceptance by two
            tr.tap=self.tap
            tr.cykm()#calculates the ykm
            tr.twoPortCircuit()#creates the two port circuit
            self.d_inter_bran.update({0:tr})

            rc=branch(1,i_bus_filter,i_bus_conv,1,1)
            rc.x=self.xc
            rc.r=self.rc
            rc.bsh=0 #divides the shunt suceptance by two
            rc.cykm()#calculates the ykm
            rc.twoPortCircuit()#creates the two port circuit
            self.d_inter_bran.update({1:rc})
            node_filt.adjm.update({0:tr})
            node_filt.adjk.update({1:rc})

        elif (self.flag_trans==1) :

            tr=branch(0,i_bus_grid,i_bus_conv,2,0)

            tr.x=self.xtf
            tr.r=self.rtf
            tr.bsh=0 #divides the shunt suceptance by two
            tr.tap=self.tap
            tr.cykm()#calculates the ykm
            tr.twoPortCircuit()#creates the two port circuit
            self.d_inter_bran.update({0:tr})

        elif (self.flag_reactor==1):
            rc=branch(1,i_bus_grid,i_bus_conv,1,1)
            rc.x=self.xc
            rc.r=self.rc
            rc.bsh=0 #divides the shunt suceptance by two
            rc.cykm()#calculates the ykm
            rc.twoPortCircuit()#creates the two port circuit
            self.d_inter_bran.update({1:rc})
    
    def include_Sgrid_set_points(self,graph):

        graph[self.i_busac].Pd=graph[self.i_busac].Pd-self.P_grid
        graph[self.i_busac].Qd=graph[self.i_busac].Pd-self.Q_grid #set the active power injected in the grid

    def Ptf(self,FlagT):
        return self.d_inter_bran[0].Pf(self.d_inter_nodes,FlagT)
    def Qtf(self,FlagT):
        return self.d_inter_bran[0].Qf(self.d_inter_nodes,FlagT)
    def Itf_re(self,FlagT):
        return self.d_inter_bran[0].Iref(self.d_inter_nodes,FlagT)
    def Itf_im(self,FlagT):
        return self.d_inter_bran[0].Iimf(self.d_inter_nodes,FlagT)
    def Prc(self,FlagT):
        return self.d_inter_bran[1].Pf(self.d_inter_nodes,FlagT)
    def Qrc(self,FlagT):
        return self.d_inter_bran[1].Qf(self.d_inter_nodes,FlagT)
    def Irc_re(self,FlagT):
        return self.d_inter_bran[1].Iref(self.d_inter_nodes,FlagT)
    def Irc_im(self,FlagT):
        return self.d_inter_bran[1].Iimf(self.d_inter_nodes,FlagT)
    def Pvirt(self): #filter bus virtual injection
        return self.d_inter_nodes[1].P(self.d_inter_nodes)
    def Qvirt(self): #filter bus virtual injection
        return self.d_inter_nodes[1].Q(self.d_inter_nodes)
    def Iconv_se(self,graph):
        Iconv_re=0
        Iconv_im=0
        if graph[self.i_busconv].FlagBS==1:
            Iconv_re += graph[self.i_busconv].V*(-graph[self.i_busconv].Bs*np.sin(graph[self.i_busconv].theta))
            Iconv_im += graph[self.i_busconv].V*(graph[self.i_busconv].Bs*np.cos(graph[self.i_busconv].theta))
        for (key,item) in graph[self.i_busconv].adjk.items():
            Iconv_re += item.Iref(graph,0)
            Iconv_im += item.Iimf(graph,0)
        for (key,item) in graph[self.i_busconv].adjm.items():
            Iconv_re += item.Iref(graph,1)
            Iconv_im += item.Iimf(graph,1)

        return Iconv_re, Iconv_im

    def Ploss_se(self,graph):
        Iconv_re, Iconv_im = self.Iconv_se(graph)
        Iconv = np.sqrt(Iconv_re**2 + Iconv_im**2)
        return self.a + self.b*Iconv + self.c*Iconv**2
    
    def Pac_se(self,graph):
        return graph[self.i_busconv].P(graph)
    def Pdc_se(self,graph_dc):
        return graph_dc[self.i_busdc].Pdc(graph_dc)


        
    




        



            


class branch():
    def __init__(self,id,fr,to,type,i):
        self.id=id
        self.fr=fr
        self.to=to
        self.type=type
        self.i=i
        self.x=-1
        self.r=-1
        self.ykm=0
        self.Y=np.zeros((2,2),dtype=complex)
        self.bsh=-1
        self.tap=-1
        self.limPA=-999
        self.flagLimP=0
    def cykm(self):
        self.ykm=1/complex(self.r,self.x)
    def twoPortCircuit(self):
        if self.type == 1:
            self.Y[0][0]=self.ykm+self.bsh
            self.Y[1][1]=self.ykm+self.bsh
            self.Y[1][0]=-self.ykm
            self.Y[0][1]=-self.ykm
        elif self.type ==2:
            self.Y[0][0]=((1/self.tap)**2)*self.ykm
            self.Y[1][1]=self.ykm
            self.Y[1][0]=-(1/self.tap)*self.ykm
            self.Y[0][1]=-(1/self.tap)*self.ykm
    def Pf(self,graph,flagT):
        k=self.fr
        m=self.to
        if flagT==0:
            P=(graph[k].V**2)*np.real(self.Y[0][0]) + graph[k].V* graph[m].V*(\
            np.real(self.Y[0][1])*np.cos(graph[k].theta-graph[m].theta)\
            +np.imag(self.Y[0][1])*np.sin(graph[k].theta-graph[m].theta))
            return P
        elif flagT==1:
            P=(graph[m].V**2)*np.real(self.Y[1][1]) + graph[m].V* graph[k].V*(\
            np.real(self.Y[1][0])*np.cos(graph[m].theta-graph[k].theta)\
            +np.imag(self.Y[0][1])*np.sin(graph[m].theta-graph[k].theta))
            return P
        else:
            return 0
    def Qf(self,graph,flagT):
        k=self.fr
        m=self.to
        if flagT==0:
            Qf=-(graph[k].V**2)*np.imag(self.Y[0][0]) - graph[k].V* graph[m].V*(\
            np.imag(self.Y[0][1])*np.cos(graph[k].theta-graph[m].theta)\
            -np.real(self.Y[0][1])*np.sin(graph[k].theta-graph[m].theta))
            return Qf
        elif flagT==1:
            Qf=-(graph[m].V**2)*np.imag(self.Y[1][1]) - graph[m].V* graph[k].V*(\
            np.imag(self.Y[1][0])*np.cos(graph[m].theta-graph[k].theta)\
            -np.real(self.Y[1][0])*np.sin(graph[m].theta-graph[k].theta))
            return Qf
        else:
            return 0                
    def dPfdt(self,graph,flagT,var):
        k=self.fr
        m=self.to
        Vk=graph[k].V
        Vm=graph[m].V
        tk=graph[k].theta
        tm=graph[m].theta
        if flagT==0:
            Bkm=np.imag(self.Y[0][1])
            Gkm=np.real(self.Y[0][1])
            if k==var: # dPkm/dtk
                return Vk*Vm*(Bkm*np.cos(tk-tm)-Gkm*np.sin(tk-tm))
            elif m==var:# dPkm/dtm
                return Vk*Vm*(-Bkm*np.cos(tk-tm)+Gkm*np.sin(tk-tm))
            else : 
                return 0
        elif flagT==1:
            Bmk=np.imag(self.Y[1][0])
            Gmk=np.real(self.Y[1][0])
            if k==var: # dPmk/dtk
                return Vk*Vm*(-Bmk*np.cos(tk-tm)-Gmk*np.sin(tk-tm))
            elif m==var: # dPmk/dtm
                return Vk*Vm*(Bmk*np.cos(tk-tm)+Gmk*np.sin(tk-tm))
            else : 
                return 0
    def dPfdV(self,graph,flagT,var):
        k=self.fr
        m=self.to
        Vk=graph[k].V
        Vm=graph[m].V
        tk=graph[k].theta
        tm=graph[m].theta  
        if flagT==0: #dPkm
            Gkk=np.real(self.Y[0][0])
            Bkm=np.imag(self.Y[0][1])
            Gkm=np.real(self.Y[0][1])
            if k==var: #dPkm/dVk             
                return 2*Gkk*Vk + Vm*(Bkm*np.sin(tk-tm)+Gkm*np.cos(tk-tm))
            elif m==var:
                return Vk*(Bkm*np.sin(tk-tm)+Gkm*np.cos(tk-tm))
            else:
                return 0    
        elif flagT==1:
            Gmm=np.real(self.Y[1][1])
            Bmk=np.imag(self.Y[1][0])
            Gmk=np.real(self.Y[1][0])
            if k==var: #dPkm/dVk  
                return Vm*(-Bmk*np.sin(tk-tm)+Gmk*np.cos(tk-tm))
            elif m==var:#dPkm/dVm
                return 2*Gmm*Vm + Vk*(-Bmk*np.sin(tk-tm)+Gmk*np.cos(tk-tm))
            else:
                return 0
    def dQfdt(self,graph,flagT,var):
        k=self.fr
        m=self.to
        Vk=graph[k].V
        Vm=graph[m].V
        tk=graph[k].theta
        tm=graph[m].theta  
        if flagT==0: #dQkm
            Bkm=np.imag(self.Y[0][1])
            Gkm=np.real(self.Y[0][1])
            if k==var: #dQkm/dtk
                return Vk*Vm*(Bkm*np.sin(tk-tm)+Gkm*np.cos(tk-tm))
            elif m==var: #dQkm/dtm
                return Vk*Vm*(-Bkm*np.sin(tk-tm)-Gkm*np.cos(tk-tm))
        elif flagT==1: #dQmk
            Bmk=np.imag(self.Y[1][0])
            Gmk=np.real(self.Y[1][0])
            if k==var: #dQmk/dtk
                return Vk*Vm*(Bmk*np.sin(tk-tm)-Gmk*np.cos(tk-tm))            
            elif m==var: #dQmk/dtm
                return Vk*Vm*(-Bmk*np.sin(tk-tm)+Gmk*np.cos(tk-tm))
            else:
                return 0
    def dQfdV(self,graph,flagT,var):
        k=self.fr
        m=self.to
        Vk=graph[k].V
        Vm=graph[m].V
        tk=graph[k].theta
        tm=graph[m].theta
        if flagT==0: #dQkm  
            Bkk=np.imag(self.Y[0][0])
            Bkm=np.imag(self.Y[0][1])
            Gkm=np.real(self.Y[0][1])
            if k==var: #dQkm/dvk
                return -2*Bkk*Vk+Vm*(-Bkm*np.cos(tk-tm)+Gkm*np.sin(tk-tm))
            elif m==var: #dQkm/dvm
                return Vk*(-Bkm*np.cos(tk-tm)+Gkm*np.sin(tk-tm))
            else:
                return 0
        elif flagT==1:
            Bmm=np.imag(self.Y[1][1])
            Bmk=np.imag(self.Y[1][0])
            Gmk=np.real(self.Y[1][0])
            if k==var: #dQmk/dvk
                return Vm*(-Bmk*np.cos(tk-tm)-Gmk*np.sin(tk-tm))
            elif m==var: #dQmk/dvm
                return -2*Bmm*Vm + Vk*(-Bmk*np.cos(tk-tm)-Gmk*np.sin(tk-tm))
            else:
                return 0
    #equations currents
    def Iref(self,graph,flagT):
        k=self.fr
        m=self.to
        Vk=graph[k].V
        Vm=graph[m].V
        tk=graph[k].theta
        tm=graph[m].theta
        if flagT == 0:
            Bkk=np.imag(self.Y[0][0])
            Gkk=np.real(self.Y[0][0])
            Bkm=np.imag(self.Y[0][1])
            Gkm=np.real(self.Y[0][1])
            return -Vk*Bkk*np.sin(tk)+Vk*Gkk*np.cos(tk)-Vm*Bkm*np.sin(tm)+Vm*Gkm*np.cos(tm)
        if flagT == 1:
            Bmm=np.imag(self.Y[1][1])
            Gmm=np.real(self.Y[1][1])
            Bmk=np.imag(self.Y[1][0])
            Gmk=np.real(self.Y[1][0])
            return -Vk*Bmk*np.sin(tk) + Vk*Gmk*np.cos(tk) - Vm*Bmm*np.sin(tm) + Vm*Gmm*np.cos(tm)
    def Iimf(self,graph,flagT):
        k=self.fr
        m=self.to
        Vk=graph[k].V
        Vm=graph[m].V
        tk=graph[k].theta
        tm=graph[m].theta
        if flagT == 0:
            Bkk=np.imag(self.Y[0][0])
            Gkk=np.real(self.Y[0][0])
            Bkm=np.imag(self.Y[0][1])
            Gkm=np.real(self.Y[0][1])
            return Vk*Bkk*np.cos(tk) + Vk*Gkk*np.sin(tk) + Vm*Bkm*np.cos(tm) + Vm*Gkm*np.sin(tm)
        if flagT == 1:
            Bmm=np.imag(self.Y[1][1])
            Gmm=np.real(self.Y[1][1])
            Bmk=np.imag(self.Y[1][0])
            Gmk=np.real(self.Y[1][0])
            return Vk*Bmk*np.cos(tk) + Vk*Gmk*np.sin(tk) + Vm*Bmm*np.cos(tm) + Vm*Gmm*np.sin(tm)
    def dIrefdt(self,graph,flagT,var):
        k=self.fr
        m=self.to
        Vk=graph[k].V
        Vm=graph[m].V
        tk=graph[k].theta
        tm=graph[m].theta
        if flagT==0: #dIkm
            Bkm=np.imag(self.Y[0][1])
            Gkm=np.real(self.Y[0][1])
            Bkk=np.imag(self.Y[0][0])
            Gkk=np.real(self.Y[0][0])
            if k==var:#dIkmtk
                return -Vk*Bkk*np.cos(tk) - Vk*Gkk*np.sin(tk)
            elif m==var:#dIkmtm
                return -Vm*Bkm*np.cos(tm) - Vm*Gkm*np.sin(tm)
            else:
                return 0
        if flagT==1:#dImk
            Bmm=np.imag(self.Y[1][1])
            Gmm=np.real(self.Y[1][1])
            Bmk=np.imag(self.Y[1][0])
            Gmk=np.real(self.Y[1][0])
            if k==var:#dImkdtk
                return -Vk*Bmk*np.cos(tk) - Vk*Gmk*np.sin(tk)
            elif m==var:#dImkdtm
                return -Vm*Bmm*np.cos(tm) - Vm*Gmm*np.sin(tm)
            else:
                return 0
    def dIrefdv(self,graph,flagT,var):
        k=self.fr
        m=self.to
        Vk=graph[k].V
        Vm=graph[m].V
        tk=graph[k].theta
        tm=graph[m].theta
        if flagT==0: #dIkm
            Bkm=np.imag(self.Y[0][1])
            Gkm=np.real(self.Y[0][1])
            Bkk=np.imag(self.Y[0][0])
            Gkk=np.real(self.Y[0][0])
            if k==var:#dIkmvk
                return -Bkk*np.sin(tk) + Gkk*np.cos(tk)
            elif m==var:#dIkmvm
                return -Bkm*np.sin(tm) + Gkm*np.cos(tm)
            else:
                return 0
        if flagT==1:#dImk
            Bmm=np.imag(self.Y[1][1])
            Gmm=np.real(self.Y[1][1])
            Bmk=np.imag(self.Y[1][0])
            Gmk=np.real(self.Y[1][0])
            if k==var:#dImkdvk
                return -Bmk*np.sin(tk) + Gmk*np.cos(tk)
            elif m==var:#dImkdvm
                return -Bmm*np.sin(tm) + Gmm*np.cos(tm)
            else:
                return 0
    def dIimfdt(self,graph,flagT,var):
        k=self.fr
        m=self.to
        Vk=graph[k].V
        Vm=graph[m].V
        tk=graph[k].theta
        tm=graph[m].theta
        if flagT==0: #dIkm
            Bkm=np.imag(self.Y[0][1])
            Gkm=np.real(self.Y[0][1])
            Bkk=np.imag(self.Y[0][0])
            Gkk=np.real(self.Y[0][0])
            if k==var:#dIkmtk
                return -Vk*Bkk*np.sin(tk) + Vk*Gkk*np.cos(tk)
            elif m==var:#dIkmtm
                return -Vm*Bkm*np.sin(tm) + Vm*Gkm*np.cos(tm)
            else:
                return 0
        if flagT==1:#dImk
            Bmm=np.imag(self.Y[1][1])
            Gmm=np.real(self.Y[1][1])
            Bmk=np.imag(self.Y[1][0])
            Gmk=np.real(self.Y[1][0])
            if k==var:#dImkdtk
                return -Vk*Bmk*np.sin(tk) + Vk*Gmk*np.cos(tk)
            elif m==var:#dImkdtm
                return -Vm*Bmm*np.sin(tm) + Vm*Gmm*np.cos(tm)
            else:
                return 0
    def dIimfdv(self,graph,flagT,var):
        k=self.fr
        m=self.to
        Vk=graph[k].V
        Vm=graph[m].V
        tk=graph[k].theta
        tm=graph[m].theta
        if flagT==0: #dIkm
            Bkm=np.imag(self.Y[0][1])
            Gkm=np.real(self.Y[0][1])
            Bkk=np.imag(self.Y[0][0])
            Gkk=np.real(self.Y[0][0])
            if k==var:#dIkmtk
                return Bkk*np.cos(tk) + Gkk*np.sin(tk)
            elif m==var:#dIkmtm
                return Bkm*np.cos(tm) + Gkm*np.sin(tm)
            else:
                return 0
        if flagT==1:#dImk
            Bmm=np.imag(self.Y[1][1])
            Gmm=np.real(self.Y[1][1])
            Bmk=np.imag(self.Y[1][0])
            Gmk=np.real(self.Y[1][0])
            if k==var:#dImkdtk
                return Bmk*np.cos(tk) + Gmk*np.sin(tk)
            elif m==var:#dImkdtm
                return Bmm*np.cos(tm) + Gmm*np.sin(tm)
            else:
                return 0


 
        
        





            

class branTCSC(branch):
    def __init__(self,id,fr,to,type,i,a=1,xtcsc_ini=-1,Pfesp=0):
        super().__init__(id,fr,to,type,i)
        self.a=a
        self.xtcsc_ini=xtcsc_ini
        self.xtcsc=xtcsc_ini
        self.Pfesp=Pfesp
        self.btcsc_ini=-1/xtcsc_ini
        self.btcsc=self.btcsc_ini
        self.k_ini=1
        self.k=self.k_ini
    def AttY(self):
        self.Y[0][0]=complex(0,-1/self.xtcsc)
        self.Y[1][1]=complex(0,-1/self.xtcsc)
        self.Y[1][0]=complex(0,1/self.xtcsc)
        self.Y[0][1]=complex(0,1/self.xtcsc)
    def AttY_B(self):
        self.Y[0][0]=complex(0,self.btcsc)
        self.Y[1][1]=complex(0,self.btcsc)
        self.Y[1][0]=complex(0,-self.btcsc)
        self.Y[0][1]=complex(0,-self.btcsc)
    def AttY_k(self):
        self.Y[0][0]=complex(0,-self.k/self.xtcsc)
        self.Y[1][1]=complex(0,-self.k/self.xtcsc)
        self.Y[1][0]=complex(0,self.k/self.xtcsc)
        self.Y[0][1]=complex(0,self.k/self.xtcsc)

    def dPfdx(self,graph,flagT):
        if flagT==0:
            k=self.fr
            m=self.to
        elif flagT==1:
            k=self.to
            m=self.fr
        return -graph[k].V*graph[m].V*((1/self.xtcsc)**2)*np.sin(graph[k].theta-graph[m].theta)
    def dQfdx(self,graph,flagT):
        if flagT==0:
            k=self.fr
            m=self.to
        elif flagT==1:
            k=self.to
            m=self.fr
        return -(1/self.xtcsc**2)*((graph[k].V**2)-graph[k].V*graph[m].V*np.cos(graph[k].theta-graph[m].theta))
    def dPfdB(self,graph,flagT):
        if flagT==0:
            k=self.fr
            m=self.to
        elif flagT==1:
            k=self.to
            m=self.fr
        return -graph[k].V*graph[m].V*np.sin(graph[k].theta-graph[m].theta)
    def dQfdB(self,graph,flagT):
        if flagT==0:
            k=self.fr
            m=self.to
        elif flagT==1:
            k=self.to
            m=self.fr
        return -(graph[k].V**2)+graph[k].V*graph[m].V*np.cos(graph[k].theta-graph[m].theta)
    def dPfdk(self,graph,flagT):
        if flagT==0:
            k=self.fr
            m=self.to
        elif flagT==1:
            k=self.to
            m=self.fr
        return graph[k].V*graph[m].V*((1/self.xtcsc))*np.sin(graph[k].theta-graph[m].theta)
    def dQfdk(self,graph,flagT):
        if flagT==0:
            k=self.fr
            m=self.to
        elif flagT==1:
            k=self.to
            m=self.fr
        return (1/self.xtcsc)*((graph[k].V**2)-graph[k].V*graph[m].V*np.cos(graph[k].theta-graph[m].theta))
    
    def dI_refdx(self,graph,flagT):
        if flagT==0:
            k=self.fr
            m=self.to
        elif flagT==1:
            k=self.to
            m=self.fr
        return (-graph[k].V*np.sin(graph[k].theta) + graph[m].V*np.sin(graph[m].theta))/(self.xtcsc**2)

    def dI_imdx(self,graph,flagT):
        if flagT==0:
            k=self.fr
            m=self.to
        elif flagT==1:
            k=self.to
            m=self.fr
        return (graph[k].V*np.cos(graph[k].theta) - graph[m].V*np.cos(graph[m].theta))/(self.xtcsc**2)
    



class node_graph():
    def __init__(self,id,bus):
        self.V=1
        self.theta=0
        self.Bs=0
        self.adjk=dict()
        self.adjm=dict()
        self.ladjk=[]
        self.ladjm=[]
        self.SVC=None
        self.id=id
        self.bus=bus
        self.V=1
        self.theta=0
        self.FlagBS=0
        self.FlagTCSC=0
        self.FlagSVC=0
        self.FlagUPFC=0
        self.FlagConvACDC=0
        self.bFACTS_adjk=dict()
        self.bFACTS_adjm=dict()
        self.bUFPC_adjk=dict()
        self.bUFPC_adjm=dict()
        self.dconv_acdc=dict() #dictionary of the converters ac-dc connected to the bus
        
    def P(self,graph):
        P=0
        if self.FlagSVC==1:
            P=P+self.SVC.Gk*self.V**2 
        for key,item in self.adjk.items():
            P=P+item.Pf(graph,0)
        for key,item in self.adjm.items():
            P=P+item.Pf(graph,1)
        for key,item in self.bUFPC_adjk.items():
            P=P+item.Pps(graph)
        for key,item in self.bUFPC_adjm.items():
            P=P+item.Psp(graph)
        if np.abs(P)<1e-12:
            P=0
        return P
    def Q(self,graph):
        if self.FlagBS==0:
            Q=0
        else:    
            Q=-self.Bs*self.V**2 
        if self.FlagSVC==1:
            Q=Q-self.SVC.Bk*self.V**2 
        for key,item in self.adjk.items():
            Q=Q+item.Qf(graph,0)
        for key,item in self.adjm.items():
            Q=Q+item.Qf(graph,1)
        for key,item in self.bUFPC_adjk.items():
            Q=Q+item.Qps(graph)
        for key,item in self.bUFPC_adjm.items():
            Q=Q+item.Qsp(graph)
        if np.abs(Q)<1e-12:
            Q=0
        return Q
    def dPdt(self,graph,bus):
        if self.i==bus:
            dPdt=0
            for key,item in self.adjk.items(): 
                dPdt=dPdt+item.dPfdt(graph,FlagT=0,var=bus)
            for key,item in self.adjm.items():
                dPdt=dPdt+item.dPfdt(graph,FlagT=0,var=bus)
            return dPdt
        elif str(self.i)+"-"+str(bus) in self.adjk.keys():
            return self.adjk[str(self.i)+"-"+str(bus)].dPfdt(graph,0,bus)
        elif str(bus)+"-"+str(self.i) in self.adjk.keys():
            return self.adjk[str(self.i)+"-"+str(bus)].dPfdt(graph,1,bus)
        else:
            return 0
    def dPdV(self,graph,bus):
        dPdV=0
        if self.FlagSVC==1:
            dPdV=dPdV+2*self.SVC.Gk*self.V      
        if self.i==bus:
            for key,item in self.adjk.items(): 
                dPdV=dPdV+item.dPfdV(graph,FlagT=0,var=bus)
            for key,item in self.adjm.items():
                dPdV=dPdV+item.dPfdV(graph,FlagT=0,var=bus)
            return dPdV
        elif str(self.i)+"-"+str(bus) in self.adjk.keys():
            return self.adjk[str(self.i)+"-"+str(bus)].dPfdV(graph,0,bus)
        elif str(bus)+"-"+str(self.i) in self.adjk.keys():
            return self.adjk[str(self.i)+"-"+str(bus)].dPfdV(graph,1,bus)
        else:
            return 0

    def dQdt(self,graph,bus):
        dQdt=0
        if self.i==bus:
            for key,item in self.adjk.items(): 
                dQdt=dQdt+item.dQdt(graph,FlagT=0,var=bus)
            for key,item in self.adjm.items():
                dQdt=dQdt+item.dQdt(graph,FlagT=0,var=bus)
            return dQdt
        elif str(self.i)+"-"+str(bus) in self.adjk.keys():
            return self.adjk[str(self.i)+"-"+str(bus)].dQdt(graph,0,bus)
        elif str(bus)+"-"+str(self.i) in self.adjk.keys():
            return  self.adjk[str(self.i)+"-"+str(bus)].dQdt(graph,1,bus)
        else:
            return 0
    def dQdV(self,graph,bus): ## ENTRA AQUI A DERIVADA DO SVC
        if self.i==bus:
            if self.FlagBS==0:
                dQdV=0
            else:    
                dQdV=-2*self.Bs*self.V
            if self.FlagSVC==1:
                dQdV=dQdV-2*self.SVC.Bk*self.V      
            for key,item in self.adjk.items(): 
                dQdV=dQdV+item.dQdV(graph,FlagT=0,var=bus)
            for key,item in self.adjm.items():
                dQdV=dQdV+item.dQdV(graph,FlagT=0,var=bus)
            return dQdV
        elif str(self.i)+"-"+str(bus) in self.adjk.keys():
            return  self.adjk[str(self.i)+"-"+str(bus)].dQdV(graph,0,bus)
        elif str(bus)+"-"+str(self.i) in self.adjk.keys():
            return  self.adjk[str(self.i)+"-"+str(bus)].dQdV(graph,1,bus)
        else:
            return  0  
    def I_inj_re(self,graph):
        I=0
        if self.FlagSVC==1:
            I=I+self.V*(-self.SVC.Bk*np.sin(self.theta)+self.SVC.Gk*np.cos(self.theta))
        if self.FlagBS==1:
            I=I+self.V*(-self.Bs*np.sin(self.theta))
        for key,item in self.adjk.items():
            I=I+item.Iref(graph,0)
        for key,item in self.adjm.items():
            I=I+item.Iref(graph,1)
        for key,item in self.bUFPC_adjk.items():
            I=I+item.Ips_re(graph)
        for key,item in self.bUFPC_adjm.items():
            I=I+item.Isp_re(graph)
        if np.abs(I)<1e-12:
            I=0
        return I
    def I_inj_im(self,graph):
        I=0
        if self.FlagSVC==1:
            I=I+self.V*(self.SVC.Bk*np.cos(self.theta)+self.SVC.Gk*np.sin(self.theta))
        if self.FlagBS==1:
            I=I+self.V*(self.Bs*np.cos(self.theta))
        for key,item in self.adjk.items():
            I=I+item.Iimf(graph,0)
        for key,item in self.adjm.items():
            I=I+item.Iimf(graph,1)
        for key,item in self.bUFPC_adjk.items():
            I=I+item.Ips_im(graph)
        for key,item in self.bUFPC_adjm.items():
            I=I+item.Isp_im(graph)
        if np.abs(I)<1e-12:
            I=0
        return I

class UPFC():
    def __init__(self,id,fr,to,Vse_ini,t_se_ini,Vsh_ini,t_sh_ini,Psp,Qsp,Vp,Rse,Xse,Rsh,Xsh,Vse_max,Vse_min,Vsh_max,Vsh_min,mode):
        self.id=id #id of UPFC
        self.p=fr  # bus from, following the graph order 
        self.s=to # bus to, following the graph order 
        self.Vse_ini=Vse_ini # Vse_ini initialization for the series source
        self.Vse=Vse_ini # Vse series source voltage magnitude
        self.t_se_ini=t_se_ini*np.pi/180 # t_se_ini series source voltage phase angle initizalization value
        self.t_se=t_se_ini*np.pi/180 # t_se series source voltage phase angle
        self.Vsh_ini=Vsh_ini # Vsh_ini initialization for the shunt source
        self.Vsh=Vsh_ini # Vsh shunt voltage source magnitude
        self.t_sh_ini=t_sh_ini*np.pi/180 # t_sh_ini shunt source voltage phase angle initizalization value
        self.t_sh=t_sh_ini*np.pi/180 # t_sh shunt source voltage phase angle
        self.Psp_set=Psp # specified value for the active power flow over the UPFC 
        self.Qsp_set=Qsp # specified value for the reactive power flow over the UPFC
        self.Vp=Vp #specified value for the voltage magnitude in the terminal p
        self.Vs=1 # voltage magnitude at the "s" terminal
        self.Rse=Rse #resistance for the series source
        self.Xse=Xse #reactance for the series source
        self.Rsh=Rsh #resistance for the shunt source
        self.Xsh=Xsh #reactance for the shunt source
        self.Yse=1/complex(Rse,Xse)  #complex admittance for the series source
        self.Ysh=1/complex(Rsh,Xsh) #complex admittance for the shunt source
        self.gse=np.real(self.Yse)
        self.bse=np.imag(self.Yse)
        self.gsh=np.real(self.Ysh)
        self.bsh=np.imag(self.Ysh)
        self.Vse_max=Vse_max # voltage magnitude superior limit the series source
        self.Vse_min=Vse_min # voltage magnitude inferior limit the series source
        self.Vsh_max=Vsh_max # voltage magnitude superior limit the shunt source
        self.Vsh_min=Vsh_min # voltage magnitude inferior limit the shunt source
        self.mode=mode # mode 0 controls voltage at bus "p"/ 1 does not control voltage at bus "p"
    
    def Pps(self,graph):
        p=self.p
        s=self.s
        PartI=(graph[p].V**2)*(self.gse+self.gsh)
        PartII=-graph[p].V*graph[s].V*(self.gse*np.cos(graph[p].theta-graph[s].theta)+self.bse*np.sin(graph[p].theta-graph[s].theta))
        PartIII=-graph[p].V*self.Vse*(self.gse*np.cos(graph[p].theta-self.t_se)+self.bse*np.sin(graph[p].theta-self.t_se))
        PartIV=-graph[p].V*self.Vsh*(self.gsh*np.cos(graph[p].theta-self.t_sh)+self.bsh*np.sin(graph[p].theta-self.t_sh))
        return PartI+PartII+PartIII+PartIV
    def Qps(self,graph):
        p=self.p
        s=self.s
        PartI=(graph[p].V**2)*(self.bse+self.bsh)
        PartII=-graph[p].V*graph[s].V*(self.bse*np.cos(graph[p].theta-graph[s].theta)-self.gse*np.sin(graph[p].theta-graph[s].theta))
        PartIII=-graph[p].V*self.Vse*(self.bse*np.cos(graph[p].theta-self.t_se)-self.gse*np.sin(graph[p].theta-self.t_se))
        PartIV=-graph[p].V*self.Vsh*(self.bsh*np.cos(graph[p].theta-self.t_sh)-self.gsh*np.sin(graph[p].theta-self.t_sh))
        return -PartI-PartII-PartIII-PartIV
    def Psp(self,graph):
        p=self.p
        s=self.s
        PartIII=(graph[s].V**2)*(self.gse)
        PartI=-graph[s].V*graph[p].V*(self.gse*np.cos(graph[s].theta-graph[p].theta)+self.bse*np.sin(graph[s].theta-graph[p].theta))
        PartII=graph[s].V*self.Vse*(self.gse*np.cos(graph[s].theta-self.t_se)+self.bse*np.sin(graph[s].theta-self.t_se))
        return PartI+PartII+PartIII
    def Qsp(self,graph):
        p=self.p
        s=self.s
        PartI=-graph[s].V*graph[p].V*(self.bse*np.cos(graph[s].theta-graph[p].theta)-self.gse*np.sin(graph[s].theta-graph[p].theta))
        PartII=graph[s].V*self.Vse*(self.bse*np.cos(graph[s].theta-self.t_se)-self.gse*np.sin(graph[s].theta-self.t_se))
        PartIII=(graph[s].V**2)*(self.bse)
        return -PartI-PartII-PartIII
    def Pse(self,graph):
        """
        Active Power generated by series font
        """
        p=self.p
        s=self.s

        PartI=(self.Vse**2)*self.gse
        PartII=-self.Vse*graph[p].V*(self.gse*np.cos(self.t_se-graph[p].theta)+self.bse*np.sin(self.t_se-graph[p].theta))
        PartIII=self.Vse*graph[s].V*(self.gse*np.cos(self.t_se-graph[s].theta)+self.bse*np.sin(self.t_se-graph[s].theta))
        return PartI+PartII+PartIII
    
    def Qse(self,graph):
        """
        Reactive Power generated by series font
        """
        p=self.p
        s=self.s
        PartI=(self.Vse**2)*self.bse
        PartII=-self.Vse*graph[p].V*(self.bse*np.cos(self.t_se-graph[p].theta)-self.gse*np.sin(self.t_se-graph[p].theta))
        PartIII=self.Vse*graph[s].V*(self.bse*np.cos(self.t_se-graph[s].theta)-self.gse*np.sin(self.t_se-graph[s].theta))
        return -PartI-PartII-PartIII

    def Psh(self,graph):
        """
        Active Power generated by shunt font
        """
        p=self.p
        PartI=-(self.Vsh**2)*self.gsh
        PartII=self.Vsh*graph[p].V*(self.gsh*np.cos(self.t_sh-graph[p].theta)+self.bsh*np.sin(self.t_sh-graph[p].theta))
        return PartI+PartII
    
    def Qsh(self,graph):
        """
        Reactive Power generated by shunt font
        """
        p=self.p
        PartI=-(self.Vsh**2)*self.bsh
        PartII=self.Vsh*graph[p].V*(self.bsh*np.cos(self.t_sh-graph[p].theta)-self.gsh*np.sin(self.t_sh-graph[p].theta))
        return -PartI-PartII
    
    def dPpsdtp(self,graph):
        """
        Calcualte the derivative of the active power in respect to the "p" (from) voltage angle
        """    
        p=self.p
        s=self.s
        Vp=graph[p].V
        Vs=graph[s].V
        tp=graph[p].theta
        ts=graph[s].theta
        Vse=self.Vse
        Vsh=self.Vsh
        tse=self.t_se
        tsh=self.t_sh
        gse=self.gse
        bse=self.bse
        gsh=self.gsh
        bsh=self.bsh

        return -Vp*Vs*(bse*np.cos(tp - ts) - gse*np.sin(tp - ts))\
               -Vp*Vse*(bse*np.cos(tp - tse) - gse *np.sin(tp - tse)) \
            - Vp*Vsh*(bsh*np.cos(tp - tsh) - gsh*np.sin(tp - tsh))
    
    
    def dQpsdtp(self,graph):
        """
        Calcualte the derivative of the reactve power in respect to the "p" (from) voltage angle
        """    
        p=self.p
        s=self.s
        Vp=graph[p].V
        Vs=graph[s].V
        tp=graph[p].theta
        ts=graph[s].theta
        Vse=self.Vse
        Vsh=self.Vsh
        tse=self.t_se
        tsh=self.t_sh
        gse=self.gse
        bse=self.bse
        gsh=self.gsh
        bsh=self.bsh

        return Vp*Vs*((-bse)*np.sin(tp -ts) - gse*np.cos(tp - ts))\
              + Vp*Vse*((-bse)*np.sin(tp - tse) - gse*np.cos(tp - tse))\
              + Vp*Vsh*((-bsh)*np.sin(tp - tsh) - gsh*np.cos(tp - tsh))
    

    def dPpsdts(self,graph):
        """
        Calcualte the derivative of the active power in respect to the "s" (to) voltage angle
        """    
        p=self.p
        s=self.s
        Vp=graph[p].V
        Vs=graph[s].V
        tp=graph[p].theta
        ts=graph[s].theta
        Vse=self.Vse
        Vsh=self.Vsh
        tse=self.t_se
        tsh=self.t_sh
        gse=self.gse
        bse=self.bse
        gsh=self.gsh
        bsh=self.bsh

        return -Vp*Vs*(-bse*np.cos(tp - ts) + gse*np.sin(tp - ts))

    def dQpsdts(self,graph):
        """
        Calcualte the derivative of the reactive power in respect to the "s" (to) voltage angle
        """    
        p=self.p
        s=self.s
        Vp=graph[p].V
        Vs=graph[s].V
        tp=graph[p].theta
        ts=graph[s].theta
        Vse=self.Vse
        Vsh=self.Vsh
        tse=self.t_se
        tsh=self.t_sh
        gse=self.gse
        bse=self.bse
        gsh=self.gsh
        bsh=self.bsh

        return Vp*Vs*(bse*np.sin(tp - ts) + gse*np.cos(tp - ts))


    def dPpsdtse(self,graph):
        """
        Calcualte the derivative of the active power in respect to the "se" (series voltage source) voltage angle
        """    
        p=self.p
        s=self.s
        Vp=graph[p].V
        Vs=graph[s].V
        tp=graph[p].theta
        ts=graph[s].theta
        Vse=self.Vse
        Vsh=self.Vsh
        tse=self.t_se
        tsh=self.t_sh
        gse=self.gse
        bse=self.bse
        gsh=self.gsh
        bsh=self.bsh

        return -Vp*Vse*(-bse*np.cos(tp - tse) + gse*np.sin(tp - tse))

    def dQpsdtse(self,graph):
        """
        Calcualte the derivative of the reactive power in respect to the "se" (series voltage source) voltage angle
        """    
        p=self.p
        s=self.s
        Vp=graph[p].V
        Vs=graph[s].V
        tp=graph[p].theta
        ts=graph[s].theta
        Vse=self.Vse
        Vsh=self.Vsh
        tse=self.t_se
        tsh=self.t_sh
        gse=self.gse
        bse=self.bse
        gsh=self.gsh
        bsh=self.bsh

        return Vp*Vse*(bse*np.sin(tp - tse) + gse*np.cos(tp - tse))

    def dPpsdtsh(self,graph):
        """
        Calcualte the derivative of the active power in respect to the "sh" (shunt voltage source) voltage angle
        """    
        p=self.p
        s=self.s
        Vp=graph[p].V
        Vs=graph[s].V
        tp=graph[p].theta
        ts=graph[s].theta
        Vse=self.Vse
        Vsh=self.Vsh
        tse=self.t_se
        tsh=self.t_sh
        gse=self.gse
        bse=self.bse
        gsh=self.gsh
        bsh=self.bsh

        return -Vp*Vsh*(-bsh*np.cos(tp - tsh) + gsh*np.sin(tp - tsh))

    def dQpsdtsh(self,graph):
        """
        Calcualte the derivative of the reactive power in respect to the "sh" (shunt voltage source) voltage angle
        """    
        p=self.p
        s=self.s
        Vp=graph[p].V
        Vs=graph[s].V
        tp=graph[p].theta
        ts=graph[s].theta
        Vse=self.Vse
        Vsh=self.Vsh
        tse=self.t_se
        tsh=self.t_sh
        gse=self.gse
        bse=self.bse
        gsh=self.gsh
        bsh=self.bsh

        return Vp*Vsh*(bsh*np.sin(tp - tsh) + gsh*np.cos(tp - tsh))
    
    def dPpsdVp(self,graph):
        """
        Calcualte the derivative of the reactive power in respect to the "p" (from terminal) voltage magnitude
        """    
        p=self.p
        s=self.s
        Vp=graph[p].V
        Vs=graph[s].V
        tp=graph[p].theta
        ts=graph[s].theta
        Vse=self.Vse
        Vsh=self.Vsh
        tse=self.t_se
        tsh=self.t_sh
        gse=self.gse
        bse=self.bse
        gsh=self.gsh
        bsh=self.bsh

        return 2*Vp*(gse + gsh) - Vs*(bse*np.sin(tp - ts) + gse*np.cos(tp - ts)) \
            - Vse*(bse*np.sin(tp- tse) + gse*np.cos(tp - tse)) \
            - Vsh*(bsh*np.sin(tp -tsh) + gsh*np.cos(tp -tsh))

    def dQpsdVp(self,graph):
        """
        Calcualte the derivative of the reactive power in respect to the "p" (from terminal) voltage magnitude
        """    
        p=self.p
        s=self.s
        Vp=graph[p].V
        Vs=graph[s].V
        tp=graph[p].theta
        ts=graph[s].theta
        Vse=self.Vse
        Vsh=self.Vsh
        tse=self.t_se
        tsh=self.t_sh
        gse=self.gse
        bse=self.bse
        gsh=self.gsh
        bsh=self.bsh

        return -2*Vp*(bse + bsh)+ \
        Vs*(bse*np.cos(tp - ts) - gse*np.sin(tp - ts)) + \
        Vse*(bse*np.cos(tp-tse) - gse*np.sin(tp- tse)) +\
        Vsh*(bsh*np.cos(tp - tsh) -gsh*np.sin(tp - tsh))


    def dPpsdVs(self,graph):
        """
        Calcualte the derivative of the reactive power in respect to the "s" (to terminal) voltage magnitude
        """    
        p=self.p
        s=self.s
        Vp=graph[p].V
        Vs=graph[s].V
        tp=graph[p].theta
        ts=graph[s].theta
        Vse=self.Vse
        Vsh=self.Vsh
        tse=self.t_se
        tsh=self.t_sh
        gse=self.gse
        bse=self.bse
        gsh=self.gsh
        bsh=self.bsh

        return -Vp*(bse*np.sin(tp - ts) + gse*np.cos(tp - ts))

    def dQpsdVs(self,graph):
        """
        Calcualte the derivative of the reactive power in respect to the "s" (to bus) voltage magnitude
        """    
        p=self.p
        s=self.s
        Vp=graph[p].V
        Vs=graph[s].V
        tp=graph[p].theta
        ts=graph[s].theta
        Vse=self.Vse
        Vsh=self.Vsh
        tse=self.t_se
        tsh=self.t_sh
        gse=self.gse
        bse=self.bse
        gsh=self.gsh
        bsh=self.bsh

        return Vp*(bse*np.cos(tp - ts) - gse*np.sin(tp - ts))
    
    def dPpsdVse(self,graph):
        """
        Calcualte the derivative of the reactive power in respect to the "se" (series source) voltage magnitude
        """    
        p=self.p
        s=self.s
        Vp=graph[p].V
        Vs=graph[s].V
        tp=graph[p].theta
        ts=graph[s].theta
        Vse=self.Vse
        Vsh=self.Vsh
        tse=self.t_se
        tsh=self.t_sh
        gse=self.gse
        bse=self.bse
        gsh=self.gsh
        bsh=self.bsh

        return -Vp*(bse*np.sin(tp - tse) + gse*np.cos(tp - tse))

    def dQpsdVse(self,graph):
        """
        Calcualte the derivative of the reactive power in respect to the "s" (series source) voltage magnitude
        """    
        p=self.p
        s=self.s
        Vp=graph[p].V
        Vs=graph[s].V
        tp=graph[p].theta
        ts=graph[s].theta
        Vse=self.Vse
        Vsh=self.Vsh
        tse=self.t_se
        tsh=self.t_sh
        gse=self.gse
        bse=self.bse
        gsh=self.gsh
        bsh=self.bsh

        return Vp*(bse*np.cos(tp - tse) - gse*np.sin(tp - tse))

    def dPpsdVsh(self,graph):
        """
        Calcualte the derivative of the reactive power in respect to the "sh" (shunt source) voltage magnitude
        """    
        p=self.p
        s=self.s
        Vp=graph[p].V
        Vs=graph[s].V
        tp=graph[p].theta
        ts=graph[s].theta
        Vse=self.Vse
        Vsh=self.Vsh
        tse=self.t_se
        tsh=self.t_sh
        gse=self.gse
        bse=self.bse
        gsh=self.gsh
        bsh=self.bsh

        return -Vp*(bsh*np.sin(tp - tsh) + gsh*np.cos(tp - tsh))

    def dQpsdVsh(self,graph):
        """
        Calcualte the derivative of the reactive power in respect to the "sh" (shunt voltage) voltage magnitude
        """    
        p=self.p
        s=self.s
        Vp=graph[p].V
        Vs=graph[s].V
        tp=graph[p].theta
        ts=graph[s].theta
        Vse=self.Vse
        Vsh=self.Vsh
        tse=self.t_se
        tsh=self.t_sh
        gse=self.gse
        bse=self.bse
        gsh=self.gsh
        bsh=self.bsh

        return Vp*(bsh*np.cos(tp - tsh) - gsh*np.sin(tp - tsh))

    #-------------------derivatives from s to p---------------------------------------------------

    def dPspdtp(self,graph):
        """
        Calcualte the derivative of the active power in respect to the "p" (from) voltage angle
        """    
        p=self.p
        s=self.s
        Vp=graph[p].V
        Vs=graph[s].V
        tp=graph[p].theta
        ts=graph[s].theta
        Vse=self.Vse
        Vsh=self.Vsh
        tse=self.t_se
        tsh=self.t_sh
        gse=self.gse
        bse=self.bse
        gsh=self.gsh
        bsh=self.bsh

        return -Vp*Vs*(-bse*np.cos(tp - ts) - gse*np.sin(tp - ts))
    
    
    def dQspdtp(self,graph):
        """
        Calcualte the derivative of the reactve power in respect to the "p" (from) voltage angle
        """    
        p=self.p
        s=self.s
        Vp=graph[p].V
        Vs=graph[s].V
        tp=graph[p].theta
        ts=graph[s].theta
        Vse=self.Vse
        Vsh=self.Vsh
        tse=self.t_se
        tsh=self.t_sh
        gse=self.gse
        bse=self.bse
        gsh=self.gsh
        bsh=self.bsh

        return Vp*Vs*(-bse*np.sin(tp - ts) + gse*np.cos(tp - ts))
    
    def dPspdts(self,graph):
        """
        Calcualte the derivative of the active power in respect to the "s" (to) voltage angle
        """    
        p=self.p
        s=self.s
        Vp=graph[p].V
        Vs=graph[s].V
        tp=graph[p].theta
        ts=graph[s].theta
        Vse=self.Vse
        Vsh=self.Vsh
        tse=self.t_se
        tsh=self.t_sh
        gse=self.gse
        bse=self.bse
        gsh=self.gsh
        bsh=self.bsh

        return -Vp*Vs*(bse*np.cos(tp- ts) + gse*np.sin(tp- ts)) \
            + Vs*Vse*(bse*np.cos(ts - tse) - gse*np.sin(ts - tse))

    def dQspdts(self,graph):
        """
        Calcualte the derivative of the reactive power in respect to the "s" (to) voltage angle
        """    
        p=self.p
        s=self.s
        Vp=graph[p].V
        Vs=graph[s].V
        tp=graph[p].theta
        ts=graph[s].theta
        Vse=self.Vse
        Vsh=self.Vsh
        tse=self.t_se
        tsh=self.t_sh
        gse=self.gse
        bse=self.bse
        gsh=self.gsh
        bsh=self.bsh

        return Vp*Vs*(bse*np.sin(tp - ts) - gse*np.cos(tp - ts)) -\
             Vs*Vse*(-bse*np.sin(ts - tse) - gse*np.cos(ts - tse))


    def dPspdtse(self,graph):
        """
        Calcualte the derivative of the active power in respect to the "se" (series voltage source) voltage angle
        """    
        p=self.p
        s=self.s
        Vp=graph[p].V
        Vs=graph[s].V
        tp=graph[p].theta
        ts=graph[s].theta
        Vse=self.Vse
        Vsh=self.Vsh
        tse=self.t_se
        tsh=self.t_sh
        gse=self.gse
        bse=self.bse
        gsh=self.gsh
        bsh=self.bsh

        return Vs*Vse*(-bse*np.cos(ts - tse) + gse*np.sin(ts - tse))

    def dQspdtse(self,graph):
        """
        Calcualte the derivative of the reactive power in respect to the "se" (series voltage source) voltage angle
        """    
        p=self.p
        s=self.s
        Vp=graph[p].V
        Vs=graph[s].V
        tp=graph[p].theta
        ts=graph[s].theta
        Vse=self.Vse
        Vsh=self.Vsh
        tse=self.t_se
        tsh=self.t_sh
        gse=self.gse
        bse=self.bse
        gsh=self.gsh
        bsh=self.bsh

        return -Vs*Vse*(bse*np.sin(ts - tse) + gse*np.cos(ts - tse))

    def dPspdtsh(self,graph):
        """
        Calcualte the derivative of the active power in respect to the "sh" (shunt voltage source) voltage angle
        """    

        return 0

    def dQspdtsh(self,graph):
        """
        Calcualte the derivative of the reactive power in respect to the "sh" (shunt voltage source) voltage angle
        """    

        return 0
    
    def dPspdVp(self,graph):
        """
        Calcualte the derivative of the reactive power in respect to the "p" (from terminal) voltage magnitude
        """    
        p=self.p
        s=self.s
        Vp=graph[p].V
        Vs=graph[s].V
        tp=graph[p].theta
        ts=graph[s].theta
        Vse=self.Vse
        Vsh=self.Vsh
        tse=self.t_se
        tsh=self.t_sh
        gse=self.gse
        bse=self.bse
        gsh=self.gsh
        bsh=self.bsh

        return -Vs*(-bse*np.sin(tp - ts) + gse*np.cos(tp - ts))

    def dQspdVp(self,graph):
        """
        Calcualte the derivative of the reactive power in respect to the "p" (from terminal) voltage magnitude
        """    
        p=self.p
        s=self.s
        Vp=graph[p].V
        Vs=graph[s].V
        tp=graph[p].theta
        ts=graph[s].theta
        Vse=self.Vse
        Vsh=self.Vsh
        tse=self.t_se
        tsh=self.t_sh
        gse=self.gse
        bse=self.bse
        gsh=self.gsh
        bsh=self.bsh

        return Vs*(bse*np.cos(tp - ts) + gse*np.sin(tp - ts))


    def dPspdVs(self,graph):
        """
        Calcualte the derivative of the reactive power in respect to the "s" (to terminal) voltage magnitude
        """    
        p=self.p
        s=self.s
        Vp=graph[p].V
        Vs=graph[s].V
        tp=graph[p].theta
        ts=graph[s].theta
        Vse=self.Vse
        Vsh=self.Vsh
        tse=self.t_se
        tsh=self.t_sh
        gse=self.gse
        bse=self.bse
        gsh=self.gsh
        bsh=self.bsh

        return -Vp*(-bse*np.sin(tp - ts) + gse*np.cos(tp - ts)) + 2*Vs*gse \
            + Vse*(bse*np.sin(ts - tse) + gse*np.cos(ts - tse))

    def dQspdVs(self,graph):
        """
        Calcualte the derivative of the reactive power in respect to the "s" (to bus) voltage magnitude
        """    
        p=self.p
        s=self.s
        Vp=graph[p].V
        Vs=graph[s].V
        tp=graph[p].theta
        ts=graph[s].theta
        Vse=self.Vse
        Vsh=self.Vsh
        tse=self.t_se
        tsh=self.t_sh
        gse=self.gse
        bse=self.bse
        gsh=self.gsh
        bsh=self.bsh

        return Vp*(bse*np.cos(tp - ts) + gse*np.sin(tp - ts)) - 2*Vs*bse \
            - Vse*(bse*np.cos(ts - tse) - gse*np.sin(ts - tse))
    
    def dPspdVse(self,graph):
        """
        Calcualte the derivative of the reactive power in respect to the "se" (series source) voltage magnitude
        """    
        p=self.p
        s=self.s
        Vp=graph[p].V
        Vs=graph[s].V
        tp=graph[p].theta
        ts=graph[s].theta
        Vse=self.Vse
        Vsh=self.Vsh
        tse=self.t_se
        tsh=self.t_sh
        gse=self.gse
        bse=self.bse
        gsh=self.gsh
        bsh=self.bsh

        return Vs*(bse*np.sin(ts - tse) + gse*np.cos(ts - tse))

    def dQspdVse(self,graph):
        """
        Calcualte the derivative of the reactive power in respect to the "s" (series source) voltage magnitude
        """    
        p=self.p
        s=self.s
        Vp=graph[p].V
        Vs=graph[s].V
        tp=graph[p].theta
        ts=graph[s].theta
        Vse=self.Vse
        Vsh=self.Vsh
        tse=self.t_se
        tsh=self.t_sh
        gse=self.gse
        bse=self.bse
        gsh=self.gsh
        bsh=self.bsh

        return -Vs*(bse*np.cos(ts - tse) - gse*np.sin(ts - tse))

    def dPspdVsh(self,graph):
        """
        Calcualte the derivative of the reactive power in respect to the "sh" (shunt source) voltage magnitude
        """    


        return 0

    def dQspdVsh(self,graph):
        """
        Calcualte the derivative of the reactive power in respect to the "sh" (shunt voltage) voltage magnitude
        """    

        return 0
    
    def dIgdtp(self,graph):
        """
        Calcualte the derivative of the power mismatch in respect to the "p" (from bus) voltage angle
        """    
        p=self.p
        s=self.s
        Vp=graph[p].V
        Vs=graph[s].V
        tp=graph[p].theta
        ts=graph[s].theta
        Vse=self.Vse
        Vsh=self.Vsh
        tse=self.t_se
        tsh=self.t_sh
        gse=self.gse
        bse=self.bse
        gsh=self.gsh
        bsh=self.bsh

        return -Vp*Vse*(-bse*np.cos(tp - tse) - gse*np.sin(tp - tse)) -\
            Vp*Vsh*(-bsh*np.cos(tp - tsh)- gsh*np.sin(tp - tsh))

    
    def dIgdts(self,graph):
        """
        Calcualte the derivative of the power mismatch in respect to the "s" (to bus) voltage angle
        """    
        p=self.p
        s=self.s
        Vp=graph[p].V
        Vs=graph[s].V
        tp=graph[p].theta
        ts=graph[s].theta
        Vse=self.Vse
        Vsh=self.Vsh
        tse=self.t_se
        tsh=self.t_sh
        gse=self.gse
        bse=self.bse
        gsh=self.gsh
        bsh=self.bsh

        return Vs*Vse*(-bse*np.cos(ts - tse) - gse*np.sin(ts - tse))

    def dIgdtse(self,graph):
        """
        Calcualte the derivative of the power mismatch in respect to the "se" (series source) voltage angle
        """    
        p=self.p
        s=self.s
        Vp=graph[p].V
        Vs=graph[s].V
        tp=graph[p].theta
        ts=graph[s].theta
        Vse=self.Vse
        Vsh=self.Vsh
        tse=self.t_se
        tsh=self.t_sh
        gse=self.gse
        bse=self.bse
        gsh=self.gsh
        bsh=self.bsh

        return -Vp*Vse*(bse*np.cos(tp - tse) + gse*np.sin(tp - tse)) \
            + Vs*Vse*(bse*np.cos(ts - tse) + gse*np.sin(ts - tse))

    def dIgdtsh(self,graph):
        """
        Calcualte the derivative of the power mismatch in respect to the "sh" (shun source) voltage angle
        """    
        p=self.p
        s=self.s
        Vp=graph[p].V
        Vs=graph[s].V
        tp=graph[p].theta
        ts=graph[s].theta
        Vse=self.Vse
        Vsh=self.Vsh
        tse=self.t_se
        tsh=self.t_sh
        gse=self.gse
        bse=self.bse
        gsh=self.gsh
        bsh=self.bsh

        return -Vp*Vsh*(bsh*np.cos(tp - tsh) + gsh*np.sin(tp - tsh))


    def dIgdVp(self,graph):
        """
        Calcualte the derivative of the power mismatch in respect to the "p" (from) voltage magnitude
        """    
        p=self.p
        s=self.s
        Vp=graph[p].V
        Vs=graph[s].V
        tp=graph[p].theta
        ts=graph[s].theta
        Vse=self.Vse
        Vsh=self.Vsh
        tse=self.t_se
        tsh=self.t_sh
        gse=self.gse
        bse=self.bse
        gsh=self.gsh
        bsh=self.bsh

        return -Vse*(-bse*np.sin(tp - tse) + gse*np.cos(tp - tse)) \
            - Vsh*(-bsh*np.sin(tp - tsh) + gsh*np.cos(tp - tsh))

    def dIgdVs(self,graph):
        """
        Calcualte the derivative of the power mismatch in respect to the "s" (to bus) voltage magnitude
        """    
        p=self.p
        s=self.s
        Vp=graph[p].V
        Vs=graph[s].V
        tp=graph[p].theta
        ts=graph[s].theta
        Vse=self.Vse
        Vsh=self.Vsh
        tse=self.t_se
        tsh=self.t_sh
        gse=self.gse
        bse=self.bse
        gsh=self.gsh
        bsh=self.bsh

        return Vse*(-bse*np.sin(ts - tse) + gse*np.cos(ts - tse))

    def dIgdVse(self,graph):
        """
        Calcualte the derivative of the power mismatch in respect to the "se" (series source) voltage magnitude
        """    
        p=self.p
        s=self.s
        Vp=graph[p].V
        Vs=graph[s].V
        tp=graph[p].theta
        ts=graph[s].theta
        Vse=self.Vse
        Vsh=self.Vsh
        tse=self.t_se
        tsh=self.t_sh
        gse=self.gse
        bse=self.bse
        gsh=self.gsh
        bsh=self.bsh

        return -Vp*(-bse*np.sin(tp - tse) + gse*np.cos(tp - tse)) \
            + Vs*(-bse*np.sin(ts - tse) + gse*np.cos(ts - tse)) + 2*Vse*gse

    def dIgdVsh(self,graph):
        """
        Calcualte the derivative of the power mismatch in respect to the "sh" (series source) voltage magnitude
        """    
        p=self.p
        s=self.s
        Vp=graph[p].V
        Vs=graph[s].V
        tp=graph[p].theta
        ts=graph[s].theta
        Vse=self.Vse
        Vsh=self.Vsh
        tse=self.t_se
        tsh=self.t_sh
        gse=self.gse
        bse=self.bse
        gsh=self.gsh
        bsh=self.bsh

        return -Vp*(-bsh*np.sin(tp - tsh) + gsh*np.cos(tp - tsh)) + 2*Vsh*gsh
    #correntes no UPFC
    def Ips_re(self,graph):
        p=self.p
        s=self.s
        Vp=graph[p].V
        Vs=graph[s].V
        tp=graph[p].theta
        ts=graph[s].theta
        Vse=self.Vse
        Vsh=self.Vsh
        tse=self.t_se
        tsh=self.t_sh
        gse=self.gse
        bse=self.bse
        gsh=self.gsh
        bsh=self.bsh
        return -Vp*(bse + bsh)*np.sin(tp) + Vp*(gse + gsh)*np.cos(tp) \
            + Vs*bse*np.sin(ts) - Vs*gse*np.cos(ts) + Vse*bse*np.sin(tse)\
            - Vse*gse*np.cos(tse) + Vsh*bsh*np.sin(tsh) - Vsh*gsh*np.cos(tsh)
    
    def Ips_im(self,graph):
        p=self.p
        s=self.s
        Vp=graph[p].V
        Vs=graph[s].V
        tp=graph[p].theta
        ts=graph[s].theta
        Vse=self.Vse
        Vsh=self.Vsh
        tse=self.t_se
        tsh=self.t_sh
        gse=self.gse
        bse=self.bse
        gsh=self.gsh
        bsh=self.bsh
        return Vp*(bse + bsh)*np.cos(tp) + Vp*(gse + gsh)*np.sin(tp) - Vs*bse*np.cos(ts)\
              -Vs*gse*np.sin(ts) - Vse*bse*np.cos(tse) - Vse*gse*np.sin(tse) -Vsh*bsh*np.cos(tsh)\
              -Vsh*gsh*np.sin(tsh)

    

    def Isp_re(self,graph):
        p=self.p
        s=self.s
        Vp=graph[p].V
        Vs=graph[s].V
        tp=graph[p].theta
        ts=graph[s].theta
        Vse=self.Vse
        Vsh=self.Vsh
        tse=self.t_se
        tsh=self.t_sh
        gse=self.gse
        bse=self.bse
        gsh=self.gsh
        bsh=self.bsh
        return Vp*bse*np.sin(tp) - Vp*gse*np.cos(tp) - Vs*bse*np.sin(ts) + Vs*gse*np.cos(ts) \
            - Vse*bse*np.sin(tse) + Vse*gse*np.cos(tse)
    
    def Isp_im(self,graph):
        p=self.p
        s=self.s
        Vp=graph[p].V
        Vs=graph[s].V
        tp=graph[p].theta
        ts=graph[s].theta
        Vse=self.Vse
        Vsh=self.Vsh
        tse=self.t_se
        tsh=self.t_sh
        gse=self.gse
        bse=self.bse
        gsh=self.gsh
        bsh=self.bsh
        return -Vp*bse*np.cos(tp) - Vp*gse*np.sin(tp) \
            + Vs*bse*np.cos(ts) + Vs*gse*np.sin(ts) \
            + Vse*bse*np.cos(tse) + Vse*gse*np.sin(tse)
    
    def dIps_redtp(self,graph):
        p=self.p
        s=self.s
        V_p=graph[p].V
        V_s=graph[s].V
        t_p=graph[p].theta
        t_s=graph[s].theta
        V_se=self.Vse
        V_sh=self.Vsh
        t_se=self.t_se
        t_sh=self.t_sh
        g_se=self.gse
        b_se=self.bse
        g_sh=self.gsh
        b_sh=self.bsh
        return -V_p*((b_se + b_sh)*np.cos(t_p) + (g_se + g_sh)*np.sin(t_p))
    
    def dIps_redts(self,graph):
        p=self.p
        s=self.s
        V_p=graph[p].V
        V_s=graph[s].V
        t_p=graph[p].theta
        t_s=graph[s].theta
        V_se=self.Vse
        V_sh=self.Vsh
        t_se=self.t_se
        t_sh=self.t_sh
        g_se=self.gse
        b_se=self.bse
        g_sh=self.gsh
        b_sh=self.bsh
        return V_s*(b_se*np.cos(t_s) + g_se*np.sin(t_s))
    
    def dIps_redtse(self,graph):
        p=self.p
        s=self.s
        V_p=graph[p].V
        V_s=graph[s].V
        t_p=graph[p].theta
        t_s=graph[s].theta
        V_se=self.Vse
        V_sh=self.Vsh
        t_se=self.t_se
        t_sh=self.t_sh
        g_se=self.gse
        b_se=self.bse
        g_sh=self.gsh
        b_sh=self.bsh
        return V_se*(b_se*np.cos(t_se) + g_se*np.sin(t_se))
    
    def dIps_redtsh(self,graph):
        p=self.p
        s=self.s
        V_p=graph[p].V
        V_s=graph[s].V
        t_p=graph[p].theta
        t_s=graph[s].theta
        V_se=self.Vse
        V_sh=self.Vsh
        t_se=self.t_se
        t_sh=self.t_sh
        g_se=self.gse
        b_se=self.bse
        g_sh=self.gsh
        b_sh=self.bsh
        return V_sh*(b_sh*np.cos(t_sh) + g_sh*np.sin(t_sh))
   
    def dIps_redVp(self,graph):
        p=self.p
        s=self.s
        V_p=graph[p].V
        V_s=graph[s].V
        t_p=graph[p].theta
        t_s=graph[s].theta
        V_se=self.Vse
        V_sh=self.Vsh
        t_se=self.t_se
        t_sh=self.t_sh
        g_se=self.gse
        b_se=self.bse
        g_sh=self.gsh
        b_sh=self.bsh
        return -(b_se + b_sh)*np.sin(t_p) + (g_se + g_sh)*np.cos(t_p)
    
    def dIps_redVs(self,graph):
        p=self.p
        s=self.s
        V_p=graph[p].V
        V_s=graph[s].V
        t_p=graph[p].theta
        t_s=graph[s].theta
        V_se=self.Vse
        V_sh=self.Vsh
        t_se=self.t_se
        t_sh=self.t_sh
        g_se=self.gse
        b_se=self.bse
        g_sh=self.gsh
        b_sh=self.bsh
        return b_se*np.sin(t_s) - g_se*np.cos(t_s)
    
    def dIps_redVse(self,graph):
        p=self.p
        s=self.s
        V_p=graph[p].V
        V_s=graph[s].V
        t_p=graph[p].theta
        t_s=graph[s].theta
        V_se=self.Vse
        V_sh=self.Vsh
        t_se=self.t_se
        t_sh=self.t_sh
        g_se=self.gse
        b_se=self.bse
        g_sh=self.gsh
        b_sh=self.bsh
        return b_se*np.sin(t_se) - g_se*np.cos(t_se)

    def dIps_redVsh(self,graph):
        p=self.p
        s=self.s
        V_p=graph[p].V
        V_s=graph[s].V
        t_p=graph[p].theta
        t_s=graph[s].theta
        V_se=self.Vse
        V_sh=self.Vsh
        t_se=self.t_se
        t_sh=self.t_sh
        g_se=self.gse
        b_se=self.bse
        g_sh=self.gsh
        b_sh=self.bsh
        return  b_sh*np.sin(t_sh) - g_sh*np.cos(t_sh)
    
    def dIps_imdtp(self,graph):
        p=self.p
        s=self.s
        V_p=graph[p].V
        V_s=graph[s].V
        t_p=graph[p].theta
        t_s=graph[s].theta
        V_se=self.Vse
        V_sh=self.Vsh
        t_se=self.t_se
        t_sh=self.t_sh
        g_se=self.gse
        b_se=self.bse
        g_sh=self.gsh
        b_sh=self.bsh
        return V_p*(-(b_se + b_sh)*np.sin(t_p) + (g_se + g_sh)*np.cos(t_p))
   
    def dIps_imdts(self,graph):
        p=self.p
        s=self.s
        V_p=graph[p].V
        V_s=graph[s].V
        t_p=graph[p].theta
        t_s=graph[s].theta
        V_se=self.Vse
        V_sh=self.Vsh
        t_se=self.t_se
        t_sh=self.t_sh
        g_se=self.gse
        b_se=self.bse
        g_sh=self.gsh
        b_sh=self.bsh
        return V_s*(b_se*np.sin(t_s) - g_se*np.cos(t_s))
    
    def dIps_imdtse(self,graph):
        p=self.p
        s=self.s
        V_p=graph[p].V
        V_s=graph[s].V
        t_p=graph[p].theta
        t_s=graph[s].theta
        V_se=self.Vse
        V_sh=self.Vsh
        t_se=self.t_se
        t_sh=self.t_sh
        g_se=self.gse
        b_se=self.bse
        g_sh=self.gsh
        b_sh=self.bsh
        
        return V_se*(b_se*np.sin(t_se) - g_se*np.cos(t_se))
    
    def dIps_imdtsh(self,graph):
        p=self.p
        s=self.s
        V_p=graph[p].V
        V_s=graph[s].V
        t_p=graph[p].theta
        t_s=graph[s].theta
        V_se=self.Vse
        V_sh=self.Vsh
        t_se=self.t_se
        t_sh=self.t_sh
        g_se=self.gse
        b_se=self.bse
        g_sh=self.gsh
        b_sh=self.bsh
        return V_sh*(b_sh*np.sin(t_sh) - g_sh*np.cos(t_sh))
    
    def dIps_imdVp(self,graph):
        p=self.p
        s=self.s
        V_p=graph[p].V
        V_s=graph[s].V
        t_p=graph[p].theta
        t_s=graph[s].theta
        V_se=self.Vse
        V_sh=self.Vsh
        t_se=self.t_se
        t_sh=self.t_sh
        g_se=self.gse
        b_se=self.bse
        g_sh=self.gsh
        b_sh=self.bsh  
        return (b_se + b_sh)*np.cos(t_p) + (g_se + g_sh)*np.sin(t_p) 
    
    def dIps_imdVs(self,graph):
        p=self.p
        s=self.s
        V_p=graph[p].V
        V_s=graph[s].V
        t_p=graph[p].theta
        t_s=graph[s].theta
        V_se=self.Vse
        V_sh=self.Vsh
        t_se=self.t_se
        t_sh=self.t_sh
        g_se=self.gse
        b_se=self.bse
        g_sh=self.gsh
        b_sh=self.bsh  
        return -b_se*np.cos(t_s) - g_se*np.sin(t_s)
    def dIps_imdVse(self,graph):
        p=self.p
        s=self.s
        V_p=graph[p].V
        V_s=graph[s].V
        t_p=graph[p].theta
        t_s=graph[s].theta
        V_se=self.Vse
        V_sh=self.Vsh
        t_se=self.t_se
        t_sh=self.t_sh
        g_se=self.gse
        b_se=self.bse
        g_sh=self.gsh
        b_sh=self.bsh  
        return -b_se*np.cos(t_se) - g_se*np.sin(t_se)
    
    def dIps_imdVsh(self,graph):
        p=self.p
        s=self.s
        V_p=graph[p].V
        V_s=graph[s].V
        t_p=graph[p].theta
        t_s=graph[s].theta
        V_se=self.Vse
        V_sh=self.Vsh
        t_se=self.t_se
        t_sh=self.t_sh
        g_se=self.gse
        b_se=self.bse
        g_sh=self.gsh
        b_sh=self.bsh  
        return -b_sh*np.cos(t_sh) - g_sh*np.sin(t_sh)
    
    def dIsp_redtp(self,graph):
        p=self.p
        s=self.s
        V_p=graph[p].V
        V_s=graph[s].V
        t_p=graph[p].theta
        t_s=graph[s].theta
        V_se=self.Vse
        V_sh=self.Vsh
        t_se=self.t_se
        t_sh=self.t_sh
        g_se=self.gse
        b_se=self.bse
        g_sh=self.gsh
        b_sh=self.bsh
        return V_p*(b_se*np.cos(t_p) + g_se*np.sin(t_p))
    
    def dIsp_redts(self,graph):
        p=self.p
        s=self.s
        V_p=graph[p].V
        V_s=graph[s].V
        t_p=graph[p].theta
        t_s=graph[s].theta
        V_se=self.Vse
        V_sh=self.Vsh
        t_se=self.t_se
        t_sh=self.t_sh
        g_se=self.gse
        b_se=self.bse
        g_sh=self.gsh
        b_sh=self.bsh
        return -V_s*(b_se*np.cos(t_s) + g_se*np.sin(t_s))
    def dIsp_redtse(self,graph):
        p=self.p
        s=self.s
        V_p=graph[p].V
        V_s=graph[s].V
        t_p=graph[p].theta
        t_s=graph[s].theta
        V_se=self.Vse
        V_sh=self.Vsh
        t_se=self.t_se
        t_sh=self.t_sh
        g_se=self.gse
        b_se=self.bse
        g_sh=self.gsh
        b_sh=self.bsh
        return -V_se*(b_se*np.cos(t_se) + g_se*np.sin(t_se))
    
    def dIsp_redtsh(self,graph):
        p=self.p
        s=self.s
        V_p=graph[p].V
        V_s=graph[s].V
        t_p=graph[p].theta
        t_s=graph[s].theta
        V_se=self.Vse
        V_sh=self.Vsh
        t_se=self.t_se
        t_sh=self.t_sh
        g_se=self.gse
        b_se=self.bse
        g_sh=self.gsh
        b_sh=self.bsh
        return 0
    
    def dIsp_redVp(self,graph):
        p=self.p
        s=self.s
        V_p=graph[p].V
        V_s=graph[s].V
        t_p=graph[p].theta
        t_s=graph[s].theta
        V_se=self.Vse
        V_sh=self.Vsh
        t_se=self.t_se
        t_sh=self.t_sh
        g_se=self.gse
        b_se=self.bse
        g_sh=self.gsh
        b_sh=self.bsh
        return b_se*np.sin(t_p) - g_se*np.cos(t_p)
        
    def dIsp_redVs(self,graph):
        p=self.p
        s=self.s
        V_p=graph[p].V
        V_s=graph[s].V
        t_p=graph[p].theta
        t_s=graph[s].theta
        V_se=self.Vse
        V_sh=self.Vsh
        t_se=self.t_se
        t_sh=self.t_sh
        g_se=self.gse
        b_se=self.bse
        g_sh=self.gsh
        b_sh=self.bsh
        return -b_se*np.sin(t_s) + g_se*np.cos(t_s)
    
    def dIsp_redVse(self,graph):
        p=self.p
        s=self.s
        V_p=graph[p].V
        V_s=graph[s].V
        t_p=graph[p].theta
        t_s=graph[s].theta
        V_se=self.Vse
        V_sh=self.Vsh
        t_se=self.t_se
        t_sh=self.t_sh
        g_se=self.gse
        b_se=self.bse
        g_sh=self.gsh
        b_sh=self.bsh
        return -b_se*np.sin(t_se) + g_se*np.cos(t_se)
        
    def dIsp_redVsh(self,graph):
        p=self.p
        s=self.s
        V_p=graph[p].V
        V_s=graph[s].V
        t_p=graph[p].theta
        t_s=graph[s].theta
        V_se=self.Vse
        V_sh=self.Vsh
        t_se=self.t_se
        t_sh=self.t_sh
        g_se=self.gse
        b_se=self.bse
        g_sh=self.gsh
        b_sh=self.bsh
        return 0
    
    def dIsp_imdtp(self,graph):
        p=self.p
        s=self.s
        V_p=graph[p].V
        V_s=graph[s].V
        t_p=graph[p].theta
        t_s=graph[s].theta
        V_se=self.Vse
        V_sh=self.Vsh
        t_se=self.t_se
        t_sh=self.t_sh
        g_se=self.gse
        b_se=self.bse
        g_sh=self.gsh
        b_sh=self.bsh    
        return V_p*(b_se*np.sin(t_p) - g_se*np.cos(t_p))
    
    
    def dIsp_imdts(self,graph):
        p=self.p
        s=self.s
        V_p=graph[p].V
        V_s=graph[s].V
        t_p=graph[p].theta
        t_s=graph[s].theta
        V_se=self.Vse
        V_sh=self.Vsh
        t_se=self.t_se
        t_sh=self.t_sh
        g_se=self.gse
        b_se=self.bse
        g_sh=self.gsh
        b_sh=self.bsh       
        return V_s*(-b_se*np.sin(t_s) + g_se*np.cos(t_s))
    def dIsp_imdtse(self,graph):
        p=self.p
        s=self.s
        V_p=graph[p].V
        V_s=graph[s].V
        t_p=graph[p].theta
        t_s=graph[s].theta
        V_se=self.Vse
        V_sh=self.Vsh
        t_se=self.t_se
        t_sh=self.t_sh
        g_se=self.gse
        b_se=self.bse
        g_sh=self.gsh
        b_sh=self.bsh 
        return V_se*(-b_se*np.sin(t_se) + g_se*np.cos(t_se))
    def dIsp_imdtsh(self,graph):
        p=self.p
        s=self.s
        V_p=graph[p].V
        V_s=graph[s].V
        t_p=graph[p].theta
        t_s=graph[s].theta
        V_se=self.Vse
        V_sh=self.Vsh
        t_se=self.t_se
        t_sh=self.t_sh
        g_se=self.gse
        b_se=self.bse
        g_sh=self.gsh
        b_sh=self.bsh 
        return 0
    
    def dIsp_imdVp(self,graph):
        p=self.p
        s=self.s
        V_p=graph[p].V
        V_s=graph[s].V
        t_p=graph[p].theta
        t_s=graph[s].theta
        V_se=self.Vse
        V_sh=self.Vsh
        t_se=self.t_se
        t_sh=self.t_sh
        g_se=self.gse
        b_se=self.bse
        g_sh=self.gsh
        b_sh=self.bsh    
        return -b_se*np.cos(t_p) - g_se*np.sin(t_p)
    
    def dIsp_imdVs(self,graph):
        p=self.p
        s=self.s
        V_p=graph[p].V
        V_s=graph[s].V
        t_p=graph[p].theta
        t_s=graph[s].theta
        V_se=self.Vse
        V_sh=self.Vsh
        t_se=self.t_se
        t_sh=self.t_sh
        g_se=self.gse
        b_se=self.bse
        g_sh=self.gsh
        b_sh=self.bsh        
        return b_se*np.cos(t_s) + g_se*np.sin(t_s)
    def dIsp_imdVse(self,graph):
            p=self.p
            s=self.s
            V_p=graph[p].V
            V_s=graph[s].V
            t_p=graph[p].theta
            t_s=graph[s].theta
            V_se=self.Vse
            V_sh=self.Vsh
            t_se=self.t_se
            t_sh=self.t_sh
            g_se=self.gse
            b_se=self.bse
            g_sh=self.gsh
            b_sh=self.bsh  
            return b_se*np.cos(t_se) + g_se*np.sin(t_se)
    def dIsp_imdVsh(self,graph):
            p=self.p
            s=self.s
            V_p=graph[p].V
            V_s=graph[s].V
            t_p=graph[p].theta
            t_s=graph[s].theta
            V_se=self.Vse
            V_sh=self.Vsh
            t_se=self.t_se
            t_sh=self.t_sh
            g_se=self.gse
            b_se=self.bse
            g_sh=self.gsh
            b_sh=self.bsh 
            return 0

class SVC():
    def __init__(self,id,bus,Rt,Xt,Bini,BMAX,BMIN,aini,amax,amin):
        self.id=id
        self.bus=bus
        self.Rt=Rt
        self.Xt=Xt
        self.Bini=Bini
        self.BSVC=Bini
        self.Xeq=(self.Xt-1/self.BSVC)
        self.Bk=-self.Xeq/(self.Xeq**2+self.Rt**2)
        self.Gk=self.Rt/(self.Xeq**2+self.Rt**2)
        self.BMAX=BMAX
        self.BMIN=BMIN
        self.aini=aini
        self.amax=amax
        self.amin=amin
    def attYk(self):
        self.Xeq=(self.Xt-1/self.BSVC)
        self.Bk=-self.Xeq/(self.Xeq**2+self.Rt**2)
        self.Gk=self.Rt/(self.Xeq**2+self.Rt**2)
    def dGkdBsvc(self):
        A=-2*self.Rt*self.BSVC*(self.Xt*self.BSVC-1)
        B=((self.Rt**2)*(self.BSVC**2)+(self.Xt*self.BSVC-1)**2)**2
        return A/B
    def dBkdBsvc(self):
        A=(self.Rt**2)*(self.BSVC**2)-(self.Xt**2)*(self.BSVC**2)+2*(self.Xt)*(self.BSVC)-1  
        B=((self.Rt**2)*(self.BSVC**2)+(self.Xt*self.BSVC-1)**2)**2
        return -A/B







class netinfo():
    def __init__(self,nbus,nram,nvar,ntheta,nv) -> None:
        self.nbus=nbus
        self.nram=nram
        self.nvar=nvar
        self.ntheta=ntheta
        self.nv=nv

class meas():
    def __init__(self,k,m,type,val,prec,br_id=None,dire=0) -> None:
        self.k=k
        self.m=m
        self.br_id=br_id
        self.direction=dire
        self.type=type
        self.val=val
        self.prec=prec
        self.sigma=np.abs(val)*prec/3
    def dz(self,graph):
        if self.type==0:
            return self.val-graph[self.k].P(graph) 
        elif self.type==1:
            return self.val-graph[self.k].Q(graph) 
        elif self.type==2:
            keyk=str(self.k)+"-"+str(self.m)
            keym=str(self.m)+"-"+str(self.k)
            if keyk in graph[self.k].adjk.keys():
                return self.val-graph[self.k].adjk[keyk].Pf(graph,0) 
            elif keym in graph[self.k].adjm.keys():
                return self.val-graph[self.k].adjm[keym].Pf(graph,1) 
            elif keyk in graph[self.k].bUFPC_adjk.keys(): 
                return self.val-graph[self.k].bUFPC_adjk[keyk].Pps(graph)
            elif keym in graph[self.k].bUFPC_adjm.keys():
                return self.val-graph[self.k].bUFPC_adjm[keym].Psp(graph)
            else:
                print("nonexistent branch in active power measurement")  
                exit(1)
        elif self.type==3:
            keyk=str(self.k)+"-"+str(self.m)
            keym=str(self.m)+"-"+str(self.k)
            if keyk in graph[self.k].adjk.keys():
                return self.val-graph[self.k].adjk[keyk].Qf(graph,0)
            elif keym in graph[self.k].adjm.keys():
                return self.val-graph[self.k].adjm[keym].Qf(graph,1)
            elif keyk in graph[self.k].bUFPC_adjk.keys(): 
                return self.val-graph[self.k].bUFPC_adjk[keyk].Qps(graph)
            elif keym in graph[self.k].bUFPC_adjm.keys():
                return self.val-graph[self.k].bUFPC_adjm[keym].Qsp(graph)
            else:
                print("reactive power measurement with non-existent branch")
                exit(1)
        elif self.type==4:
            return self.val-graph[self.k].V
        elif self.type==5:
            return self.val-graph[self.k].theta
        elif self.type==6:
            return self.val-graph[self.k].I_inj_re(graph) 
        elif self.type==7:
            return self.val-graph[self.k].I_inj_im(graph) 
        elif self.type==8:
            keyk=str(self.k)+"-"+str(self.m)
            keym=str(self.m)+"-"+str(self.k)
            if keyk in graph[self.k].adjk.keys():
                return self.val-graph[self.k].adjk[keyk].Iref(graph,0) 
            elif keym in graph[self.k].adjm.keys():
                return self.val-graph[self.k].adjm[keym].Iref(graph,1) 
            elif keyk in graph[self.k].bUFPC_adjk.keys(): 
                return self.val-graph[self.k].bUFPC_adjk[keyk].Ips_re(graph)
            elif keym in graph[self.k].bUFPC_adjm.keys():
                return self.val-graph[self.k].bUFPC_adjm[keym].Isp_re(graph)
            else:
                print("active power flow measurement with non-existent branch")
                exit(1)
        elif self.type==9:
            keyk=str(self.k)+"-"+str(self.m)
            keym=str(self.m)+"-"+str(self.k)
            if keyk in graph[self.k].adjk.keys():
                return self.val-graph[self.k].adjk[keyk].Iimf(graph,0)
            elif keym in graph[self.k].adjm.keys():
                return self.val-graph[self.k].adjm[keym].Iimf(graph,1)
            elif keyk in graph[self.k].bUFPC_adjk.keys(): 
                return self.val-graph[self.k].bUFPC_adjk[keyk].Ips_im(graph)
            elif keym in graph[self.k].bUFPC_adjm.keys():
                return self.val-graph[self.k].bUFPC_adjm[keym].Isp_im(graph)
            else:
                print("reactive power flow measurement with non-existent branch")
                exit(1)
        elif self.type==10:
            # measurement is a TCSC control variable
            k=self.k
            keyk=str(self.k)+"-"+str(self.m)
            return self.val-graph[k].bFACTS_adjk[keyk].xtcsc
        elif self.type==11:
            #measurement is a SVC control variable
            k=self.k
            return self.val-graph[k].SVC.BSVC
        elif self.type==12:
            # measure is a control variable of the UPFC (magnitude of the shunt source voltage)
            k=self.k
            keyk=str(self.k)+"-"+str(self.m)
            return self.val-graph[k].bUFPC_adjk[keyk].Vsh
        elif self.type==13:
            # measurement is a control variable of the UPFC (angle of the shunt source voltage)
            k=self.k
            keyk=str(self.k)+"-"+str(self.m)
            return self.val - (graph[k].theta-graph[k].bUFPC_adjk[keyk].t_sh)
        elif self.type==14:
            #measurement is a control variable of the UPFC (magnitude of the series source voltage)
            k=self.k
            keyk=str(self.k)+"-"+str(self.m)
            return self.val - graph[k].bUFPC_adjk[keyk].Vse
        elif self.type==15:
            # measurement is a control variable of the UPFC (angle of the series source voltage)
            k=self.k
            keyk=str(self.k)+"-"+str(self.m)
            return self.val - (graph[k].theta-graph[k].bUFPC_adjk[keyk].t_se)
        elif self.type==100:# DC measurements
            return self.val-graph[self.k].Pdc(graph) #here is the graph_dc
        
        else:
            print("nonexistent measurement type")
            exit(1)

            # return self.val - conv.branch[]          
    def cx(self,graph):
        if self.type==0:
            return graph[self.k].P(graph)
        elif self.type==1:
            return graph[self.k].Q(graph)
        elif self.type==2:
            keyk=str(self.k)+"-"+str(self.m)
            keym=str(self.m)+"-"+str(self.k)
            if keyk in graph[self.k].adjk.keys():
                return graph[self.k].adjk[keyk].Pf(graph,0)
            elif keym in graph[self.k].adjm.keys():
                return graph[self.k].adjm[keym].Pf(graph,1)
            else:
                print("active power flow measurement with non-existent branch")
                exit(1)
        elif self.type==3:
            keyk=str(self.k)+"-"+str(self.m)
            keym=str(self.m)+"-"+str(self.k)
            if keyk in graph[self.k].adjk.keys():
                return graph[self.k].adjk[keyk].Qf(graph,0)
            elif keym in graph[self.k].adjm.keys():
                return graph[self.k].adjm[keym].Qf(graph,1)
            else:
                print("reactive power flow measurement with non-existent branch")
                exit(1)
        elif self.type==4:
            return graph[self.k].V
    

        

class meas_conv(meas):
    def __init__(self,k,m,type,val,prec,br_id=None,dire=0) -> None:
        super().__init__(k,m,type,val,prec,br_id=br_id,dire=dire)
        self.sigma=np.abs(val)*prec/3
    def dz_conv(self,conv_acdc,graph,graph_dc): 
        if self.type in [0,1,2,3,4,5,6,7,8,9]: #active power
             return self.dz(graph)
        elif self.type==200: #virtual injection in the conv filt bus
            return self.val - conv_acdc[self.k].Pvirt()
        elif self.type==201: #virtual injection in the conv filt bus
            return self.val - conv_acdc[self.k].Qvirt()
        elif self.type==202: # power flow trafo active             
            return self.val - conv_acdc[self.k].Ptf(self.m)
        elif self.type==203: # power flow trafo reactive
            return self.val - conv_acdc[self.k].Qtf(self.m)
        elif self.type==220:
            return self.val - conv_acdc[self.k].Prc(self.m)
        elif self.type==230:
            return self.val - conv_acdc[self.k].Qrc(self.m)
        elif self.type==244:
            return self.val - graph[conv_acdc[self.k].i_busconv].V/graph_dc[conv_acdc[self.k].i_busdc].Vdc
        elif self.type==245:
            return self.val - (graph[conv_acdc[self.k].i_busac].theta - graph[conv_acdc[self.k].i_busconv].theta)
        elif self.type==299: # conv constraints
            return -(conv_acdc[self.k].Pdc_se(graph_dc) + conv_acdc[self.k].Pac_se(graph) + conv_acdc[self.k].Ploss_se(graph))


class meas_dc(meas):
    def __init__(self,k,m,type,val,prec,br_id=None,dire=0) -> None:
        super().__init__(k,m,type,val,prec,br_id=br_id,dire=dire)
        self.sigma=np.abs(val)*prec/3
    def dz(self,graph_dc):
        if self.type==100: # DC power flow injection measurement
            return self.val-graph_dc[self.k].Pdc(graph_dc)
        elif self.type==101: # current injection measurement
            return self.val-graph_dc[self.k].Idc(graph_dc)
        elif self.type==102: # DC power flow measurement
            return self.val-graph_dc[self.k].adj[self.br_id].Pfdc(graph_dc,self.direction) #TODO modify this in the AC code
        elif self.type==103:
            return self.val-graph_dc[self.k].adj[self.br_id].Ifdc(graph_dc,self.direction) #TODO modify this in the AC code
        elif self.type==104: # DC voltage measurement
            return self.val-graph_dc[self.k].Vdc        
        else:
            raise ValueError("nonexistent measurement type in DC system")
        
    
    


class state():
    def __init__(self,v,t) -> None:
        self.v=v
        self.t=t


class prioriMAP():
    def __init__(self,graph,var_tcsc={},var_svc={},var_UPFC={},flag_priori=0,H=[],W=[],lamb=1.0) -> None:
        self.flag_priori=flag_priori
        self.node=[]
        self.tcsc={}
        self.svc={}
        self.upfc_tse={}
        self.upfc_tsh={}
        self.upfc_Vse={}
        self.upfc_Vsh={}
        
        i=0
        for no in graph:
            self.node.append(node_priori(graph[i].V,graph[i].theta))
            i=i+1

        for key, item in var_tcsc.items():
            k=int(key.split("-")[0])
            self.tcsc[key]=graph[k].adjk[key].xtcsc

        for key,item in var_svc.items():
            self.svc[key]=graph[key].SVC.BSVC

        for key,item in var_UPFC.items():
            p,s = key.split("-")
            p=int(p)
            self.upfc_tse[key]=graph[p].bUFPC_adjk[key].t_se
            self.upfc_tsh[key]=graph[p].bUFPC_adjk[key].t_sh
            self.upfc_Vse[key]=graph[p].bUFPC_adjk[key].Vse
            self.upfc_Vsh[key]=graph[p].bUFPC_adjk[key].Vsh

        self.H=H
        self.W=W
        self.P_inv=lamb*self.H.T@self.W@self.H

        Wmei_prio=np.diag(np.sqrt(np.diag(W)))

        self.WmeiH=np.sqrt(lamb)*Wmei_prio@H
        


        

class node_priori():
    def __init__(self,V,theta):
        self.V=V
        self.theta=theta




class branch_dc():
    def __init__(self,id,fr,to,i):
        self.id=id
        self.fr=fr
        self.to=to
        self.i=i
        self.r=-1
        self.p=1
    def Pfdc(self,graph,flag):
        if flag==0:
            k=self.fr
            m=self.to
        else:
            k=self.to
            m=self.fr
        return self.p*graph[k].Vdc*(graph[k].Vdc-graph[m].Vdc)/self.r
    def Ifdc(self,graph,flag):
        if flag==0:
            k=self.fr
            m=self.to
        else:
            k=self.to
            m=self.fr
        return self.p*(graph[k].Vdc-graph[m].Vdc)/self.r
    def dPfdc_dVdc(self,graph,flag,var):
        if flag==0:
            k=self.fr
            m=self.to
        else:
            k=self.to
            m=self.fr
        if k==var: # dPkm/dVdck
            return self.p*(2*graph[k].Vdc-graph[m].Vdc)/self.r
        else: # dPkm/dVdcm
            return -self.p*graph[k].Vdc/self.r
    def dIfdc_dVdc(self,graph,flag,var):
        if flag==0:
            k=self.fr
            m=self.to
        else:
            k=self.to
            m=self.fr
        if k==var: # dIfkm/dVdck
            return self.p*1/self.r
        else: # dIfkm/dVdcm
            return -self.p*1/self.r


class node_graph_dc():
    def __init__(self,id,bus_dc):
        self.Vdc=1
        self.adjk=dict()
        self.adjm=dict()
        self.adj=dict()
        self.ladjk=[]
        self.ladjm=[]
        self.id=id
        self.bus_dc=bus_dc
        self.FlagConvACDC=0
        self.dconv_acdc={}
    def Pdc(self,graph):
        Pdc=0
        for key in self.adjk.keys():
            Pdc+=self.adjk[key].Pfdc(graph,0)
        for key in self.adjm.keys():
            Pdc+=self.adjm[key].Pfdc(graph,1)
        return Pdc
    def Idc(self,graph):
        Idc=0
        for key in self.adjk.keys():
            Idc+=self.adjk[key].Ifdc(graph,0)
        for key in self.adjm.keys():
            Idc+=self.adjm[key].Ifdc(graph,1)
        return Idc
        
