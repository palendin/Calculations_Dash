import numpy as np
import json
import os
import pandas as pd
from calc_function import *
#print(os. getcwd()) #get current working directory
path = os.path.dirname(__file__) #path of this python file
os.chdir(path) #change to the directory of this folder since the working dir was different

#gathering json data
with open('molecular_weight.json') as json_file:
    mw = json.load(json_file)
with open('stoichiometry.json') as json_file:
    sto = json.load(json_file)
with open('nitrogen_sources.json') as json_file:
    ns = json.load(json_file)

#create dictionary from molecular_weight json
element_key = []
element_value = []
for e in mw['molecular weight']:
    element_key.append(e['name']) 
    element_value.append(e['molecular weight g/mol'])
molar_weight = dict(zip(element_key, element_value))

#create dictonary from stoich json
stoich_name_key = [] #name of the compound i.e NH4
stoich_element_keys = list(sto['stoichiometry'][0].keys()) #element names
stoich_element_keys.remove('name') #remove string "name" 
stoich_element_values = [] #values of the element

for s in sto['stoichiometry']:
    stoich_name_key.append(s['name'])
    for e in stoich_element_keys:
        stoich_element_values.append(s[e])

stoich = {}
k = 0
for i in range(len(stoich_name_key)):
    stoich[stoich_name_key[i]] = {}
    for j in stoich_element_keys: #loop through elements for each compound
        stoich[stoich_name_key[i]][j] = stoich_element_values[k] #name, element name, element value
        k += 1

#create dictionary from nitrogen source json
ns_name_key = [] #name of the compound
ns_conc_key = list(ns['nitrogen_sources'][0].keys())
ns_conc_key.remove('name') #remove string "name" 
ns_conc_values = [] #concentration values

for n in ns['nitrogen_sources']:
    ns_name_key.append(n['name'])
    for c in ns_conc_key:
        ns_conc_values.append(n[c])

n_source = {}
k = 0
for i in range(len(ns_name_key)):
    n_source[ns_name_key[i]] = {}
    for j in ns_conc_key: #loop through elements for each compound
        n_source[ns_name_key[i]][j] = ns_conc_values[k] #name, element name, element value
        k += 1

#---------------------------------------------------------------------------------------
run_data = pd.read_csv('Run_Data.csv')
df = pd.DataFrame(run_data)
df_run_data = df.fillna(0) #replace NaN with 0
#print(df_run_data)

header = list(df_run_data.columns.values)                                                                                                                                             
#run_names = df_run_data['Hermes'] #key in dict
unique_run_names = df_run_data.Hermes.unique() #np array of unique hermes name

#build dictionary of the raw data
dict = {}
i = 0
j = 0
for urn in unique_run_names:
    single_run = df_run_data.loc[df_run_data['Hermes'] == unique_run_names[i]] #dataframe for single run
    A = single_run['PSA mL'] #might be able to work with this-----------------
    #print(A.iloc[0])
    #cumsum()
    B = df_PSA_cum_calc(A)
    
    #print(form_array(header,single_run))
    #dict[urn] = form_array(header,single_run)
    dict[urn] = {}
    for h in header:
        #print(j)
        if j < len(header): #len counts from 1.
            dict[urn][h] = form_array(header,single_run)[j]
            j += 1
    i += 1
    j = 0
#print(dict['H11433-21']['Ammonium g/kg'])

#perform calculations with dictionary 
broth_density = 1.02 # g/ml
NH4OH_density = 0.91 #g/ml
diluted_NH4OH_density = 0.98
base_weight = df_run_data['Base Weight'].values #g
base_weight_sum = sum(base_weight,0) #for logic check whether to use weight or totalizer

for urn in unique_run_names:
    #convert into np array, so each array variable is made of individual arrays of data so its easier to work with
    Weight_drawed = np.array(dict[urn]['Tank Weight Pre kg']) - np.array(dict[urn]['Tank Weight Post kg']) 
    #Weight_drawed1 = df[urn]['Tank Weight Pre kg'] - df[urn]['Tank Weight Post kg'] doesnt work
    
    Cum_weight_drawed = np.array(cum_calc(Weight_drawed))
    
    Biomass_drawed = np.array(dict[urn]['Biomass g/L'])*Weight_drawed/broth_density
    Cum_biomass_drawed = np.array(cum_calc(Biomass_drawed))

    Riboflavin_drawed = np.array(dict[urn]['Riboflavin g/kg'])*Weight_drawed
    Cum_riboflavin_drawed = np.array(cum_calc(Riboflavin_drawed))

    NH4_drawed = np.array(dict[urn]['Ammonium g/kg'])*Weight_drawed
    Cum_NH4_drawed = np.array(cum_calc(NH4_drawed))
    
    Biomass = np.array(dict[urn]['Biomass g/L'])
    Riboflavin = np.array(dict[urn]['Riboflavin g/kg'])
    NH4 = np.array(dict[urn]['Ammonium g/kg'])
    Tankweight_pre = np.array(dict[urn]['Tank Weight Pre kg'])
    Tankweight_post = np.array(dict[urn]['Tank Weight Post kg'])
    Base_totalizer = np.array(dict[urn]['Base totalizer mL'])
    Base_weight = np.array(dict[urn]['Base Weight'])
    PSA = np.array(dict[urn]['PSA mL'])

    #N-balance (initial)
    biomass_N_init = Biomass[0]*Tankweight_pre[0]/broth_density/molar_weight['Yeast']*stoich['Yeast']['N'] #init biomass for each run
    MAP_N_init = Tankweight_pre[0]/broth_density*n_source['Monoammonium Phosphate in Media']['conc g/L']/molar_weight['Monoammonium Phosphate (MAP)']*stoich['Monoammonium Phosphate (MAP)']['N']
 
    #N-balance (cumulative N in) 
    if base_weight_sum == 0: #decide to use base weight or base totalizer
        Cum_base_N_in = Base_totalizer/1000*n_source['Diluted Ammonium Hydroxide']['conc M'] #mol
    else:
        Cum_base_weight = Base_weight[0] - Base_weight
        Cum_base_N_in = Cum_base_weight/NH4OH_density/1000*n_source['Ammonium Hydroxide']['conc M'] #mols
   
    Cum_PSA_N_in = np.array(PSA_cum_calc(PSA))/1000*n_source['Monoammonium Phosphate in PSA']['conc g/L']/molar_weight['Monoammonium Phosphate (MAP)']*stoich['Monoammonium Phosphate (MAP)']['N']

    #N-balance (cumulative out) 
    Cum_biomass_N_out = Cum_biomass_drawed/molar_weight['Yeast']*stoich['Yeast']['N'] #mols
    Cum_riboflavin_N_out = Cum_riboflavin_drawed/molar_weight['Riboflavin']*stoich['Riboflavin']['N']
    Cum_broth_N_out = Cum_NH4_drawed/molar_weight['Ammonium']*stoich['Ammonium']['N']
    
    #N-balance (Accumulation)
    Biomass_N = Biomass*Tankweight_post/broth_density/molar_weight['Yeast']*stoich['Yeast']['N'] #mols
    Riboflavin_N = Riboflavin*Tankweight_post/molar_weight['Riboflavin']*stoich['Riboflavin']['N']
    Broth_N = NH4*Tankweight_post/molar_weight['Ammonium']*stoich['Ammonium']['N']
    
    #N-balance Total In
    N_in = biomass_N_init + MAP_N_init + Cum_base_N_in + Cum_PSA_N_in 
    N_out = Cum_biomass_N_out + Cum_riboflavin_N_out + Cum_broth_N_out
    N_acc = Biomass_N + Riboflavin_N + Broth_N

    #Closure
    Closure = (N_out + N_acc)/N_in*100
    Hermes = np.array([urn]*len(Closure))

'''
header = []
dataframe = []
with open('countries.csv', 'w', encoding='UTF8') as f:
    writer = csv.writer(f)

    # write the header
    writer.writerow(header)
    # write the data
    writer.writerow(dataframe)
'''

#A = locals().keys()
#B = list(A)
#print(B[0])

#print(Biomass_drawed[1][0])  #access elements (array, index)

'''
#N-balance (cumulative in)
base_weight = df_run_data['Base Weight'].values
base_weight_sum = sum(base_weight,0)

if base_weight_sum == 0:
    Cum_NH4_in = cum_calc(unique_run_names, Base_totalizer)
#print(Base_totalizer)
#print(Cum_NH4_in)
'''

'''
A = np.array(Draw_weight[0]) #convert into array

#A = Biomass_drawed[0]*Draw_weight[0]
#print(A[5])

for i in A: #unpack list within list to make it work with dictionary
    for j in i:
        ns_conc_key.append(j)


def cum_calc(name,data_array):
    array = []
    for n in range(len(name)): #loop through individual runs
        v = data_array[n][0] #initial value for the run
        array_length = range(len(data_array[n]))
        for l in array_length:
            if l <  len(array_length) - 1: 
                v = v + data_array[n][l+1] #exclude initial value in the array. need to reduce loop by 1
                array.append(v)
    return array

A = np.array([1,2]) 
B = np.array([1,2,3,4])
C = B[:, np.newaxis] + A #broadcasting so A+B works
print(C) 

#Hermes,Time,Sample Type,Tank Weight Pre kg,Tank Weight Post kg
#Biomass g/L,Cum Biomass g,Riboflavin g/kg,Cum Riboflavin g
#Ammonium g/kg,PSA mL,Base Weight,Base totalizer mL
'''


