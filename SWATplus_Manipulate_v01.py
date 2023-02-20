# -*- coding: utf-8 -*-
"""
Created on Wed Sep 26 17:28:57 2018

@author: Camargos C / Luis Barresi
"""
import os
from mpi4py import MPI

class InputFileManipulator(object):
    # connect Object with a SWATplus input file
    def __init__(self, filename, parList, core_nr):
        pathdir = 'calib_parallel'+ os.sep +'parallel_'+core_nr
        self.filename = filename
        ffile = open(pathdir+os.sep+self.filename, "r")        
        self.textOld = ffile.readlines()
        self.file_len = len(self.textOld)
        ffile.close()
        self.initParValue(parList)
        self.prepareChangePar()
                   
    def initParValue(self, parList):
        for namePar in parList:
            row, col1, col2, dig, minValue, maxValue = self.parInfo[namePar]
            self.parValue[namePar] = [float(self.textOld[row-1][col1:col2])]
    
    def prepareChangePar(self):
        self.textNew = self.textOld[:] # copy instead of new name allocation
    
    # built to be overridden if one parameter exists several times in each file, e.g. for different soil layers
    def setChangePar(self, namePar, changePar, changeHow):
        self.changePar(namePar, changePar, changeHow)

    def changePar(self, namePar, changePar, changeHow, offsetRow=0, offsetCol=0, index=0):
        # change initial parameter depending on chosen method
        changePar = float(changePar)
        if changeHow == "+":
            changedPar = self.parValue[namePar][index] + changePar
        elif changeHow == "*":
            changedPar = self.parValue[namePar][index] + self.parValue[namePar][index] * changePar
        elif changeHow == "s":
            changedPar = changePar
        # insert changed Parameter in textNew
        row, col1, col2, dig, minValue, maxValue = self.parInfo[namePar]
        if changedPar < minValue:
            print(namePar,":", changedPar, " replaced by MIN acceptable value" )
            changedPar = minValue
        elif changedPar > maxValue:
            print(namePar,":", changedPar, " replaced by MAX acceptable value" )
            changedPar = maxValue
        row += offsetRow
        col1 += offsetCol
        col2 += offsetCol
        format = "%" + str(col2-col1+1) + "." + str(dig) + "f"
        self.textNew[row-1] = (self.textNew[row-1][:col1-1] +
                            (format%changedPar).rjust(col2-col1+1) +
                            self.textNew[row-1][col2:])

    # save textNew in file (file ready for SWAT)
    def finishChangePar(self,core_nr):
        #try:
        #      core_nr = str(int(os.environ['OMPI_COMM_WORLD_RANK'])) # +1 to prevent zero if necessary...
        #except KeyError:
        #      core_nr = str(1)#str(int(np.random.uniform(0,1000))) # if you run on windows
        ffile = open('calib_parallel'+os.sep+'parallel_'+core_nr+os.sep+self.filename, "w")
        ffile.writelines(self.textNew)
        ffile.close
        self.prepareChangePar()

    def landuseNames():
        try:
            #when OS is linux
            core_nr = str(int(os.environ['OMPI_COMM_WORLD_RANK'])+1) #if necessary,+1 to prevent zero
        except KeyError: 
            #when OS is windows
            comm = MPI.COMM_WORLD 
            core_nr = str(comm.Get_rank()+1) #if necessary,+1 to prevent zero
        lumfile = open('calib_parallel'+os.sep+'parallel_'+core_nr+os.sep+ 'landuse.lum', "r")
        lumtext = lumfile.readlines()
        lum_len = len(lumtext)
        lumfile.close()
        parinfo = (3, 75, 92, 0)
        lumrow, lumcol1, lumcol2, lumdig = parinfo
        luNames = []
        for i in range(lum_len-2):
            luNames.append(lumtext[lumrow-1][lumcol1:lumcol2].split())
            lumrow += 1
        return luNames
               
            
class calManipulator(InputFileManipulator):
    # Comment from Carla:
    # {"name": ("Line in File", "first column", "last column", "decimal digits") 
    # TODO: Instead of hardcoding the positions, the position in the file should be searched automatically using the parameter name
    parInfo = {"number":     (2,  1,  5,0), #I NEED TO VERIFY THIS NUMBERS WITH CARLA
               "cal_parm":   (4,  1, 23,0),
               "chg_typ":    (4, 24, 30,0),
               "chg_val":    (4, 31, 44,5),
               "conds":      (4, 45, 54,0),
               "soil_lyr1":  (4, 55, 64,0),
               "soil_lyr2":  (4, 65, 74,0),
               "yr1":        (4, 75, 84,0),
               "yr2":        (4, 85, 94,0),
               "day1":       (4, 95,104,0),
               "day2":       (4,105,114,0),
               "obj_tot":    (4,115,124,0),
               #"snomelt_tmp":    (4, 31, 44,5),
               #"snofall_tmp":    (5, 31, 44,5),
               #"surlag":    (6, 31, 44,5)
               }
    def __init__(self, filename, parList, core_nr):
        self.parValue = {"number": None,
               "cal_parm":    None,
               "chg_typ":     None,
               "chg_val":     None,
               "conds":       None,
               "soil_lyr1":   None,
               "soil_lyr2":   None,
               "yr1":         None,
               "yr2":         None,
               "day1":        None,
               "day2":        None,
               "obj_tot":     None,
               #"snomelt_tmp":    None,
               #"snofall_tmp":    None,
               #"surlag":    None
               }
        InputFileManipulator.__init__(self, filename, parList, core_nr) 
                   
class bsnManipulator(InputFileManipulator):
    #information about parameters:
    #(1)row in file, (2) first and (2) last relevant column in row
    # and (4) digits
    parInfo = {"lai_noevap":   (3,  1, 12,5,0,10),
               "sw_init":      (3, 13, 26,5,0,1),
               "surq_lag":     (3, 27, 40,5,0.05,24),
               "adj_pkrt":     (3, 41, 54,5,0.5,2),
               "adj_pkrt_sed": (3, 55, 68,5,0,2),
               "lin_sed":      (3, 69, 82,5,0.0001,0.01),
               "exp_sed":      (3, 83, 96,5,1,1.5),
               "orgn_min":     (3, 97,110,5,0.001,0.003),
               "n_uptake":     (3,111,124,5,0,100),
               "p_uptake":     (3,125,138,5,0,100),
               "n_perc":       (3,139,152,5,0,1),
               "p_perc":       (3,153,166,5,10,17.5),
               "p_soil":       (3,167,180,5,100,200),
               "p_avail":      (3,181,194,5,0.01,0.7),
               "rsd_decomp":   (3,195,208,5,0.02,0.1),
               "pest_perc":    (3,209,222,5,0,1),
               "msk_co1":      (3,223,236,5,0,10),
               "msk_co2":      (3,237,250,5,0,10),
               "msk_x":        (3,251,264,5,0,0.3),
               #"trans_loss":   (3,265,278,5,0,1),
               "nperco_lchtile": (3,265,278,5,0,1),
               "evap_adj":     (3,281,294,5,0.5,1),
               #"cn_co":        (3,293,306,5,0,1),
               "scoef":        (3,295,308,5,0,1),
               "denit_exp":    (3,309,322,5,0,3),
               "denit_frac":   (3,323,336,5,0,1),
               "man_bact":     (3,337,350,5,0,1),
               "adj_uhyd":     (3,351,364,5,0,1),
               "cn_froz":      (3,365,378,5,0,0),#
               "dorm_hr":      (3,379,392,5,0,24),
               #"s_max":        (3,391,404,5,0,0),#
               "plaps":        (3,393,406,5,0,0),
               #"n_fix":        (3,405,418,5,0,1),
               "tlaps":        (3,407,420,5,0,1),
               "n_fix_max":    (3,421,434,5,1,20),
               "rsd_decay":    (3,435,448,5,0,0.05),
               "rsd_cover":    (3,449,462,5,0.1,0.5),
               #"vel_crit":     (3,461,474,5,0,10),
               "urb_init_abst":(3,463,477,5,0,10),
               #"res_sed":      (3,475,488,5,0.09,0.27),
               "petco_pmpt":   (3,478,491,5,0.09,0.27),
               "uhyd_alpha":   (3,492,505,5,0.5,10),
               "splash":       (3,506,519,5,0.9,3.1),
               "rill":         (3,520,533,5,0.5,2),
               "surq_exp":     (3,534,547,5,1,3),
               "cov_mgt":      (3,548,561,5,0.001,0.45),
               "cha_d50":      (3,562,575,5,10,100),
               #"cha_part_sd":  (3,573,586,5,1,5),
               "co2":          (3,576,589,5,1,5),
               #"adj_cn":       (3,587,600,5,0,0),#
               "day_lag_max":  (3,590,603,5,0,0),
               "igen":         (3,604,611,0,0,1)}
# expands init-method of FileManipulator to generate parValue-dictionaries for individual instances
    def __init__(self, filename, parList, core_nr):
        self.parValue = {"lai_noevap":   None,
               "sw_init":      None,
               "surq_lag":     None,
               "adj_pkrt":     None,
               "adj_pkrt_sed": None,
               "lin_sed":      None,
               "exp_sed":      None,
               "orgn_min":     None,
               "n_uptake":     None,
               "p_uptake":     None,
               "n_perc":       None,
               "p_perc":       None,
               "p_soil":       None,
               "p_avail":      None,
               "rsd_decomp":   None,
               "pest_perc":    None,
               "msk_co1":      None,
               "msk_co2":      None,
               "msk_x":        None,
               #"trans_loss":   None,
               "nperco_lchtile":   None,
               "evap_adj":     None,
               #"cn_co":        None,
               "scoef":        None,
               "denit_exp":    None,
               "denit_frac":   None,
               "man_bact":     None,
               "adj_uhyd":     None,
               "cn_froz":      None,
               "dorm_hr":      None,
               #"s_max":        None,
               "plaps":        None,
               #"n_fix":        None,
               "tlaps":        None,
               "n_fix_max":    None,
               "rsd_decay":    None,
               "rsd_cover":    None,
               #"vel_crit":     None,
               "urb_init_abst": None,
               #"res_sed":      None,
               "petco_pmpt":   None,
               "uhyd_alpha":   None,
               "splash":       None,
               "rill":         None,
               "surq_exp":     None,
               "cov_mgt":      None,
               "cha_d50":      None,
               #"cha_part_sd":  None,
               "co2":          None,
               #"adj_cn":       None,
               "day_lag_max":  None,
               "igen":         None}
        InputFileManipulator.__init__(self, filename, parList, core_nr)
    bsnParList = ["lai_noevap","sw_init","surq_lag","adj_pkrt","adj_pkrt_sed","lin_sed",
                  "exp_sed","orgn_min","n_uptake","p_uptake","n_perc","p_perc","p_soil",
                  "p_avail","rsd_decomp","pest_perc","msk_co1","msk_co2","msk_x",#"trans_loss",
                  "nperco_lchtile",
                  "evap_adj",#"cn_co", 
                  "scoef",
                  "denit_exp","denit_frac","man_bact","adj_uhyd","cn_froz",
                  "dorm_hr",#"s_max",
                  "plaps", #"n_fix",
                  "tlaps", "n_fix_max","rsd_decay","rsd_cover",#"vel_crit",
                  "urb_init_abst", #"res_sed", 
                  "petco_pmpt","uhyd_alpha","splash","rill","surq_exp","cov_mgt","cha_d50",
                  #"cha_part_sd",
                  "co2",#"adj_cn", 
                  "day_lag_max", "igen"]
                      
class snoManipulator(InputFileManipulator):
    parInfo = {"name":      (3,  1,  7,0,0,0),
               "fall_tmp":  (3,  8, 30,5,-5,5),
               "melt_tmp":  (3, 31, 44,5,-5,5),
               "melt_max":  (3, 45, 58,5,0,10),
               "melt_min":  (3, 59, 72,5,0,10),
               "tmp_lag":   (3, 73, 86,5,0,1),
               "snow_h2o":  (3, 87,100,5,0,500),
               "cov50":     (3,101,114,5,0,1),
               "snow_init": (3,115,128,5,0,5)}
    def __init__(self, filename, parList, core_nr):
        self.parValue = {"name": None,
               "fall_tmp":  None,
               "melt_tmp":  None,
               "melt_max":  None,
               "melt_min":  None,
               "tmp_lag":   None,
               "snow_h2o":  None,
               "cov50":     None,
               "snow_init": None}
        InputFileManipulator.__init__(self, filename, parList, core_nr)
    snoParList = ["fall_tmp","melt_tmp","melt_max","melt_min","tmp_lag","snow_h2o","cov50",
                  "snow_init"]

class hydManipulator(InputFileManipulator):
    parInfo = {"name":      (3,  1,  7,0,0,0),
               "lat_ttime": (3,  8, 30,5,0,180),
               "lat_sed":   (3, 31, 44,5,0,5000),
               "can_max":   (3, 45, 58,5,0,100),
               "esco":      (3, 59, 72,5,0,1),
               "epco":      (3, 73, 86,5,0,1),
               "orgn_enrich":  (3, 87,100,5,0,5),
               "orgp_enrich":  (3,101,114,5,0,5),
               #"evap_pothole": (3,115,128,5,0,1),#cn3_swf
               "cn3_swf":  (3,115,128,5,0,1), 
               "bio_mix":  (3,129,142,5,0,1),
               "perco":    (3,143,156,5,0,1),
               "lat_orgn": (3,157,170,5,0,200),
               "lat_orgp": (3,171,184,5,0,200),
               "harg_pet": (3,185,198,5,0,0), #
               #"cn_plntet":(3,199,212,5,0.5,2)
               "latq_co":  (3,199,212,5,0.5,2)} 
    def __init__(self, filename, parList, core_nr):
        self.parValue = {"name": None,
               "lat_ttime": None,
               "lat_sed":   None,
               "can_max":   None,
               "esco":      None,
               "epco":      None,
               "orgn_enrich":  None,
               "orgp_enrich":  None,
               #"evap_pothole": None,
               "cn3_swf":  None,
               "bio_mix":  None,
               "perco":    None,
               "lat_orgn": None,
               "lat_orgp": None,
               "harg_pet": None,
               #"cn_plntet":None
               "latq_co": None}
        InputFileManipulator.__init__(self, filename, parList, core_nr)
    hydParList = ["lat_ttime","lat_sed","can_max","esco","epco","orgn_enrich","orgp_enrich", 
                  #"evap_pothole",
                  "cn3_swf", "bio_mix","perco","lat_orgn","lat_orgp","harg_pet", "latq_co"
                  #"cn_plntet"
                  ]                  
                      
class chaManipulator(InputFileManipulator):
    parInfo = {"name":      (3,  1, 15,0,0,0,0,0),
               "order":     (3, 16, 34,0,0,0),
               "wd":        (3, 35, 48,5,0,1000),
               "dp":        (3, 49, 62,5,0,30),
               "slp":       (3, 63, 76,5,0,10),
               "len":       (3, 77, 90,5,0,500),
               "mann":      (3, 91,104,5,0,0.3),
               "k":         (3,105,118,5,0,500),
               "erod_fact": (3,119,132,5,0,0.6),
               "cov_fact":  (3,133,146,5,0,1),
               #"hc_cov":    (3,147,160,5,0.5,100), #wdrto
               "wd_rto":    (3,147,160,5,0.5,100),
               "eq_slp":    (3,161,174,5,0,0), #chseq
               "d50":       (3,175,188,5,1,10000),
               "clay":      (3,189,202,5,0,100),
               "carbon":    (3,203,216,5,0,15), 
               "dry_bd":    (3,217,230,5,0.9,3),
               "side_slp":  (3,231,244,5,0,5),
               "bed_load":  (3,245,258,5,0,1),
               #"t_conc":    (3,259,272,5,1,86400),
               "fps":       (3,259,272,5,1,86400),
               #"shear_bnk": (3,273,286,5,0,0),
               "fpn":       (3,273,286,5,0,0),
               #"hc_erod":   (3,287,300,5,0,1),
               "n_conc":    (3,287,300,5,0,1),
               #"hc_ht":     (3,301,314,5,0,0), 
               "p_conc":    (3,301,314,5,0,0),
               #"hc_len":    (3,315,328,5,0,0)
               "p_bio":     (3,315,328,5,0,0)} #
    def __init__(self, filename, parList, core_nr):
        self.parValue = {"name": None,
               "order":     None,
               "wd":        None,
               "dp":        None,
               "slp":       None,
               "len":       None,
               "mann":      None,
               "k":         None,
               "erod_fact": None,
               "cov_fact":  None,
               #"hc_cov":    None,
               "wd_rto":    None,
               "eq_slp":    None,
               "d50":       None,
               "clay":      None,
               "carbon":    None,
               "dry_bd":    None,
               "side_slp":  None,
               "bed_load":  None,
               #"t_conc":    None,
               "fps":       None,
               #"shear_bnk": None,
               "fpn":       None,
               #"hc_erod":   None,
               "n_conc":    None,
               #"hc_ht":     None,
               "p_conc":    None,
               #"hc_len":    None
               "p_bio":     None}
        InputFileManipulator.__init__(self, filename, parList, core_nr)
    chaParList = ["wd","dp","slp","len","mann","k","erod_fact","cov_fact",
                  #"hc_cov",
                  "wd_rto", "eq_slp","d50","clay","carbon","dry_bd","side_slp","bed_load",
                  #"t_conc","shear_bnk","hc_erod","hc_ht","hc_len"
                  "fps", "fpn", "n_conc", "p_conc", "p_bio"]                      
        
    # overrides initParValue: multiple HRUs have to be considered.    
    def initParValue(self, parList):
        for namePar in parList:
            row, col1, col2, dig, minValue, maxValue = self.parInfo[namePar]
            llist = []
            for i in range(self.file_len-3):
                llist.append(float(self.textOld[row-1][col1:col2]))
                row += 1
            self.parValue[namePar] = llist

    # overrides setChangePar: multiple HRUs have to be considered.
    def setChangePar(self, namePar, changePar, changeHow):
        n_par = len(self.parValue[namePar])
        #print(n_par)
        for index in range(n_par):
            offsetRow = index
            self.changePar(namePar, changePar, changeHow, offsetRow, 0, index)
            #print(self.parValue[namePar][index])

class topManipulator(InputFileManipulator):
    parInfo = {"name":       (3,  1, 15,0,0,0),
               "slp":        (3, 17, 30,5,0,1),
               "slp_len":    (3, 31, 44,5,10,150),
               "lat_len":    (3, 45, 58,5,0,150),
               "dist_cha":   (3, 59, 72,5,0,100000),
               "depos":      (3, 73, 86,5,1,1)} #
    def __init__(self, filename, parList, core_nr):
        self.parValue = {"name": None,
               "slp":         None,
               "slp_len":     None,
               "lat_len":     None,
               "dist_cha":    None,
               "depos":       None}
        InputFileManipulator.__init__(self, filename, parList, core_nr)
    topParList = ["slp","slp_len","lat_len","dist_cha","depos"]
    
    # overrides initParValue: multiple HRUs have to be considered.    
    def initParValue(self, parList):
        for namePar in parList:
            row, col1, col2, dig, minValue, maxValue = self.parInfo[namePar]
            llist = []
            for i in range(self.file_len-3):
                llist.append(float(self.textOld[row-1][col1:col2]))
                row += 1
            self.parValue[namePar] = llist

    # overrides setChangePar: multiple HRUs have to be considered.
    def setChangePar(self, namePar, changePar, changeHow):
        n_par = len(self.parValue[namePar])
        #print(n_par)
        for index in range(n_par):
            offsetRow = index
            self.changePar(namePar, changePar, changeHow, offsetRow, 0, index)
            #print(self.parValue[namePar][index])
            
class aquManipulator(InputFileManipulator):
    parInfo = {"name":       (3,  8, 17,0,0,0),
               "init":       (3, 18, 44,0,0,0),
               "gw_flo":     (3, 45, 58,5,0,2),
               "dep_bot":    (3, 59, 72,5,0,10),
               "dep_wt":     (3, 73, 86,5,0,10),
               "no3_n":      (3, 87,100,5,0,1000),
               "sol_p":      (3,101,114,5,0,1000),
               #"ptl_n":      (3,115,128,5,0,15),
               "carbon":     (3,115,128,5,0,15),
               #"ptl_p":      (3,129,142,5,0,1000),
               "flo_dist":   (3,129,142,5,0,1000),
               "bf_max":     (3,143,156,5,0,2),
               "alpha_bf":   (3,157,170,5,0,1),
               "revap":      (3,171,184,5,0.02,0.2),
               "rchg_dp":    (3,185,198,5,0,1),
               "spec_yld":   (3,199,212,5,0,0.4),
               "hl_no3n":    (3,213,226,5,0,200),
               "flo_min":    (3,227,240,5,0,10),
               "revap_min":  (3,241,254,5,0,10)}
    def __init__(self, filename, parList, core_nr):
        self.parValue = {"name": None,
                      "init": None,
               "gw_flo":     None,
               "dep_bot":    None,
               "dep_wt":     None,
               "no3_n":      None,
               "sol_p":      None,
               #"ptl_n":      None,
               "carbon":     None,
               #"ptl_p":      None,
               "flo_dist":   None,
               "bf_max":     None,
               "alpha_bf":   None,
               "revap":      None,
               "rchg_dp":    None,
               "spec_yld":   None,
               "hl_no3n":    None,
               "flo_min":    None,
               "revap_min":  None}
        InputFileManipulator.__init__(self, filename, parList, core_nr)
    aquParList = ["gw_flo","dep_bot","dep_wt","no3_n","sol_p",#"ptl_n",
                  "carbon", #"ptl_p",
                  "flo_dist", "bf_max",
                  "alpha_bf","revap","rchg_dp","spec_yld","hl_no3n","flo_min","revap_min"]
    
    # overrides initParValue: multiple HRUs have to be considered.    
    def initParValue(self, parList):
        for namePar in parList:
            row, col1, col2, dig, minValue, maxValue = self.parInfo[namePar]
            llist = []
            for i in range(self.file_len-3):
                llist.append(float(self.textOld[row-1][col1:col2]))
                row += 1
            self.parValue[namePar] = llist

    # overrides setChangePar: multiple HRUs have to be considered.
    def setChangePar(self, namePar, changePar, changeHow):
        n_par = len(self.parValue[namePar])
        #print(n_par)
        for index in range(n_par):
            offsetRow = index
            self.changePar(namePar, changePar, changeHow, offsetRow, 0, index)
            #print(self.parValue[namePar][index])
            
class cnManipulator(InputFileManipulator):
    parInfo = {"name":      (3,  0, 21,0,0,0),
               "cn_a":      (3, 22, 30,5,25,98),
               "cn_b":      (3, 31, 44,5,25,98),
               "cn_c":      (3, 45, 58,5,25,98),
               "cn_d":      (3, 59, 72,5,25,98)}
    def __init__(self, filename, parList, core_nr):
        self.parValue = {"name": None,
               "cn_a":     None,
               "cn_b":      None,
               "cn_c":      None,
               "cn_d":      None}
        InputFileManipulator.__init__(self, filename, parList, core_nr)
    cnParList = ["cn_a","cn_b","cn_c","cn_d"]
        
    # overrides initParValue: multiple HRUs have to be considered.    
    def initParValue(self, parList):
        luNames = InputFileManipulator.landuseNames()
        row1, col11, col12, dig1, minValue, maxValue = self.parInfo['name']           
        namelists = []
        for i in range(self.file_len-2):
            namelists.append(self.textOld[row1-1][col11:col12].split())
            row1 += 1
        for namePar in parList:
            row, col1, col2, dig, minValue, maxValue = self.parInfo[namePar]
            llist = []
            for i in range(self.file_len-2):
                llist.append(float(self.textOld[row-1][col1:col2]))
                row += 1
            self.row2 = []
            for i in luNames:
                if i in namelists and i != ['urban']:
                    self.row2.append(namelists.index(i))
            self.parValue[namePar] = llist

    # overrides setChangePar: multiple HRUs have to be considered.
    def setChangePar(self, namePar, changePar, changeHow):
        n_par = self.row2
        for index in n_par:
            offsetRow = index
            self.changePar(namePar, changePar, changeHow, offsetRow, 0, index)

    # def changePar(self, namePar, changePar, changeHow, offsetRow=0, offsetCol=0, index=0):
    #     # change initial parameter depending on chosen method
    #     changePar = float(changePar)
    #     #print(index)
    #     #print(changePar)
    #     #print(self.parValue[namePar])
    #     if changeHow == "+":
    #         changedPar1 = self.parValue[namePar][index] + changePar
    #     elif changeHow == "*":
    #         changedPar1 = self.parValue[namePar][index] + self.parValue[namePar][index] * changePar
    #     elif changeHow == "s":
    #         changedPar1 = changePar
    #     if changedPar1 < 98 and changedPar1 > 25:
    #         changedPar = changedPar1
    #     elif changedPar1 >= 98:
    #         changedPar = 98
    #     elif changedPar1 <= 25:
    #         changedPar = 25
    #     # insert changed Parameter in textNew
    #     row, col1, col2, dig = self.parInfo[namePar]
    #     row += offsetRow
    #     col1 += offsetCol
    #     col2 += offsetCol
    #     format = "%" + str(col2-col1+1) + "." + str(dig) + "f"
    #     self.textNew[row-1] = (self.textNew[row-1][:col1-1] +
    #                         (format%changedPar).rjust(col2-col1+1) +
    #                         self.textNew[row-1][col2:])
          
class cnINDIVManipulator(InputFileManipulator):
    parInfo = {"name":      (3,  0, 21,0),
               "cn_a3":      (3, 22, 30,5),
                      "cn_a4":      (4, 22, 30,5),
                      "cn_a5":      (5, 22, 30,5),
                      "cn_a6":      (6, 22, 30,5),
                      "cn_a7":      (7, 22, 30,5),
                      "cn_a8":      (8, 22, 30,5),
                      "cn_a9":      (9, 22, 30,5),                      
                      "cn_a10":      (10, 22, 30,5),
                      "cn_a11":      (11, 22, 30,5),
                      "cn_a12":      (12, 22, 30,5),
                      "cn_a13":      (13, 22, 30,5),
                      "cn_a14":      (14, 22, 30,5),
                      "cn_a15":      (15, 22, 30,5),
                      "cn_a16":      (16, 22, 30,5),
                      "cn_a17":      (17, 22, 30,5),
                      "cn_a18":      (18, 22, 30,5),
                      "cn_a19":      (19, 22, 30,5),
                      "cn_a20":      (20, 22, 30,5),
                      "cn_a21":      (21, 22, 30,5),
                      "cn_a22":      (22, 22, 30,5),
                      "cn_a23":      (23, 22, 30,5),
                      "cn_a24":      (24, 22, 30,5),
                      "cn_a25":      (25, 22, 30,5),
                      "cn_a26":      (26, 22, 30,5),
                      "cn_a27":      (27, 22, 30,5),
                      "cn_a28":      (28, 22, 30,5),
                      "cn_a29":      (29, 22, 30,5),
                      "cn_a30":      (30, 22, 30,5),
                      "cn_a31":      (31, 22, 30,5),
                      "cn_a32":      (32, 22, 30,5),
                      "cn_a33":      (33, 22, 30,5),
                      "cn_a34":      (34, 22, 30,5),
                      "cn_a35":      (35, 22, 30,5),
                      "cn_a36":      (36, 22, 30,5),
                      "cn_a37":      (37, 22, 30,5),
                      "cn_a38":      (38, 22, 30,5),
                      "cn_a39":      (39, 22, 30,5),
                      "cn_a40":      (40, 22, 30,5),
                      "cn_a41":      (41, 22, 30,5),
                      "cn_a42":      (42, 22, 30,5),
                      "cn_a43":      (43, 22, 30,5),
                      "cn_a44":      (44, 22, 30,5),
                      "cn_a45":      (45, 22, 30,5),
                      "cn_a46":      (46, 22, 30,5),
                      "cn_a47":      (47, 22, 30,5),
                      "cn_a48":      (48, 22, 30,5),
                      "cn_a49":      (49, 22, 30,5),
                      "cn_a50":      (50, 22, 30,5),
                      "cn_a51":      (51, 22, 30,5),
                      "cn_a52":      (52, 22, 30,5),
                      "cn_a53":      (53, 22, 30,5),
                      "cn_a54":      (54, 22, 30,5),
                      "cn_b3":      (3, 31, 44,5),
                      "cn_b4":      (4, 31, 44,5),
                      "cn_b5":      (5, 31, 44,5),
                      "cn_b6":      (6, 31, 44,5),
                      "cn_b7":      (7, 31, 44,5),
                      "cn_b8":      (8, 31, 44,5),
                      "cn_b9":      (9, 31, 44,5),
                      "cn_b10":      (10, 31, 44,5),
                      "cn_b11":      (11, 31, 44,5),
                      "cn_b12":      (12, 31, 44,5),
                      "cn_b13":      (13, 31, 44,5),
                      "cn_b14":      (14, 31, 44,5),
                      "cn_b15":      (15, 31, 44,5),
                      "cn_b16":      (16, 31, 44,5),
                      "cn_b17":      (17, 31, 44,5),
                      "cn_b18":      (18, 31, 44,5),
                      "cn_b19":      (19, 31, 44,5),
                      "cn_b20":      (20, 31, 44,5),
                      "cn_b21":      (21, 31, 44,5),
                      "cn_b22":      (22, 31, 44,5),
                      "cn_b23":      (23, 31, 44,5),
                      "cn_b24":      (24, 31, 44,5),
                      "cn_b25":      (25, 31, 44,5),
                      "cn_b26":      (26, 31, 44,5),
                      "cn_b27":      (27, 31, 44,5),
                      "cn_b28":      (28, 31, 44,5),
                      "cn_b29":      (29, 31, 44,5),
                      "cn_b30":      (30, 31, 44,5),
                      "cn_b31":      (31, 31, 44,5),
                      "cn_b32":      (32, 31, 44,5),
                      "cn_b33":      (33, 31, 44,5),
                      "cn_b34":      (34, 31, 44,5),
                      "cn_b35":      (35, 31, 44,5),
                      "cn_b36":      (36, 31, 44,5),
                      "cn_b37":      (37, 31, 44,5),
                      "cn_b38":      (38, 31, 44,5),
                      "cn_b39":      (39, 31, 44,5),
                      "cn_b40":      (40, 31, 44,5),
                      "cn_b41":      (41, 31, 44,5),
                      "cn_b42":      (42, 31, 44,5),
                      "cn_b43":      (43, 31, 44,5),
                      "cn_b44":      (44, 31, 44,5),
                      "cn_b45":      (45, 31, 44,5),
                      "cn_b46":      (46, 31, 44,5),
                      "cn_b47":      (47, 31, 44,5),
                      "cn_b48":      (48, 31, 44,5),
                      "cn_b49":      (49, 31, 44,5),
                      "cn_b50":      (50, 31, 44,5),
                      "cn_b51":      (51, 31, 44,5),
                      "cn_b52":      (52, 31, 44,5),
                      "cn_b53":      (53, 31, 44,5),
                      "cn_b54":      (54, 31, 44,5),
                      "cn_c3":      (3, 45, 58,5),
                      "cn_c4":      (4, 45, 58,5),
                      "cn_c5":      (5, 45, 58,5),
                      "cn_c6":      (6, 45, 58,5),
                      "cn_c7":      (7, 45, 58,5),
                      "cn_c8":      (8, 45, 58,5),
                      "cn_c9":      (9, 45, 58,5),
                      "cn_c10":      (10, 45, 58,5),
                      "cn_c11":      (11, 45, 58,5),
                      "cn_c12":      (12, 45, 58,5),
                      "cn_c13":      (13, 45, 58,5),
                      "cn_c14":      (14, 45, 58,5),
                      "cn_c15":      (15, 45, 58,5),
                      "cn_c16":      (16, 45, 58,5),
                      "cn_c17":      (17, 45, 58,5),
                      "cn_c18":      (18, 45, 58,5),
                      "cn_c19":      (19, 45, 58,5),
                      "cn_c20":      (20, 45, 58,5),
                      "cn_c21":      (21, 45, 58,5),
                      "cn_c22":      (22, 45, 58,5),
                      "cn_c23":      (23, 45, 58,5),
                      "cn_c24":      (24, 45, 58,5),
                      "cn_c25":      (25, 45, 58,5),
                      "cn_c26":      (26, 45, 58,5),
                      "cn_c27":      (27, 45, 58,5),
                      "cn_c28":      (28, 45, 58,5),
                      "cn_c29":      (29, 45, 58,5),
                      "cn_c30":      (30, 45, 58,5),
                      "cn_c31":      (31, 45, 58,5),
                      "cn_c32":      (32, 45, 58,5),
                      "cn_c33":      (33, 45, 58,5),
                      "cn_c34":      (34, 45, 58,5),
                      "cn_c35":      (35, 45, 58,5),
                      "cn_c36":      (36, 45, 58,5),
                      "cn_c37":      (37, 45, 58,5),
                      "cn_c38":      (38, 45, 58,5),
                      "cn_c39":      (39, 45, 58,5),
                      "cn_c40":      (40, 45, 58,5),
                      "cn_c41":      (41, 45, 58,5),
                      "cn_c42":      (42, 45, 58,5),
                      "cn_c43":      (43, 45, 58,5),
                      "cn_c44":      (44, 45, 58,5),
                      "cn_c45":      (45, 45, 58,5),
                      "cn_c46":      (46, 45, 58,5),
                      "cn_c47":      (47, 45, 58,5),
                      "cn_c48":      (48, 45, 58,5),
                      "cn_c49":      (49, 45, 58,5),
                      "cn_c50":      (50, 45, 58,5),
                      "cn_c51":      (51, 45, 58,5),
                      "cn_c52":      (52, 45, 58,5),
                      "cn_c53":      (53, 45, 58,5),
                      "cn_c54":      (54, 45, 58,5),
                      "cn_d3":      (3, 59, 72,5),
                      "cn_d4":      (4, 59, 72,5),
                      "cn_d5":      (5, 59, 72,5),
                      "cn_d6":      (6, 59, 72,5),
                      "cn_d7":      (7, 59, 72,5),
                      "cn_d8":      (8, 59, 72,5),
                      "cn_d9":      (9, 59, 72,5),
                      "cn_d10":      (10, 59, 72,5),
                      "cn_d11":      (11, 59, 72,5),
                      "cn_d12":      (12, 59, 72,5),
                      "cn_d13":      (13, 59, 72,5),
                      "cn_d14":      (14, 59, 72,5),
                      "cn_d15":      (15, 59, 72,5),
                      "cn_d16":      (16, 59, 72,5),
                      "cn_d17":      (17, 59, 72,5),
                      "cn_d18":      (18, 59, 72,5),
                      "cn_d19":      (19, 59, 72,5),
                      "cn_d20":      (20, 59, 72,5),
                      "cn_d21":      (21, 59, 72,5),
                      "cn_d22":      (22, 59, 72,5),
                      "cn_d23":      (23, 59, 72,5),
                      "cn_d24":      (24, 59, 72,5),
                      "cn_d25":      (25, 59, 72,5),
                      "cn_d26":      (26, 59, 72,5),
                      "cn_d27":      (27, 59, 72,5),
                      "cn_d28":      (28, 59, 72,5),
                      "cn_d29":      (29, 59, 72,5),
                      "cn_d30":      (30, 59, 72,5),
                      "cn_d31":      (31, 59, 72,5),
                      "cn_d32":      (32, 59, 72,5),
                      "cn_d33":      (33, 59, 72,5),
                      "cn_d34":      (34, 59, 72,5),
                      "cn_d35":      (35, 59, 72,5),
                      "cn_d36":      (36, 59, 72,5),
                      "cn_d37":      (37, 59, 72,5),
                      "cn_d38":      (38, 59, 72,5),
                      "cn_d39":      (39, 59, 72,5),
                      "cn_d40":      (40, 59, 72,5),
                      "cn_d41":      (41, 59, 72,5),
                      "cn_d42":      (42, 59, 72,5),
                      "cn_d43":      (43, 59, 72,5),
                      "cn_d44":      (44, 59, 72,5),
                      "cn_d45":      (45, 59, 72,5),
                      "cn_d46":      (46, 59, 72,5),
                      "cn_d47":      (47, 59, 72,5),
                      "cn_d48":      (48, 59, 72,5),
                      "cn_d49":      (49, 59, 72,5),
                      "cn_d50":      (50, 59, 72,5),
                      "cn_d51":      (51, 59, 72,5),
                      "cn_d52":      (52, 59, 72,5),
                      "cn_d53":      (53, 59, 72,5),
                      "cn_d54":      (54, 59, 72,5)}
    def __init__(self, filename, parList, core_nr):
        self.parValue = {"name": None,
                      "cn_a3":       None,
                      "cn_a4":       None,
                      "cn_a5":       None,
                      "cn_a6":       None,                      
                      "cn_a7":       None,
                      "cn_a8":       None,
                      "cn_a9":       None,
                      "cn_a10":       None,
                      "cn_a11":       None,
                      "cn_a12":       None,
                      "cn_a13":       None,
                      "cn_a14":       None,
                      "cn_a15":       None,
                      "cn_a16":       None,
                      "cn_a17":       None,
                      "cn_a18":       None,
                      "cn_a19":       None,
                      "cn_a20":       None,
                      "cn_a21":       None,
                      "cn_a22":       None,
                      "cn_a23":       None,
                      "cn_a24":       None,
                      "cn_a25":       None,
                      "cn_a26":       None,
                      "cn_a27":       None,
                      "cn_a28":       None,
                      "cn_a29":       None,
                      "cn_a30":       None,
                      "cn_a31":       None,
                      "cn_a32":       None,
                      "cn_a33":       None,
                      "cn_a34":       None,
                      "cn_a35":       None,
                      "cn_a36":       None,
                      "cn_a37":       None,
                      "cn_a38":       None,
                      "cn_a39":       None,
                      "cn_a40":       None,
                      "cn_a41":       None,
                      "cn_a42":       None,
                      "cn_a43":       None,
                      "cn_a44":       None,
                      "cn_a45":       None,
                      "cn_a46":       None,
                      "cn_a47":       None,
                      "cn_a48":       None,
                      "cn_a49":       None,
                      "cn_a50":       None,
                      "cn_a51":       None,
                      "cn_a52":       None,
                      "cn_a53":       None,
                      "cn_a54":       None,
                      "cn_b3":       None,
                      "cn_b4":       None,
                      "cn_b5":       None,
                      "cn_b6":       None,
                      "cn_b7":       None,
                      "cn_b8":       None,
                      "cn_b9":       None,
                      "cn_b10":       None,
                      "cn_b11":       None,
                      "cn_b12":       None,
                      "cn_b13":       None,
                      "cn_b14":       None,
                      "cn_b15":       None,
                      "cn_b16":       None,
                      "cn_b17":       None,
                      "cn_b18":       None,
                      "cn_b19":       None,
                      "cn_b20":       None,
                      "cn_b21":       None,
                      "cn_b22":       None,
                      "cn_b23":       None,
                      "cn_b24":       None,
                      "cn_b25":       None,
                      "cn_b26":       None,
                      "cn_b27":       None,
                      "cn_b28":       None,
                      "cn_b29":       None,
                      "cn_b30":       None,
                      "cn_b31":       None,
                      "cn_b32":       None,
                      "cn_b33":       None,
                      "cn_b34":       None,
                      "cn_b35":       None,
                      "cn_b36":       None,
                      "cn_b37":       None,
                      "cn_b38":       None,
                      "cn_b39":       None,
                      "cn_b40":       None,
                      "cn_b41":       None,
                      "cn_b42":       None,
                      "cn_b43":       None,
                      "cn_b44":       None,
                      "cn_b45":       None,
                      "cn_b46":       None,
                      "cn_b47":       None,
                      "cn_b48":       None,
                      "cn_b49":       None,
                      "cn_b50":       None,
                      "cn_b51":       None,
                      "cn_b52":       None,
                      "cn_b53":       None,
                      "cn_b54":       None,
                      "cn_c3":       None,
                      "cn_c4":       None,
                      "cn_c5":       None,
                      "cn_c6":       None,
                      "cn_c7":       None,
                      "cn_c8":       None,
                      "cn_c9":       None,
                      "cn_c10":       None,
                      "cn_c11":       None,
                      "cn_c12":       None,
                      "cn_c13":       None,
                      "cn_c14":       None,
                      "cn_c15":       None,
                      "cn_c16":       None,
                      "cn_c17":       None,
                      "cn_c18":       None,
                      "cn_c19":       None,
                      "cn_c20":       None,
                      "cn_c21":       None,
                      "cn_c22":       None,
                      "cn_c23":       None,
                      "cn_c24":       None,
                      "cn_c25":       None,
                      "cn_c26":       None,
                      "cn_c27":       None,
                      "cn_c28":       None,
                      "cn_c29":       None,
                      "cn_c30":       None,
                      "cn_c31":       None,
                      "cn_c32":       None,
                      "cn_c33":       None,
                      "cn_c34":       None,
                      "cn_c35":       None,
                      "cn_c36":       None,
                      "cn_c37":       None,
                      "cn_c38":       None,
                      "cn_c39":       None,
                      "cn_c40":       None,
                      "cn_c41":       None,
                      "cn_c42":       None,
                      "cn_c43":       None,
                      "cn_c44":       None,
                      "cn_c45":       None,
                      "cn_c46":       None,
                      "cn_c47":       None,
                      "cn_c48":       None,
                      "cn_c49":       None,
                      "cn_c50":       None,
                      "cn_c51":       None,
                      "cn_c52":       None,
                      "cn_c53":       None,
                      "cn_c54":       None,
                      "cn_d3":       None,
                      "cn_d4":       None,
                      "cn_d5":       None,
                      "cn_d6":       None,
                      "cn_d7":       None,
                      "cn_d8":       None,
                      "cn_d9":       None,
                      "cn_d10":       None,
                      "cn_d11":       None,
                      "cn_d12":       None,
                      "cn_d13":       None,
                      "cn_d14":       None,
                      "cn_d15":       None,
                      "cn_d16":       None,
                      "cn_d17":       None,
                      "cn_d18":       None,
                      "cn_d19":       None,
                      "cn_d20":       None,
                      "cn_d21":       None,
                      "cn_d22":       None,
                      "cn_d23":       None,
                      "cn_d24":       None,
                      "cn_d25":       None,
                      "cn_d26":       None,
                      "cn_d27":       None,
                      "cn_d28":       None,
                      "cn_d29":       None,
                      "cn_d30":       None,
                      "cn_d31":       None,
                      "cn_d32":       None,
                      "cn_d33":       None,
                      "cn_d34":       None,
                      "cn_d35":       None,
                      "cn_d36":       None,
                      "cn_d37":       None,
                      "cn_d38":       None,
                      "cn_d39":       None,
                      "cn_d40":       None,
                      "cn_d41":       None,
                      "cn_d42":       None,
                      "cn_d43":       None,
                      "cn_d44":       None,
                      "cn_d45":       None,
                      "cn_d46":       None,
                      "cn_d47":       None,
                      "cn_d48":       None,
                      "cn_d49":       None,
                      "cn_d50":       None,
                      "cn_d51":       None,
                      "cn_d52":       None,
                      "cn_d53":       None,
                      "cn_d54":       None}
        InputFileManipulator.__init__(self, filename, parList, core_nr)
    cnINDIVParList = ["cn_a3","cn_a4","cn_a5","cn_a6","cn_a7","cn_a8","cn_a9","cn_a10","cn_a11",
                      "cn_a12","cn_a13","cn_a14","cn_a15","cn_a16","cn_a17","cn_a18","cn_a19",
                      "cn_a20","cn_a21","cn_a22","cn_a23","cn_a24","cn_a25","cn_a26","cn_a27",
                      "cn_a28","cn_a29","cn_a30","cn_a31","cn_a32","cn_a33","cn_a34","cn_a35",
                      "cn_a36","cn_a37","cn_a38","cn_a39","cn_a40","cn_a41","cn_a42","cn_a43",
                      "cn_a44","cn_a45","cn_a46","cn_a47","cn_a48","cn_a49","cn_a50","cn_a51",
                      "cn_a52","cn_a53","cn_a54","cn_b3","cn_b4","cn_b5","cn_b6","cn_b7","cn_b8",
                      "cn_b9","cn_b10","cn_b11","cn_b12","cn_b13","cn_b14","cn_b15","cn_b16",
                      "cn_b17","cn_b18","cn_b19","cn_b20","cn_b21","cn_b22","cn_b23","cn_b24",
                      "cn_b25","cn_b26","cn_b27","cn_b28","cn_b29","cn_b30","cn_b31","cn_b32",
                      "cn_b33","cn_b34","cn_b35","cn_b36","cn_b37","cn_b38","cn_b39","cn_b40",
                      "cn_b41","cn_b42","cn_b43","cn_b44","cn_b45","cn_b46","cn_b47","cn_b48",
                      "cn_b49","cn_b50","cn_b51","cn_b52","cn_b53","cn_b54","cn_c3","cn_c4",
                      "cn_c5","cn_c6","cn_c7","cn_c8","cn_c9","cn_c10","cn_c11","cn_c12",
                      "cn_c13","cn_c14","cn_c15","cn_c16","cn_c17","cn_c18","cn_c19","cn_c20",
                      "cn_c21","cn_c22","cn_c23","cn_c24","cn_c25","cn_c26","cn_c27","cn_c28",
                      "cn_c29","cn_c30","cn_c31","cn_c32","cn_c33","cn_c34","cn_c35","cn_c36",
                      "cn_c37","cn_c38","cn_c39","cn_c40","cn_c41","cn_c42","cn_c43","cn_c44",
                      "cn_c45","cn_c46","cn_c47","cn_c48","cn_c49","cn_c50","cn_c51","cn_c52",
                      "cn_c53","cn_c54","cn_d3","cn_d4","cn_d5","cn_d6","cn_d7","cn_d8","cn_d9",
                      "cn_d10","cn_d11","cn_d12","cn_d13","cn_d14","cn_d15","cn_d16","cn_d17",
                      "cn_d18","cn_d19","cn_d20","cn_d21","cn_d22","cn_d23","cn_d24","cn_d25",
                      "cn_d26","cn_d27","cn_d28","cn_d29","cn_d30","cn_d31","cn_d32","cn_d33",
                      "cn_d34","cn_d35","cn_d36","cn_d37","cn_d38","cn_d39","cn_d40","cn_d41",
                      "cn_d42","cn_d43","cn_d44","cn_d45","cn_d46","cn_d47","cn_d48","cn_d49",
                      "cn_d50","cn_d51","cn_d52","cn_d53","cn_d54"]
    
    def initParValue(self, parList):
        for namePar in parList:
            row, col1, col2, dig = self.parInfo[namePar]
            self.parValue[namePar] = [float(self.textOld[row-1][col1:col2])]
            
    def changePar(self, namePar, changePar, changeHow, offsetRow=0, offsetCol=0, index=0):
        # change initial parameter depending on chosen method
        changePar = float(changePar)
        #print(index)
        #print(changePar)
        #print(self.parValue[namePar])
        if changeHow == "+":
            changedPar1 = self.parValue[namePar][index] + changePar
        elif changeHow == "*":
            changedPar1 = self.parValue[namePar][index] + self.parValue[namePar][index] * changePar
        elif changeHow == "s":
            changedPar1 = changePar
        if changedPar1 < 98 and changedPar1 > 25:
            changedPar = changedPar1
        elif changedPar1 >= 98:
            changedPar = 98
        elif changedPar1 <= 25:
            changedPar = 25
        # insert changed Parameter in textNew
        row, col1, col2, dig = self.parInfo[namePar]
        row += offsetRow
        col1 += offsetCol
        col2 += offsetCol
        format = "%" + str(col2-col1+1) + "." + str(dig) + "f"
        self.textNew[row-1] = (self.textNew[row-1][:col1-1] +
                            (format%changedPar).rjust(col2-col1+1) +
                            self.textNew[row-1][col2:])


class ovnManipulator(InputFileManipulator):
    parInfo = {"name":         (3,  1, 22,0,0,0),
               "ovn_mean":     (3, 23, 30,5,0.001,0.6),
               "ovn_min":      (3, 31, 44,5,0.001,0.6),
               "ovn_max":      (3, 45, 58,5,0.001,0.6)}
    def __init__(self, filename, parList, core_nr):
        self.parValue = {"name": None,
               "ovn_mean":    None,
               "ovn_min":     None,
               "ovn_max":     None}
        InputFileManipulator.__init__(self, filename, parList, core_nr)
    ovnParList = ["ovn_mean","ovn_min","ovn_max"]
   
    # overrides initParValue: multiple HRUs have to be considered.    
    def initParValue(self, parList):
        for namePar in parList:
            row, col1, col2, dig, minValue, maxValue = self.parInfo[namePar]
            llist = []
            for i in range(self.file_len-3):
                llist.append(float(self.textOld[row-1][col1:col2]))
                row += 1
            self.parValue[namePar] = llist

    # overrides setChangePar: multiple HRUs have to be considered.
    def setChangePar(self, namePar, changePar, changeHow):
        n_par = len(self.parValue[namePar])
        #print(n_par)
        for index in range(n_par):
            offsetRow = index
            self.changePar(namePar, changePar, changeHow, offsetRow, 0, index)
            
class solManipulator(InputFileManipulator):
    parInfo = {"nly":         (3, 33, 35,0,0,0),
               "dp":          (4,127,136,5,0,3500),
               "bd":          (4,137,150,5,0.9,3),
               "awc":         (4,151,164,5,0.01,1),
               "soil_k":       (4,165,178,5,0.001,2000),
               "carbon":      (4,179,192,5,0.1,10),
               "clay":        (4,193,206,5,0,100),
               "silt":        (4,207,220,5,0,100),
               "sand":        (4,221,234,5,0,100),
               "rock":        (4,235,248,5,0,100),
               "alb":         (4,249,262,5,0,0.25),
               "usle_k":      (4,263,276,5,0,0.65),
               "ec":          (4,277,290,5,0,100),
               "caco3":       (4,291,304,5,0,65),
               "ph":          (4,304,318,5,3,10)}
    def __init__(self, filename, parList, core_nr):
        self.parValue = {"nly":  None,
                      "dp":   None,
               "bd":          None,
               "awc":         None,
               "soil_k":      None,
               "carbon":      None,
               "clay":        None,
               "silt":        None,
               "sand":        None,
               "rock":        None,
               "alb":         None,
               "usle_k":      None,
               "ec":          None,
               "caco3":       None,
               "ph":          None}
        InputFileManipulator.__init__(self, filename, parList, core_nr)
    solParList = ["dp","bd","awc","soil_k","carbon","clay","silt","sand","rock","alb",
                  "usle_k","ec","caco3","ph"]
              
    # overrides initParValue: multiple HRUs have to be considered.    
    def initParValue(self, parList):
        for namePar in parList:
            row, col1, col2, dig, minValue, maxValue = self.parInfo[namePar]
            row_l, col1_l, col2_l, dig_l, minValue_l, maxValue_l = self.parInfo["nly"]
            layer = []
            layer.append(row)
            #print(self.file_len)
            for l in range(self.file_len-row_l):
                try:
                    layer.append(int(self.textOld[row_l+l-1][col1_l:col2_l])+1)
                except:
                    pass
            #print(layer)
            self.empty_row = []
            for i in range(len(layer)-2):
                #self.empty_row.append(sum(layer[:i+1])-1)
                self.empty_row.append(sum(layer[:i+1])+layer[i+1]-2)
            #print(self.empty_row)
            llist = []          
            lines = [i for i in range(self.file_len) if i not in self.empty_row]
            #print(lines)
            for i in lines[row_l:]:
                llist.append(float(self.textOld[i][col1:col2]))
            #print(llist)
            self.parValue[namePar] = llist

    # overrides setChangePar: multiple HRUs have to be considered.
    def setChangePar(self, namePar, changePar, changeHow):
        e_row = [i-3 for i in self.empty_row]
        Lines = [i for i in range(self.file_len) if i not in e_row]
        #print(Lines)
        index = 0
        for i in Lines[:len(Lines)-3]:
            offsetRow = i
            self.changePar(namePar, changePar, changeHow, offsetRow, 0, index)                      
            index += 1

"""

"""
class parManipulator(object):
    def __init__(self,pathdir,core_nr):
        self.core_nr=core_nr
        self.pathdir=pathdir             
        #self.files=os.listdir(self,pathdir)

#here all parameters from the bsn-file are assigned in the dictionary for calibration        
    def bsn(pathdir,core_nr):       
        #all parameters from the bsn-file are assigned in the dictionary for calibration
        bsnfiles = ["parameters.bsn"]
        bsn = []
        for i in bsnfiles:
            bsn.append(bsnManipulator(i, bsnManipulator.bsnParList , core_nr))
        return bsn

    def sno(pathdir,core_nr):       
        #all parameters from the sno-file are assigned in the dictionary for calibration
        snofiles = ["snow.sno"]
        sno = []
        for i in snofiles:
            sno.append(snoManipulator(i, snoManipulator.snoParList , core_nr))
        return sno

    def cha(pathdir,core_nr):       
        #all parameters from the cha-file are assigned in the dictionary for calibration
        chafiles = ["hyd-sed-lte.cha"]
        cha = []
        for i in chafiles:
            cha.append(chaManipulator(i, chaManipulator.chaParList , core_nr))
        return cha

    def sol(pathdir,core_nr):       
        #all parameters from the sol-file are assigned in the dictionary for calibration
        solfiles = ["soils.sol"]
        sol = []
        for i in solfiles:
            sol.append(solManipulator(i, solManipulator.solParList , core_nr))
        return sol

    def aqu(pathdir,core_nr):       
        #all parameters from the aqu-file are assigned in the dictionary for calibration
        aqufiles = ["aquifer.aqu"]
        aqu = []
        for i in aqufiles:
            aqu.append(aquManipulator(i, aquManipulator.aquParList , core_nr))
        return aqu

    def hyd(pathdir,core_nr):       
        #all parameters from the hyd-file are assigned in the dictionary for calibration
        hydfiles = ["hydrology.hyd"]
        hyd = []
        for i in hydfiles:
            hyd.append(hydManipulator(i, hydManipulator.hydParList , core_nr))
        return hyd

    def cn(pathdir,core_nr):       
        #all parameters from the cn-file are assigned in the dictionary for calibration
        cnfiles = ["cntable.lum"]
        cn = []
        for i in cnfiles:
            cn.append(cnManipulator(i, cnManipulator.cnParList , core_nr))
        return cn

    def cnINDIV(pathdir,core_nr):       
        #all parameters from the cnINDIV-file are assigned in the dictionary for calibration
        cnINDIVfiles = ["cntable.lum"]
        cnINDIV = []
        for i in cnINDIVfiles:
            cnINDIV.append(cnINDIVManipulator(i, cnINDIVManipulator.cnINDIVParList , core_nr))
        return cnINDIV

    def ovn(pathdir,core_nr):       
        #all parameters from the ovn-file are assigned in the dictionary for calibration
        ovnfiles = ["ovn_table.lum"]
        ovn = []
        for i in ovnfiles:
            ovn.append(ovnManipulator(i, ovnManipulator.ovnParList , core_nr))
        return ovn

    def top(pathdir,core_nr):       
        #all parameters from the top-file are assigned in the dictionary for calibration
        topfiles = ["topography.hyd"]
        top = []
        for i in topfiles:
            top.append(topManipulator(i, topManipulator.topParList , core_nr))
        return top

#         #calfiles = ["calibration.cal"]
#         #cal = []
#         #for i in calfiles:
#         #     cal.append(calManipulator(i, ["snomelt_tmp","snofall_tmp","surlag"]))
#         #manipulators["cal"] = cal
