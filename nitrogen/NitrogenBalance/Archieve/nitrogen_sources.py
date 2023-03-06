import json
import os

data1 = {
    'nitrogen_sources': [
        {
            'name' : 'Ammonium Hydroxide',
            'conc M' : 14.8,
            'conc g/L' : 518.6
        },
        {
            'name' : 'Diluted Ammonium Hydroxide',
            'conc M' : 2.96,
            'conc g/L' : 103.7
        },
        {
            'name' : 'Monoammonium Phosphate in Media',
            'conc M' : 0.061,
            'conc g/L' : 7
        },
        {
            'name' : 'Monoammonium Phosphate in PSA',
            'conc M' : 0.56,
            'conc g/L': 64.8
        }
    ]
}

data2 = {
    'stoichiometry': [
        {
            'name' : 'Yeast',
            'C' : 4,
            'H' : 7.44,
            'O' : 2.64,
            'N' : 0.68,
            'P' : 0
        },
        {
            'name' : 'Ammomium Hydroxide',
            'C' : 0,
            'H' : 5,
            'O' : 1,
            'N' : 1,
            'P' : 0
        },
        {
            'name' : 'Monoammonium Phosphate (MAP)',
            'C' : 0,
            'H' : 6,
            'O' : 4,
            'N' : 1,
            'P' : 1
        },
        {
            'name' : 'Ammonium',
            'C' : 0,
            'H' : 4,
            'O' : 0,
            'N' : 1,
            'P' : 0
        },
        {
            'name' : 'Riboflavin',
            'C' : 17,
            'H' : 20,
            'O' : 6,
            'N' : 4,
            'P' : 0
        }
    ]
}

data3 = {
    'molecular weight': [
        {
            'name' : 'C',
            'molecular weight g/mol' : 12
        },
        {
            'name' : 'H',
            'molecular weight g/mol' : 1
        },
        {
            'name' : 'O',
            'molecular weight g/mol' : 16
        },
        {
            'name' : 'N',
            'molecular weight g/mol' : 14
        },
        {
            'name' : 'P',
            'molecular weight g/mol' : 31
        },
        {
            'name' : 'Yeast',
            'molecular weight g/mol' : 107
        },
        {
            'name' : 'Monoammonium Phosphate (MAP)',
            'molecular weight g/mol' : 115
        },
        {
            'name' : 'Riboflavin',
            'molecular weight g/mol' : 376
        },
        {
            'name' : 'Ammonium',
            'molecular weight g/mol' : 18
        }
    ]
}
json_string = json.dumps(data1, indent=4)
path = os.path.dirname(__file__)
with open(os.path.join(path,'nitrogen_sources.json'), 'w') as outfile:
    outfile.write(json_string)

json_string = json.dumps(data2, indent=4)
path = os.path.dirname(__file__)
with open(os.path.join(path,'stoichiometry.json'), 'w') as outfile:
    outfile.write(json_string)

json_string = json.dumps(data3, indent=4)
path = os.path.dirname(__file__)
with open(os.path.join(path,'molecular_weight.json'), 'w') as outfile:
    outfile.write(json_string)