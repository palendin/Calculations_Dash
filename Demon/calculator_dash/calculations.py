import pandas as pd
import numpy as np
import json
from jsonfile_to_dict import json_to_dict

def KPI(df):
    
    molar_weight = json_to_dict('molecular_weight.json')
    stoich = json_to_dict('stoichiometry.json') 
    n_source = json_to_dict('nitrogen_sources.json')
    # KPI calc
    pass
    return

def mass_balance(RCS_df):
    
    molar_weight = json_to_dict('molecular_weight.json')
    stoich = json_to_dict('stoichiometry.json') 
    n_source = json_to_dict('nitrogen_sources.json')
    
    # Acc = (in - out) + (generated - consumed)

    # Additions
    cum_feed = RCS_df.groupby('hermes_run', squeeze = True).apply(lambda x: x['Adjusted Feed Vessel Weight'].iat[0] - x['Adjusted Feed Vessel Weight'])
    RCS_df['cum_feed'] = cum_feed.reset_index(level = 0, drop=True) # g

    Cum_PSA_in = RCS_df.groupby('hermes_run', squeeze = True).apply(lambda  x: x['PSA'].cumsum()) # ml
    RCS_df['Cum_PSA_in'] = Cum_PSA_in.reset_index(level = 0, drop = True) 

    Cum_base_in = RCS_df.groupby('hermes_run', squeeze = True).apply(lambda x: x['Base totalizer'] if x['Tank Weight pre sample'].mean() < 0.5 else x['Base Weight g'].iat[0] - x['Base Weight g']) #mol
    RCS_df['Cum_base_in'] = Cum_base_in.reset_index(level = 0, drop = True)

    O2_consumed = RCS_df.groupby('hermes_run', squeeze = True).apply(lambda x: x['O2 Consumed']*molar_weight['O2']['molecular weight g/mol']) #g
    RCS_df['O2_consumed'] = O2_consumed.reset_index(level = 0, drop=True)

    # assumes there is no bottle switch
    Overlay_in = RCS_df.groupby('hermes_run', squeeze = True).apply(lambda x: x['SclSubsB_PV'].iat[0] - x['SclSubsB_PV'])
    RCS_df['Overlay_in'] = Overlay_in.reset_index(level = 0, drop=True)

    # Out
    Weight_draw = RCS_df.groupby('hermes_run', squeeze = True).apply(lambda x: x['Tank Weight pre sample']-x['Tank Weight post sample']) # kg
    RCS_df['Weight_draw'] = Weight_draw.reset_index(level = 0, drop=True) # kg
    Cum_weight_draw = RCS_df.groupby('hermes_run', squeeze = True).apply(lambda  x: x['Weight_draw'].cumsum()) # kg
    RCS_df['Cum_weight_draw'] = Cum_weight_draw.reset_index(level = 0, drop=True)

    Cum_over_flow = RCS_df.groupby('hermes_run', squeeze = True).apply(lambda x: x['Overflow Weight'].cumsum()) # g
    RCS_df['Cum_over_flow'] = Cum_over_flow.reset_index(level = 0, drop=True)

    Cum_tank_weight = RCS_df.groupby('hermes_run', squeeze = True).apply(lambda x: x['Cum_weight_draw']*1000 + x['Cum_over_flow'] + x['Tank Weight post sample'].iat[0]*1000)
    RCS_df['Cum_tank_weight'] = Cum_tank_weight.reset_index(level = 0, drop=True)

    Tank_weight_accumulated = RCS_df.groupby('hermes_run', squeeze = True).apply(lambda x: x['Cum_tank_weight'] - x['Cum_tank_weight'].iat[0])
    RCS_df['Tank_weight_accumulated'] = Tank_weight_accumulated.reset_index(level = 0, drop=True)

    H2O_evap = RCS_df.groupby('hermes_run', squeeze = True).apply(lambda x: x['H2O Evaporated']*molar_weight['H2O']['molecular weight g/mol']) # g
    RCS_df['H2O_evap'] = H2O_evap.reset_index(level = 0, drop=True)

    CO2_out = RCS_df.groupby('hermes_run', squeeze = True).apply(lambda x: x['CO2 Evolved']*molar_weight['CO2']['molecular weight g/mol']) # g
    RCS_df['CO2_out'] = CO2_out.reset_index(level = 0, drop=True)

    # Mass closure
    Total_in = RCS_df['cum_feed'] + RCS_df['Cum_PSA_in'] + RCS_df['Cum_base_in'] + RCS_df['O2_consumed'] + RCS_df['Overlay_in']
    Total_out = RCS_df['Tank_weight_accumulated'] + RCS_df['H2O_evap'] + RCS_df['CO2_out']
    Mass_closure = Total_out/Total_in
    RCS_df['Mass_closure'] = Mass_closure.reset_index(level = 0, drop=True)
    
    return RCS_df

def carbon_balance(RCS_df):
    
    molar_weight = json_to_dict('molecular_weight.json')
    stoich = json_to_dict('stoichiometry.json') 
    n_source = json_to_dict('nitrogen_sources.json')
    
    # calculate TRS carbon
    #squeeze works with groupby when you only have a single hermes_run. Without it, you have an erorr
    cum_feed = RCS_df.groupby('hermes_run', squeeze = True).apply(lambda x: x['Adjusted Feed Vessel Weight'].iat[0] - x['Adjusted Feed Vessel Weight'])
    #print(feed_weight)
    # print(feed_weight.columns)
    # #feed_difference = feed_weight.shift(1)
    #cum_feed = cum_feed.fillna(0)
    #print(feed_weight)
    # print(feed_weight.reset_index(level = 0, drop=True))
    RCS_df['cum_feed'] = cum_feed.reset_index(level = 0, drop=True) # g
    #RCS_df['feed_difference'] = feed_weight[['Adjusted Feed Vessel Weight']]

    #cum_feed = RCS_df.groupby('hermes_run', squeeze = True).apply(lambda  x: x['feed_difference'].cumsum())
    #RCS_df['cum_feed'] = cum_feed.reset_index(level = 0, drop=True)

    cum_TRS = RCS_df.groupby('hermes_run', squeeze = True).apply(lambda  x: x['cum_feed']*(x['Feed Trs']/100))
    RCS_df['cum_TRS'] = cum_TRS.reset_index(level = 0, drop=True)

    TRS_carbon = RCS_df.groupby('hermes_run', squeeze = True).apply(lambda  x: x['cum_TRS']*0.4) # g, 0.4 is the weight ratio of C/glucose
    RCS_df['TRS_carbon'] = TRS_carbon.reset_index(level = 0, drop=True)

    # Calculate CO2 carbon
    Cum_CO2_carbon = RCS_df.groupby('hermes_run', squeeze = True).apply(lambda  x: x['CO2 Evolved']*44*0.2727)
    RCS_df['Cum_CO2_carbon'] = Cum_CO2_carbon.reset_index(level = 0, drop=True) # g

    # Calculate biomass carbon
    cell_weight = 21.3E-12 #g/cell
    Weight_draw = RCS_df.groupby('hermes_run', squeeze = True).apply(lambda x: x['Tank Weight pre sample']-x['Tank Weight post sample']) # kg
    RCS_df['Weight_draw'] = Weight_draw.reset_index(level = 0, drop=True) # kg

    Biomass_density = RCS_df.groupby('hermes_run', squeeze = True).apply(lambda  x: x['Total_Cell_Density']*1E6*cell_weight*1000) # g/L
    RCS_df['Biomass_density'] = Biomass_density.reset_index(level = 0, drop=True)

    Avg_biomass_density = RCS_df.groupby('hermes_run', squeeze = True).apply(lambda  x: x['Biomass_density'].expanding().mean()) # g/L
    RCS_df['Avg_biomass_density'] = Avg_biomass_density.reset_index(level = 0, drop=True)

    Tank_biomass = RCS_df.groupby('hermes_run', squeeze = True).apply(lambda  x: x['Biomass_density']*x['Tank Weight post sample']/x['Broth Density']) # g
    RCS_df['Tank_biomass'] = Tank_biomass.reset_index(level = 0, drop=True)

    Biomass_draw = RCS_df.groupby('hermes_run', squeeze = True).apply(lambda  x: x['Weight_draw']*x['Biomass_density']/x['Broth Density']) # g
    RCS_df['Biomass_draw'] = Biomass_draw.reset_index(level = 0, drop=True)

    Cum_biomass_draw = RCS_df.groupby('hermes_run', squeeze = True).apply(lambda x: x['Biomass_draw'].cumsum()) # g
    RCS_df['Cum_biomass_draw'] = Cum_biomass_draw.reset_index(level = 0, drop=True)

    Cum_biomass = RCS_df.groupby('hermes_run', squeeze = True).apply(lambda x: x['Tank_biomass'] + x['Cum_biomass_draw']) # g
    RCS_df['Cum_biomass'] = Cum_biomass.reset_index(level = 0, drop=True)

    Cum_biomass_carbon = RCS_df.groupby('hermes_run', squeeze = True).apply(lambda x: x['Cum_biomass']*0.44859) # g, 0.44 is the g-C/g-biomass ratio
    RCS_df['Cum_biomass_carbon'] = Cum_biomass_carbon.reset_index(level = 0, drop=True)

    # calculate myrcene carbon

    Myrcene_draw = RCS_df.groupby('hermes_run', squeeze = True).apply(lambda  x: x['Weight_draw']*x['Myrcene  broth g/kg']) # g
    RCS_df['Myrcene_draw'] = Myrcene_draw.reset_index(level = 0, drop=True)

    Cum_myrcene_draw = RCS_df.groupby('hermes_run', squeeze = True).apply(lambda  x: x['Myrcene_draw'].cumsum()) # g
    RCS_df['Cum_myrcene_draw'] = Cum_myrcene_draw.reset_index(level = 0, drop=True)

    # myrcene in tank
    Tank_myrcene = RCS_df.groupby('hermes_run', squeeze = True).apply(lambda x: x['Myrcene  broth g/kg']*x['Tank Weight post sample']) # g
    RCS_df['Tank_myrcene'] = Tank_myrcene.reset_index(level = 0, drop=True)

    # trap myrcene
    trap_overlay = 0.1638 # kg 
    Trap_myrcene = RCS_df.groupby('hermes_run', squeeze = True).apply(lambda x: x['Myrcene  overlay g/kg']*trap_overlay) # g
    RCS_df['Trap_myrcene'] = Trap_myrcene.reset_index(level = 0, drop=True)

    # effluent myrcene
    Effluent_myrcene = RCS_df.groupby('hermes_run', squeeze = True).apply(lambda x: x['Overflow Weight']/1000*x['Myrcene  effluent_broth g/kg'])
    RCS_df['Effluent_myrcene'] = Effluent_myrcene.reset_index(level = 0, drop=True)   

    Cum_effluent_myrcene = RCS_df.groupby('hermes_run', squeeze = True).apply(lambda x: x['Effluent_myrcene'].cumsum())
    RCS_df['Cum_effluent_myrcene'] = Cum_effluent_myrcene.reset_index(level = 0, drop=True)   

    Total_myrcene = RCS_df['Tank_myrcene'] + RCS_df['Cum_myrcene_draw'] + RCS_df['Trap_myrcene'] + RCS_df['Cum_effluent_myrcene'] # g
    RCS_df['Total_myrcene'] = Total_myrcene.reset_index(level = 0, drop=True)

    Total_myrcene_carbon = RCS_df.groupby('hermes_run', squeeze = True).apply(lambda x: x['Total_myrcene']*0.88) # 0.88 g-C/g-myrcene ratio 
    RCS_df['Total_myrcene_carbon'] = Total_myrcene_carbon.reset_index(level = 0, drop=True)

    # carbon balance
    CO2_percent = RCS_df.groupby('hermes_run', squeeze = True).apply(lambda x: (x['Cum_CO2_carbon']/x['TRS_carbon']*100))
    RCS_df['CO2_percent'] = CO2_percent.reset_index(level = 0, drop=True)

    Biomass_percent = RCS_df.groupby('hermes_run', squeeze = True).apply(lambda x: (x['Cum_biomass_carbon']/x['TRS_carbon']*100))
    RCS_df['Biomass_percent'] = Biomass_percent.reset_index(level = 0, drop=True)

    Myrcene_percent = RCS_df.groupby('hermes_run', squeeze = True).apply(lambda x: (x['Total_myrcene_carbon']/x['TRS_carbon']*100))
    RCS_df['Myrcene_percent'] = Myrcene_percent.reset_index(level = 0, drop=True)

    Carbon_closure =  RCS_df.groupby('hermes_run', squeeze = True).apply(lambda x: ((x['Cum_CO2_carbon']+x['Cum_biomass_carbon']+x['Total_myrcene_carbon'])/x['TRS_carbon'])*100)
    RCS_df['Carbon_closure'] = Carbon_closure.reset_index(level = 0, drop=True)

    # TRS/O2 
    TRS_O2 = RCS_df.groupby('hermes_run', squeeze = True).apply(lambda x: (x['cum_TRS']/180)/x['O2 Consumed'])
    RCS_df['TRS_O2'] = TRS_O2.reset_index(level = 0, drop=True)

    # Product/O2 ratio
    Myrcene_O2 = RCS_df.groupby('hermes_run', squeeze = True).apply(lambda x: (x['Total_myrcene']/136.23)/x['O2 Consumed'])
    RCS_df['Myrcene_O2'] = Myrcene_O2.reset_index(level = 0, drop=True)

    # TRS for biomass (x2.077), TRS for product(x6.3), TRS for maintenace = TRS other - TRS biomass - TRS product 
    TRS_biomass = RCS_df.groupby('hermes_run', squeeze = True).apply(lambda x: x['Cum_biomass']*2.077) # g
    RCS_df['TRS_biomass'] = TRS_biomass.reset_index(level = 0, drop=True)

    TRS_product = RCS_df.groupby('hermes_run', squeeze = True).apply(lambda x: x['Total_myrcene']*6.3) # g
    RCS_df['TRS_product'] = TRS_product.reset_index(level = 0, drop=True)

    TRS_other = RCS_df.groupby('hermes_run', squeeze = True).apply(lambda x: x['cum_TRS'] - x['TRS_product'] - x['TRS_biomass']) # g
    RCS_df['TRS_other'] = TRS_other.reset_index(level = 0, drop=True)  

    # maintenance 
    shift_post_weight = RCS_df.groupby('hermes_run', squeeze = True).apply(lambda x: x['Tank Weight post sample'].shift(1))
    RCS_df['shift_post_weight'] = shift_post_weight.reset_index(level = 0, drop=True)  

    Avg_interval_vol = RCS_df.groupby('hermes_run', squeeze = True).apply(lambda x: (x[['shift_post_weight', 'Tank Weight pre sample']].mean(axis=1))/1.02) # L
    RCS_df['Avg_interval_vol'] = Avg_interval_vol.reset_index(level = 0, drop=True)  

    Avg_vol = RCS_df.groupby('hermes_run', squeeze = True).apply(lambda x: x['Avg_interval_vol'].expanding().mean()) # using expanding  mean method
    RCS_df['Avg_vol'] = Avg_vol.reset_index(level = 0, drop=True)

    maintenance = RCS_df.groupby('hermes_run', squeeze = True).apply(lambda x: x['TRS_other']/(x['Avg_biomass_density']*x['Avg_vol'])/x['sample_time'])
    RCS_df['maintenance'] = maintenance.reset_index(level = 0, drop=True)

    return RCS_df

def nitrogen_balance(RCS_df):
    #(molar_weight, stoich, n_source) = importjson()
    molar_weight = json_to_dict('molecular_weight.json')
    stoich = json_to_dict('stoichiometry.json') 
    n_source = json_to_dict('nitrogen_sources.json')
    
    NH4OH_density = 0.91 #g/ml
    diluted_NH4OH_density = 0.98 # g/cell
    cell_weight = 21.3E-12 #g/cell
    RCS_df['PSA'] = RCS_df['PSA'].shift(1)
    RCS_df = RCS_df.fillna(0)
    
    # nitrogen balance calc
    Weight_draw = RCS_df.groupby('hermes_run').apply(lambda x: x['Tank Weight pre sample']-x['Tank Weight post sample']) # kg
    RCS_df['Weight_draw'] = Weight_draw.reset_index(level = 0, drop=True) # kg

    Cum_weight_draw = RCS_df.groupby('hermes_run').apply(lambda  x: x['Weight_draw'].cumsum()) # kg
    RCS_df['Cum_weight_draw'] = Cum_weight_draw.reset_index(level = 0, drop=True)

    Biomass_density = RCS_df.groupby('hermes_run').apply(lambda  x: x['Total_Cell_Density']*1E6*cell_weight*1000) # g/L
    RCS_df['Biomass_density'] = Biomass_density.reset_index(level = 0, drop=True)

    Tank_biomass = RCS_df.groupby('hermes_run').apply(lambda  x: x['Biomass_density']*x['Tank Weight post sample']/x['Broth Density']) # g
    RCS_df['Tank_biomass'] = Tank_biomass.reset_index(level = 0, drop=True)

    Biomass_draw = RCS_df.groupby('hermes_run').apply(lambda  x: x['Weight_draw']*x['Biomass_density']/x['Broth Density']) # g
    RCS_df['Biomass_draw'] = Biomass_draw.reset_index(level = 0, drop=True)

    Cum_biomass_draw = RCS_df.groupby('hermes_run').apply(lambda x: x['Biomass_draw'].cumsum()) # g
    RCS_df['Cum_biomass_draw'] = Cum_biomass_draw.reset_index(level = 0, drop=True)

    Cum_biomass = RCS_df.groupby('hermes_run').apply(lambda x: x['Tank_biomass'] + x['Cum_biomass_draw']) # g
    RCS_df['Cum_biomass'] = Cum_biomass.reset_index(level = 0, drop=True)

    Riboflavin_draw = RCS_df.groupby('hermes_run').apply(lambda  x: x['Weight_draw']*x['Riboflavin Titer in grams']) # g
    RCS_df['Riboflavin_draw'] = Riboflavin_draw.reset_index(level = 0, drop=True)

    Cum_riboflavin_draw = RCS_df.groupby('hermes_run').apply(lambda  x: x['Riboflavin_draw'].cumsum()) # g
    RCS_df['Cum_riboflavin_draw'] = Cum_riboflavin_draw.reset_index(level = 0, drop=True)

    Cum_PSA_in = RCS_df.groupby('hermes_run').apply(lambda  x: x['PSA'].cumsum()) # ml
    RCS_df['Cum_PSA_in'] = Cum_PSA_in.reset_index(level = 0, drop = True) 

    NH4_draw = RCS_df.groupby('hermes_run').apply(lambda x: x['Weight_draw']*x['Ammonium']) # g
    RCS_df['NH4_draw'] = NH4_draw.reset_index(level = 0, drop = True)

    Cum_NH4_draw = RCS_df.groupby('hermes_run').apply(lambda  x: x['NH4_draw'].cumsum()) # g
    RCS_df['Cum_NH4_draw'] = Cum_NH4_draw.reset_index(level = 0, drop = True)

    #N-balance (initial)
    biomass_N_init = RCS_df.groupby('hermes_run')['Cum_biomass'].nth(0)/molar_weight['Yeast']['molecular weight g/mol']*stoich['Yeast']['N'] #init biomass for each run by extract 1st value of Cum biomass column
    MAP_N_init = RCS_df.groupby('hermes_run')['Tank Weight pre sample'].nth(0)/RCS_df['Broth Density'][0]*n_source['Monoammonium Phosphate in Media']['conc g/L']/molar_weight['Monoammonium Phosphate (MAP)']['molecular weight g/mol']*stoich['Monoammonium Phosphate (MAP)']['N']

    #N-balance (cumulative N in)
    Cum_base_N_in = RCS_df.groupby('hermes_run').apply(lambda x: x['Base totalizer']/1000*n_source['Diluted Ammonium Hydroxide']['conc M'] if x['Tank Weight pre sample'].mean() < 0.5 else x['Base totalizer']/NH4OH_density/1000*n_source['Ammonium Hydroxide']['conc M']) #mol
    RCS_df['Cum_base_N_in'] = Cum_base_N_in.reset_index(level = 0, drop = True)

    Cum_PSA_N_in = RCS_df.groupby('hermes_run').apply(lambda x: x['Cum_PSA_in']/1000*n_source['Monoammonium Phosphate in PSA']['conc g/L']/molar_weight['Monoammonium Phosphate (MAP)']['molecular weight g/mol']*stoich['Monoammonium Phosphate (MAP)']['N'])
    RCS_df['Cum_PSA_N_in'] = Cum_PSA_N_in.reset_index(level = 0, drop = True)

    #N-balance (cumulative N out) 
    Cum_biomass_N_out = RCS_df['Cum_biomass_draw']/molar_weight['Yeast']['molecular weight g/mol']*stoich['Yeast']['N'] #mols
    RCS_df['Cum_biomass_N_out'] = Cum_biomass_N_out.reset_index(level = 0, drop = True)

    Cum_riboflavin_N_out = RCS_df['Cum_riboflavin_draw']/molar_weight['Riboflavin']['molecular weight g/mol']*stoich['Riboflavin']['N']
    RCS_df['Cum_riboflavin_N_out'] = Cum_riboflavin_N_out.reset_index(level = 0, drop = True)

    Cum_broth_N_out = RCS_df['Cum_NH4_draw']/molar_weight['Ammonium']['molecular weight g/mol']*stoich['Ammonium']['N']
    RCS_df['Cum_broth_N_out'] = Cum_broth_N_out.reset_index(level = 0, drop = True)

    #N-balance (Accumulation)
    Biomass_N = RCS_df['Biomass_density']*RCS_df['Tank Weight post sample']/RCS_df['Broth Density']/molar_weight['Yeast']['molecular weight g/mol']*stoich['Yeast']['N'] # mols
    RCS_df['Biomass_N'] = Biomass_N.reset_index(level = 0, drop = True)

    Riboflavin_N = RCS_df['Riboflavin Titer in grams']*RCS_df['Tank Weight post sample']/molar_weight['Riboflavin']['molecular weight g/mol']*stoich['Riboflavin']['N']
    RCS_df['Riboflavin_N'] = Riboflavin_N.reset_index(level = 0, drop = True)

    Broth_N = RCS_df['Ammonium']*RCS_df['Tank Weight post sample']/molar_weight['Ammonium']['molecular weight g/mol']*stoich['Ammonium']['N']
    RCS_df['Broth_N'] = Broth_N.reset_index(level = 0, drop = True)

    #N-balance Total In
    N_in = biomass_N_init + MAP_N_init + Cum_base_N_in + Cum_PSA_N_in 
    RCS_df['N_in'] = N_in.reset_index(level = 0, drop = True)

    #N-Balance Total Out
    N_out = Cum_biomass_N_out + Cum_riboflavin_N_out + Cum_broth_N_out
    RCS_df['N_out'] = N_out.reset_index(level = 0, drop = True)

    #N-Balance Total Acc
    N_acc = Biomass_N + Riboflavin_N + Broth_N 
    RCS_df['N_acc'] = N_acc.reset_index(level = 0, drop = True)

    #Closure
    Closure = (RCS_df['N_out'] + RCS_df['N_acc'])/RCS_df['N_in']*100 # mols
    RCS_df['Closure'] = Closure.reset_index(level = 0, drop = True)
    RCS_df = RCS_df.round(2)

    return RCS_df
