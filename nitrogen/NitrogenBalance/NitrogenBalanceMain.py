import numpy as np
import json
import os
import pandas as pd
import plotly.express as px
import dash
from dash import Dash, dcc, html, Input, Output
import dash_bootstrap_components as dbc
import plotly.graph_objects as go

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
        print(j)

        k += 1

#---------------------------------------------------------------------------------------
run_data = pd.read_csv('Run_Data.csv')
df = pd.DataFrame(run_data)
df['PSA mL'] = df['PSA mL'].shift(1) #shift column down by 1 to align riboflavin nitrogen with PSA addition
df_run_data = df.fillna(0) #replace NaN with 0

header = list(df_run_data.columns.values)                                                                                                                                             
#run_names = df_run_data['Hermes'] #key in dict
unique_run_names = df_run_data.Hermes.unique() #np array of unique hermes name

#Hermes,Time,Sample Type,Tank Weight Pre kg,Tank Weight Post kg
#Biomass g/L,Cum Biomass g,Riboflavin g/kg,Cum Riboflavin g
#Ammonium g/kg,PSA mL,Base Weight,Base totalizer mL

broth_density = 1.02 # g/ml
NH4OH_density = 0.91 # g/ml
diluted_NH4OH_density = 0.98

Weight_draw = df_run_data.groupby('Hermes').apply(lambda x: x['Tank Weight Pre kg']-x['Tank Weight Post kg'])
df_run_data['Weight_draw'] = Weight_draw.reset_index(level = 0, drop=True) #fix  multiindex so it can add to dataframe

Cum_weight_draw = df_run_data.groupby('Hermes').apply(lambda  x: x['Weight_draw'].cumsum())
df_run_data['Cum_weight_draw'] = Cum_weight_draw.reset_index(level = 0, drop=True)

Biomass_draw = df_run_data.groupby('Hermes').apply(lambda  x: x['Weight_draw']*x['Biomass g/L']/broth_density)
df_run_data['Biomass_draw'] = Biomass_draw.reset_index(level = 0, drop=True)

Cum_biomass_draw = df_run_data.groupby('Hermes').apply(lambda  x: x['Biomass_draw'].cumsum())
df_run_data['Cum_biomass_draw'] = Cum_biomass_draw.reset_index(level = 0, drop=True)

Riboflavin_draw = df_run_data.groupby('Hermes').apply(lambda  x: x['Weight_draw']*x['Riboflavin g/kg'])
df_run_data['Riboflavin_draw'] = Riboflavin_draw.reset_index(level = 0, drop=True)

Cum_riboflavin_draw = df_run_data.groupby('Hermes').apply(lambda  x: x['Riboflavin_draw'].cumsum())
df_run_data['Cum_riboflavin_draw'] = Cum_riboflavin_draw.reset_index(level = 0, drop=True)

NH4_draw = df_run_data.groupby('Hermes').apply(lambda x: x['Weight_draw']*x['Ammonium g/kg'])
df_run_data['NH4_draw'] = NH4_draw.reset_index(level = 0, drop = True)

Cum_NH4_draw = df_run_data.groupby('Hermes').apply(lambda  x: x['NH4_draw'].cumsum())
df_run_data['Cum_NH4_draw'] = Cum_NH4_draw.reset_index(level = 0, drop = True)

Cum_base_weight = df_run_data.groupby('Hermes').apply(lambda x: x['Base Weight'].iloc[0] - x['Base Weight'])
df_run_data['Cum_base_weight'] = Cum_base_weight.reset_index(level = 0, drop = True)

Cum_PSA_in = df_run_data.groupby('Hermes').apply(lambda  x: x['PSA mL'].cumsum()) #need to apply PSA cum function
df_run_data['Cum_PSA_in'] = Cum_PSA_in.reset_index(level = 0, drop = True)

#N-balance (initial)
biomass_N_init = df_run_data.groupby('Hermes')['Cum Biomass g'].nth(0)/molar_weight['Yeast']*stoich['Yeast']['N'] #init biomass for each run by extract 1st value of Cum biomass column
MAP_N_init = df_run_data.groupby('Hermes')['Tank Weight Pre kg'].nth(0)/broth_density*n_source['Monoammonium Phosphate in Media']['conc g/L']/molar_weight['Monoammonium Phosphate (MAP)']*stoich['Monoammonium Phosphate (MAP)']['N']

#N-balance (cumulative N in)
Cum_base_N_in = df_run_data.groupby('Hermes').apply(lambda x: x['Base totalizer mL']/1000*n_source['Diluted Ammonium Hydroxide']['conc M'] if x['Base Weight'].sum() == 0 else x['Base Weight']/NH4OH_density/1000*n_source['Ammonium Hydroxide']['conc M']) #mol
df_run_data['Cum_base_N_in'] = Cum_base_N_in.reset_index(level = 0, drop = True)

Cum_PSA_N_in = df_run_data.groupby('Hermes').apply(lambda x: x['Cum_PSA_in']/1000*n_source['Monoammonium Phosphate in PSA']['conc g/L']/molar_weight['Monoammonium Phosphate (MAP)']*stoich['Monoammonium Phosphate (MAP)']['N'])
df_run_data['Cum_PSA_N_in'] = Cum_PSA_N_in.reset_index(level = 0, drop = True)

#N-balance (cumulative N out) 
Cum_biomass_N_out = df_run_data['Cum_biomass_draw']/molar_weight['Yeast']*stoich['Yeast']['N'] #mols
df_run_data['Cum_biomass_N_out'] = Cum_biomass_N_out.reset_index(level = 0, drop = True)

Cum_riboflavin_N_out = df_run_data['Cum_riboflavin_draw']/molar_weight['Riboflavin']*stoich['Riboflavin']['N']
df_run_data['Cum_riboflavin_N_out'] = Cum_riboflavin_N_out.reset_index(level = 0, drop = True)

Cum_broth_N_out = df_run_data['Cum_NH4_draw']/molar_weight['Ammonium']*stoich['Ammonium']['N']
df_run_data['Cum_broth_N_out'] = Cum_broth_N_out.reset_index(level = 0, drop = True)

#N-balance (Accumulation)
Biomass_N = df_run_data['Biomass g/L']*df_run_data['Tank Weight Post kg']/broth_density/molar_weight['Yeast']*stoich['Yeast']['N'] #mols
df_run_data['Biomass_N'] = Biomass_N.reset_index(level = 0, drop = True)

Riboflavin_N = df_run_data['Riboflavin g/kg']*df_run_data['Tank Weight Post kg']/molar_weight['Riboflavin']*stoich['Riboflavin']['N']
df_run_data['Riboflavin_N'] = Riboflavin_N.reset_index(level = 0, drop = True)

Broth_N = df_run_data['Ammonium g/kg']*df_run_data['Tank Weight Post kg']/molar_weight['Ammonium']*stoich['Ammonium']['N']
df_run_data['Broth_N'] = Broth_N.reset_index(level = 0, drop = True)

#N-balance Total In
N_in = biomass_N_init + MAP_N_init + Cum_base_N_in + Cum_PSA_N_in 
df_run_data['N_in'] = N_in.reset_index(level = 0, drop = True)

#N-Balance Total Out
N_out = Cum_biomass_N_out + Cum_riboflavin_N_out + Cum_broth_N_out
df_run_data['N_out'] = N_out.reset_index(level = 0, drop = True)

#N-Balance Total Acc
N_acc = Biomass_N + Riboflavin_N + Broth_N 
df_run_data['N_acc'] = N_acc.reset_index(level = 0, drop = True)

#Closure
Closure = (df_run_data['N_out'] + df_run_data['N_acc'])/df_run_data['N_in']*100
df_run_data['Closure'] = Closure.reset_index(level = 0, drop = True)
df_run_data = df_run_data.round(2)


#print(df_run_data.info())
#print(df_run_data.iloc[:,30:40]) display column 30 - 40
#df = df_run_data[df_run_data['Hermes'].isin(['H11433-21','H11433-22'])].iloc[-1:]
#print(df)

#using plotly and dash for visualization
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
colors = {
    'dark': True,
    'detail': '#007439',
    'primary': '#00EA64',
    'secondary': '#6E6E6E',
}

# used in dropdown menu
runs = df_run_data.Hermes.unique()
headers = list(df_run_data.columns.values)  

#how to use div https://stackoverflow.com/questions/62234909/layout-management-in-plotly-dash-app-how-to-position-html-div
app.layout = html.Div([

    # boostrapping, every dbc.row is a new row.
    dbc.Row([dbc.Col(html.H1('Nitrogen Balance', style = {'text-align': 'center'}))]),
    
    dbc.Row([dbc.Col(html.Label('Select Run',style={'font-weight': 'bold', "text-align": "start", 'font-size': 25}), width = 6, className = 'bg-primary ps-4'),
             dbc.Col(html.Label('Select Run',style={'font-weight': 'bold', "text-align": "start", 'font-size': 25}), width = 6, className = 'bg-primary ps-4')
            ], justify = 'start'),
    
    dbc.Row([dbc.Col([dcc.Dropdown(id='Hermes',
                    options=[{'label': i, 'value': i} for i in runs],   #df_run_data['Hermes']], #user will see this
                    value= None, #[i for i in df_run_data['Hermes']],  #default values to show runs
                    multi=True,
                    # style={'width':'40%','display': 'inline-block'}
                    )], width = 6, className = 'bg-secondary ps-4 pe-4'),
    
            dbc.Col([dcc.Dropdown(id='Columns',
                    options=[{'label': i, 'value': i} for i in headers],   
                    value= None, 
                    multi=True,
                    # style={'width':'40%','display': 'inline-block'}
                    )], width = 6, className = 'bg-secondary ps-4 pe-4'),
            
            ], justify = 'start'
           ),
    html.Div(id ='output_container', children=[]),
    #html.Br(), #break here we want the space between divider and graph
    dbc.Row([dbc.Col([dcc.Graph(id='balance',figure={},
                    # style={'width': '80vh', 'height': '50vh'}
                    )], width = 6),
             dbc.Col([dcc.Graph(id='balance1',figure={},
                    # style={'width': '80vh', 'height': '50vh'}
                    
                    )], width = 6)])
 
])

#--------call back--------- 
#connect output to html.div and dcc.Graph
@app.callback(
    [Output(component_id = 'output_container', component_property = 'children'), #relate to html.div
     Output(component_id = 'balance', component_property = 'figure'),
     Output(component_id = 'balance1', component_property = 'figure')], #relate to dcc.graph
    [Input(component_id = 'Hermes', component_property = 'value'),
     Input(component_id = 'Columns', component_property = 'value')],
      #relate to dcc.dropdown 
)

#to connect Plotly graphs with Dash Components
def update_graph(option_hermes, data_columns): #1 input per arg. 1 def for each callback. always refers to input
    print(option_hermes)
    #print(type(option_hermes))
    container1 = 'Hermes selected is: {}'.format(option_hermes) 
    container2 = 'Data selected is: {}'.format(data_columns)
    print(container1)

    dff = df_run_data.copy() #best to play around with the copy of dataframe
    dff = dff[dff['Hermes'].isin(option_hermes)] #for multi: True. display relevant dataframe if it contains hermes
    dff1 = dff.loc[:, dff.columns.isin(data_columns)]
    print(dff1)
    #y_dff = dff[str(data_columns)]
    #print(y_dff)
    # filtering columns by name


    # hermes column disappears from df after grouping
    #dff_last = dff.groupby('Hermes').last()
    #dff_last['Hermes'] = option_hermes #add selected hermes back to df
    #dff_last = dff_last[dff_last['Hermes'].isin(option_hermes)] #display last row base on hermes input
    
    #dff = dff[dff['Hermes'] == option_hermes] #filters dataframe based on selected hermes (for multi:false)

    scatter = px.scatter(dff1, x=dff1.iloc[:,0], y=dff1.iloc[:,1:len(data_columns)], color=dff['Hermes'], title = 'Closure vs Time') # 'Time','Closure'
    scatter.update_traces(mode='markers+lines')

    #fig1 = px.bar(dff_last, x='Hermes', y='Closure', color ='Hermes', title = 'Overall Closure')
    #fig1.update_traces()
    #below fig1 also works referring to dff
    #fig1 = px.bar(dff, x=dff.groupby('Hermes')['Hermes'].last(), y=dff.groupby('Hermes')['Closure'].last(), color = dff.groupby('Hermes')['Hermes'].last())
    #fig.show()

    return container1, container2, scatter #return is going to the output (#output call back = # of returns)

#plot for total in N, total out N base on hermes selection

if __name__ == '__main__':
    app.run_server(debug=True)

# '''
# #build dictionary of the raw data
# dict = {}
# i = 0
# j = 0
# for urn in unique_run_names:
#     single_run = df_run_data.loc[df_run_data['Hermes'] == unique_run_names[i]] #dataframe for single run  
#     #print(form_array(header,single_run))
#     #dict[urn] = form_array(header,single_run)
#     dict[urn] = {}
#     for h in header:
#         #print(j)
#         if j < len(header): #len counts from 1.
#             dict[urn][h] = form_array(header,single_run)[j]
#             j += 1
#     i += 1
#     j = 0
# #print(dict['H11433-21']['Ammonium g/kg'])

# #perform calculations with dictionary 

# base_weight = df_run_data['Base Weight'].values #g
# base_weight_sum = sum(base_weight,0) #for logic check whether to use weight or totalizer

# for urn in unique_run_names:
#     #convert into np array, so each array variable is made of individual arrays of data so its easier to work with
#     Weight_drawed = np.array(dict[urn]['Tank Weight Pre kg']) - np.array(dict[urn]['Tank Weight Post kg']) 
    
#     Cum_weight_drawed = np.array(cum_calc(Weight_drawed))
    
#     Biomass_drawed = np.array(dict[urn]['Biomass g/L'])*Weight_drawed/broth_density
#     Cum_biomass_drawed = np.array(cum_calc(Biomass_drawed))

#     Riboflavin_drawed = np.array(dict[urn]['Riboflavin g/kg'])*Weight_drawed
#     Cum_riboflavin_drawed = np.array(cum_calc(Riboflavin_drawed))

#     NH4_drawed = np.array(dict[urn]['Ammonium g/kg'])*Weight_drawed
#     Cum_NH4_drawed = np.array(cum_calc(NH4_drawed))
    
#     Biomass = np.array(dict[urn]['Biomass g/L'])
#     Riboflavin = np.array(dict[urn]['Riboflavin g/kg'])
#     NH4 = np.array(dict[urn]['Ammonium g/kg'])
#     Tankweight_pre = np.array(dict[urn]['Tank Weight Pre kg'])
#     Tankweight_post = np.array(dict[urn]['Tank Weight Post kg'])
#     Base_totalizer = np.array(dict[urn]['Base totalizer mL'])
#     Base_weight = np.array(dict[urn]['Base Weight'])
#     PSA = np.array(dict[urn]['PSA mL'])

#     #N-balance (initial)
#     biomass_N_init = Biomass[0]*Tankweight_pre[0]/broth_density/molar_weight['Yeast']*stoich['Yeast']['N'] #init biomass for each run
#     MAP_N_init = Tankweight_pre[0]/broth_density*n_source['Monoammonium Phosphate in Media']['conc g/L']/molar_weight['Monoammonium Phosphate (MAP)']*stoich['Monoammonium Phosphate (MAP)']['N']
 
#     #N-balance (cumulative N in) 
#     if base_weight_sum == 0: #decide to use base weight or base totalizer
#         Cum_base_N_in = Base_totalizer/1000*n_source['Diluted Ammonium Hydroxide']['conc M'] #mol
#     else:
#         Cum_base_weight = Base_weight[0] - Base_weight
#         Cum_base_N_in = Cum_base_weight/NH4OH_density/1000*n_source['Ammonium Hydroxide']['conc M'] #mols
   
#     Cum_PSA_N_in = np.array(PSA_cum_calc(PSA))/1000*n_source['Monoammonium Phosphate in PSA']['conc g/L']/molar_weight['Monoammonium Phosphate (MAP)']*stoich['Monoammonium Phosphate (MAP)']['N']

#     #N-balance (cumulative out) 
#     Cum_biomass_N_out = Cum_biomass_drawed/molar_weight['Yeast']*stoich['Yeast']['N'] #mols
#     Cum_riboflavin_N_out = Cum_riboflavin_drawed/molar_weight['Riboflavin']*stoich['Riboflavin']['N']
#     Cum_broth_N_out = Cum_NH4_drawed/molar_weight['Ammonium']*stoich['Ammonium']['N']
    
#     #N-balance (Accumulation)
#     Biomass_N = Biomass*Tankweight_post/broth_density/molar_weight['Yeast']*stoich['Yeast']['N'] #mols
#     Riboflavin_N = Riboflavin*Tankweight_post/molar_weight['Riboflavin']*stoich['Riboflavin']['N']
#     Broth_N = NH4*Tankweight_post/molar_weight['Ammonium']*stoich['Ammonium']['N']
    
#     #N-balance Total In
#     N_in = biomass_N_init + MAP_N_init + Cum_base_N_in + Cum_PSA_N_in 
#     N_out = Cum_biomass_N_out + Cum_riboflavin_N_out + Cum_broth_N_out
#     N_acc = Biomass_N + Riboflavin_N + Broth_N

#     #Closure
#     Closure = (N_out + N_acc)/N_in*100
#     Hermes = np.array([urn]*len(Closure))

# header = []
# dataframe = []
# with open('countries.csv', 'w', encoding='UTF8') as f:
#     writer = csv.writer(f)

#     # write the header
#     writer.writerow(header)
#     # write the data
#     writer.writerow(dataframe)


# #A = locals().keys()
# #B = list(A)
# #print(B[0])

# #print(Biomass_drawed[1][0])  #access elements (array, index)


# #N-balance (cumulative in)
# base_weight = df_run_data['Base Weight'].values
# base_weight_sum = sum(base_weight,0)

# if base_weight_sum == 0:
#     Cum_NH4_in = cum_calc(unique_run_names, Base_totalizer)
# #print(Base_totalizer)
# #print(Cum_NH4_in)



# A = np.array(Draw_weight[0]) #convert into array

# #A = Biomass_drawed[0]*Draw_weight[0]
# #print(A[5])

# for i in A: #unpack list within list to make it work with dictionary
#     for j in i:
#         ns_conc_key.append(j)


# def cum_calc(name,data_array):
#     array = []
#     for n in range(len(name)): #loop through individual runs
#         v = data_array[n][0] #initial value for the run
#         array_length = range(len(data_array[n]))
#         for l in array_length:
#             if l <  len(array_length) - 1: 
#                 v = v + data_array[n][l+1] #exclude initial value in the array. need to reduce loop by 1
#                 array.append(v)
#     return array

# A = np.array([1,2]) 
# B = np.array([1,2,3,4])
# C = B[:, np.newaxis] + A #broadcasting so A+B works
# print(C) 
# '''
# '''
# html.H1('Nitrogen Balance', style = {'text-align': 'center'}),

#     #html.Div('Select Run'),
#     html.Div(children=[ #first row
#         html.Div(children=[ #first column first row
#             html.Label('Select Run',style={'font-weight': 'bold', "text-align": "center", 'font-size': 25, 'display': 'inline-block'}),
#             html.Label('Select Run',style={'font-weight': 'bold', "text-align": "center", 'font-size': 25, 'display': 'inline-block'}),
#             ]),
#         html.Div(children=[ #first column second row (since no inline previous)
#             dcc.Dropdown(
#                 id='Hermes',
#                 options=[{'label': i, 'value': i} for i in runs],   #df_run_data['Hermes']], #user will see this
#                 value= None, #[i for i in df_run_data['Hermes']],  #default values to show runs
#                 multi=True,
#                 style={'width':'40%','display': 'inline-block'}
#                 ),
#             dcc.Dropdown(
#                 id='Columns',
#                 options=[{'label': i, 'value': i} for i in headers],   #df_run_data['Hermes']], #user will see this
#                 value= None, #[i for i in df_run_data['Hermes']],  #default values to show runs
#                 multi=True,
#                 style={'width':'40%','display': 'inline-block'}
#                 ),
#             ])
#         ]),
#     html.Div(id ='output_container', children=[]),
#     html.Br(), #break here we want the space between divider and graph
#     dcc.Graph(id='balance',figure={}, style={'width': '80vh', 'height': '50vh'}), #can hard code a figure variable, but thats not adjustable. 
#     dcc.Graph(id='balance1',figure={}, style={'width': '80vh', 'height': '50vh'}) 
# '''