import json
import numpy as np

def json_to_dict(filename):
    
    with open(filename) as json_file:
        jsn = json.load(json_file)
        #print("Datatype of variable: ", type(json_file))
        #print(json[0])
        for i in jsn:
            json_name = i #only output the title name
           
    string = json_name # need to generalize this - how to get the first string inside json file?
    #print(string)
    
    #create dictonary
    name_key = [] #name of the compound i.e NH4
    keys = list(jsn[string][0].keys()) # keys under each name
    keys.remove('name') #remove string "name" from key list
    values = [] #values of the element

    for s in jsn[string]: # get list of names
        name_key.append(s['name'])
        for e in keys: # get list of values from each keys under each names 
            values.append(s[e])

    dictionary = {}
    k = 0
    for i in range(len(name_key)):
        dictionary[name_key[i]] = {} #create dictionary with names
        for j in keys: #loop through each key under names
            dictionary[name_key[i]][j] = values[k] #add key and its value to each name
            k += 1
            
    return dictionary
