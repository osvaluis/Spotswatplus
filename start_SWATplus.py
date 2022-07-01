# -*- coding: utf-8 -*-
"""
Created on Mon Oct  8 21:21:49 2018

@author: Camargos C / Luis Barresi
"""

import numpy as np
#import random
import subprocess as sub
import SWATplus_ReadOut_v01 as read
import SWATplus_Manipulate_v01 as man
import os, shutil
from mpi4py import MPI
import spotpy
import matplotlib.pyplot as plt
import pandas as pd
from spotpy.likelihoods import gaussianLikelihoodMeasErrorOut as GausianLike

class spot_setup(object):
    def __init__(self,para):
    	self.parameter_fname = 'input_swatplus.txt'
    	self.observeddata_fname = 'observed'+os.sep+'discharge-ls.txt'	
    	self.observeddata = np.loadtxt(self.observeddata_fname)
    	self.nr_of_observations = len(self.observeddata)	
    	self.para = para
    	self.parf = np.genfromtxt(self.parameter_fname, delimiter=',', dtype=None, encoding='ascii') 
    	self.params = []
    	for i in range(len(self.parf)):
            self.params.append(spotpy.parameter.Uniform(name=self.parf[i][0],low=self.parf[i][1],
                                high=self.parf[i][2], step=np.mean([np.abs(self.parf[i][1]),np.abs(self.parf[i][2])])/5.0))
      
    def parameters(self):
    	return spotpy.parameter.generate(self.params)

    def onerror(self, func, path, exc_info):
        """
        Error handler for ``shutil.rmtree``.
    
        If the error is due to an access error (read only file)
        it attempts to add write permission and then retries.
    
        If the error is for another reason it re-raises the error.
    
        Usage : ``shutil.rmtree(path, onerror=onerror)``
        """
        import stat
        if not os.access(path, os.W_OK):
            # Is the error an access error ?
            os.chmod(path, stat.S_IWUSR)
            func(path)
        else:
            raise
        
    def simulation(self,vector):    
        try:
            #when OS is linux
            core_nr = str(int(os.environ['OMPI_COMM_WORLD_RANK'])+1) #if necessary,+1 to prevent zero
        except KeyError: 
            #when OS is windows
            comm = MPI.COMM_WORLD 
            core_nr = str(comm.Get_rank()+1) #if necessary,+1 to prevent zero
        pathdir = 'calib_parallel'+ os.sep +'parallel_'+core_nr 
        if os.path.exists(pathdir+ os.sep):
                shutil.rmtree(pathdir, onerror=self.onerror)
                print('Deleting folder ' + pathdir)
                try:
                    shutil.copytree('TxtInOut', pathdir)
                except WindowsError as e:
                    print ("ERROR: WINDOWSERROR = ",e)
                except :
                    print ("ERROR: Some other error happened")
                #shutil.copytree('TxtInOut', pathdir)
                print('Copying folder ' + pathdir)
        else:
                shutil.copytree('TxtInOut', pathdir)
                print('Copying folder ' + pathdir)
			
        
        data=vector

        latq_co = data[0]
        #slp = data[1]
        cn_b = data[1]   
        #k = data[2]
        #mann = data[4]
        cn3_swf = data[2]
        awc = data[3]
        #soilk = data[5]        
        #bd = data[6]
        alpha_bf = data[4]
        rchg_dp = data[5]
        revap = data[6]
        revap_min = data[7]
        flo_min = data[8]
        #bf_max = data[11]
        sp_yld = data[9]
        #lat_ttime = data[9]
        #can_max = data[8]
        esco = data[10]
        #ovn_mean = data[17]
        #slp_len = data[28]       
        #epco = data[11]
        #perco = data[9]
        #melt_tmp = data[0]
        #fall_tmp = data[1]
        #surq_lag = data[2]        
        
        Manipulator = man.parManipulator
        
        # for d in Manipulator.bsn(pathdir,core_nr):
        #       d.setChangePar("surq_lag",surq_lag,"s")
        #       d.finishChangePar(core_nr)
        # for d in Manipulator.sno(pathdir,core_nr):
        #       d.setChangePar("melt_tmp",melt_tmp,"s")
        #       d.setChangePar("fall_tmp",fall_tmp,"s")
        #       d.finishChangePar(core_nr)
        #for d in Manipulator.cha(pathdir,core_nr):
              #d.setChangePar("mann",mann,"s")
              #d.setChangePar("k",k,"*")
              #d.finishChangePar(core_nr)
        for d in Manipulator.sol(pathdir,core_nr):
              d.setChangePar("awc",awc,"+")
              #d.setChangePar("soil_k",soilk,"*")
              #d.setChangePar("bd",bd,"*")
              #d.finishChangePar(core_nr)
        for d in Manipulator.aqu(pathdir,core_nr):
              d.setChangePar("alpha_bf",alpha_bf,"s")
              d.setChangePar("rchg_dp",rchg_dp,"s")
              d.setChangePar("revap",revap,"s")
              d.setChangePar("revap_min",revap_min,"s")
              d.setChangePar("flo_min",flo_min,"s")
              #d.setChangePar("bf_max",bf_max,"s")
              d.setChangePar("spec_yld", sp_yld, "s")
              d.finishChangePar(core_nr)
        for d in Manipulator.hyd(pathdir,core_nr):
              d.setChangePar("esco",esco,"s")
              #d.setChangePar("lat_ttime",lat_ttime,"s")
              #d.setChangePar("can_max",can_max,"s")
              d.setChangePar("latq_co", latq_co, "s")
              #d.setChangePar("epco",epco,"s")
              #d.setChangePar("perco",perco,"s")
              d.setChangePar("cn3_swf", cn3_swf, "*")
              d.finishChangePar(core_nr)
        for d in Manipulator.cn(pathdir,core_nr):
              d.setChangePar("cn_b",cn_b,"*")
              #d.finishChangePar(core_nr)
        #for d in Manipulator.ovn(pathdir,core_nr):
              #d.setChangePar("ovn_mean",ovn_mean,"*")
              #d.finishChangePar(core_nr)
        #for d in Manipulator.top(pathdir,core_nr):
              #d.setChangePar("slp",slp,"*")
              #d.setChangePar("slp_len",slp_len,"s")
              #d.setChangePar("lat_len",lat_len,"+")
              #d.finishChangePar(core_nr)
#        for d in cal:
#              d.setChangePar("snomelt_tmp",snomelt_tmp,"s")
#              d.setChangePar("snofall_tmp",snofall_tmp,"s")
#              d.setChangePar("surlag",surlag,"s")
#              d.finishChangePar(core_nr)       
        try:
                  curdir = os.getcwd() 
                  os.chdir('calib_parallel'+os.sep+'parallel_'+core_nr)
                  sub.call(['rev60.5.4_64rel.exe'])
                  os.chdir(curdir)
                  #subbasins = [13] #subbasin number where output should be extracted
                  channels = [25] #channel number where output should be extracted
                  results_class = read.channel_sd_day(["flo_out"],channels,core_nr)
                  results = []
                  for channel in channels:
                      results.append(results_class.outValues['flo_out'][channel])
                  print('Total discharge: ',round(sum(results[0]),3), 'm3.s-1')

        except:
            raise
            print("SWAT produced an error, returning nans")
            results = [[np.nan]*self.nr_of_observations] # Number of simulations that SWAT creates (without warm-up period)
        return results
                  
    def evaluation(self):
        # Load Observation data here and return them as lists [[],[],[]...]
        observationdatalists = []
        observationdatalists.append(self.observeddata)        
        return observationdatalists
    
    
    
    def objectivefunction(self,simulation,evaluation):
        indexs=[]      
        for obs in evaluation:
            index=[]
            for i in range(len(obs)):
                if not obs[i] == -9999: #used for missing observation data
                #if not (obs[i] == -9999.0 or obs[i] < 1.0): #used for missing observation data
                    index.append(i)
            #print(index)                    
            indexs.append(index)
        sub = np.array(simulation[0])[indexs[0]]
        print(sub)
        print(evaluation[0][indexs[0]])
        df1 = pd.date_range(start="2003-01-01",end="2007-12-31").to_pydatetime().tolist()
        plt.figure(figsize=(12, 8))
        plt.plot(df1, sub, label='simulated', 
        linewidth=1)
        plt.plot(df1, evaluation[0][indexs[0]], color='red', 
        label='observed', linewidth=1)
        plt.title('Streamflow')
        plt.xlabel('Date')
        plt.ylabel('flow')
        plt.legend()
        plt.tight_layout()
        plt.show() 
        #sub_lognse = spotpy.objectivefunctions.lognashsutcliffe(evaluation[0][indexs[0]],sub, epsilon=0.001)
        likelihood = GausianLike(evaluation, simulation)
        sub_nse = spotpy.objectivefunctions.nashsutcliffe(evaluation, simulation)
        sub1 = sub_nse #- 1
        #return sub1
        return [likelihood, sub1]
            
if __name__ == "__main__":
    parallel = 'mpi' if 'OMPI_COMM_WORLD_SIZE' in os.environ else 'seq'
    starter = spot_setup(parallel) #Initiate class
    sampler = spotpy.algorithms.dream(starter,dbname='calib_parallel'+os.sep+'SWATplus_dream',dbformat='csv',parallel=parallel)
    sampler.sample(repetitions=3000)