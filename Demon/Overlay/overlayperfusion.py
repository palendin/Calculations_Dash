import matplotlib.pyplot as plt
import pandas as pd
import os
import numpy as np
from scipy.integrate import odeint
from scipy.optimize import curve_fit
import math

#fit overlay perfusion to KPI


os.chdir(os.path.dirname(os.path.abspath(__file__)))

#regression fit for OL conc in tank vs effluent conc
overlay_perfusion = pd.read_csv('overlayperfusion.csv')

overlay_perfusion = overlay_perfusion.fillna(0)
print(overlay_perfusion)
#Preview the first 5 lines of the loaded data 
#top5 = data.head()

#add puseodo data in the end
#overlay_perfusion.loc[len(overlay_perfusion.index)] = [40, 9, 0, 0.57, 0]

broth_density = 1.02 # g/ml
overlay_density = 0.85 # g/ml
bioreactor_vol = 0.3/broth_density # Liters

OL_perfusion = overlay_perfusion['Overlay Rate g/L/hr']
OL_perfusion = (OL_perfusion*24*bioreactor_vol/overlay_density)/1000/bioreactor_vol # L/day
yield_std = overlay_perfusion.iloc[:,4]
prod_std = overlay_perfusion.iloc[:,6]

Yield = overlay_perfusion['Yield %']
Productivity = overlay_perfusion['Productivity g/L/hr']


#regression curve fit
def PerfusionKPICurveFit(X,a,b,c):
    #f = X/(a+b*X**(1/c))
    f = a*X/(1+b*X)**(1/c)
    return f

reg, cov  = curve_fit(PerfusionKPICurveFit, OL_perfusion, Yield) #reg contains fitted values in an array
reg1, cov1  = curve_fit(PerfusionKPICurveFit, OL_perfusion, Productivity) #reg contains fitted values in an array
print('yield coef are {}, {}, {}'.format(reg[0], reg[1], reg[2]))
print('prod coef are {}, {}, {}'.format(reg1[0], reg1[1], reg1[2]))

fig = plt.figure()
ax = fig.add_subplot()
ax.errorbar(OL_perfusion, Yield, yerr = yield_std, fmt = 'o', color = 'red')
#ax.scatter(OL_perfusion,Yield, marker = '*', color='red')
ax.plot(OL_perfusion, PerfusionKPICurveFit(OL_perfusion, *reg))
ax.set_xlabel('overlay perfusion rate (L/L/day)', fontsize=12)
ax.set_ylabel('yield', fontsize=12)
ax.text(0.3,6 , 'y={:0.2f}x/(1+{:0.2f}x^(1/{:0.2f}))'.format(reg[0], reg[1], reg[2]))

fig1 = plt.figure()
ax1 = fig1.add_subplot()
ax1.errorbar(OL_perfusion, Productivity, yerr = prod_std, fmt = 'o', color = 'red')
#ax1.scatter(OL_perfusion,Productivity, marker = '*', color='blue')
ax1.plot(OL_perfusion, PerfusionKPICurveFit(OL_perfusion, *reg1))
ax1.set_xlabel('overlay perfusion rate (L/L/day)', fontsize=12)
ax1.set_ylabel('productivity', fontsize=12)
ax1.text(0.3,0.4 , 'y={:0.2f}x/(1+{:0.2f}x^(1/{:0.2f}))'.format(reg1[0], reg1[1], reg1[2]))

plt.show()
