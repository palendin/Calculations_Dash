import matplotlib.pyplot as plt
import pandas as pd
import os
import numpy as np
from scipy.integrate import odeint
from scipy.optimize import curve_fit

#regression fit for OL conc in tank vs effluent conc
overlay_data = pd.read_csv("Overlay_Data.csv") #, encoding = "ISO-8859-1", engine='python')
#Preview the first 5 lines of the loaded data 
#top5 = data.head()
tank_OL = overlay_data['OL conc']
tank_OL = tank_OL[np.logical_not(np.isnan(tank_OL))] #removes NaN from the data
effluent_OL = overlay_data['Effluent Conc']
effluent_OL = effluent_OL[np.logical_not(np.isnan(effluent_OL))]
OL_density = 0.85

Time =  overlay_data['Time (min)']
Capillary_Free_Oil  = overlay_data['Capillary Free oil g/g']

Time1 = Time[0:7]
Capillary_Free_Oil1 = Capillary_Free_Oil[0:7]
print(Capillary_Free_Oil1)
Capillary_Free_Oil2 = Capillary_Free_Oil[7:14]
print(Capillary_Free_Oil2)

#regression curve fit
def OverlayCurveFit(tank_overlay,max_effluent_overlay,K):
    effluent_overlay = max_effluent_overlay*tank_overlay/(0.2*K+tank_overlay) 
    return effluent_overlay

reg, cov  = curve_fit(OverlayCurveFit, tank_OL, effluent_OL) #reg contains fitted values in an array

x = np.linspace(0,30,60)
fig,ax = plt.subplots()
ax.plot(tank_OL, OverlayCurveFit(tank_OL, *reg),linewidth = 3, label='measured')
ax.plot(x, OverlayCurveFit(x,*reg), 'r--', linewidth = 3, label='fit')
plt.xlabel('tank overlay concentration %')
plt.ylabel('effluent overlay concentration %')

#Myrcene balance around inlet and effluent outlet
def Overlay_Conc_In_Tank(y, t):
    
    V = y[0] #Volume
    C = y[1] #OL conc
    dVdt = Fin - Fout
    dCdt = (Fin*C_overlay - Cs_max*C/(K+C)*Fout)/V # %OL g/g

    return [dVdt,dCdt]

#varying Overlay addition rate. 
tank_type = '0.5L'
if tank_type == '20L':
    Tank_volume = 12 # L
    weight_increase = 10 # %
    Overlay_amount = [0,3150] #g/day
    #Overlay_amount = 20
    #print(Overlay_amount)
    #Effluent = 2.4 # g/min
    Fin = 5.3 # total inlet into the tank g/min
    #Return = 2.5 # g/min
    Fout = Fin - weight_increase*Tank_volume*1000/144000 # Fout should just be the effluent since return stream does not affect it  # + Return #200/(60*24) # pump out at 4%, ~ 70 g/day
    #Fin = F_water + F_overlay # g/min 
    print(Fout, 'g/min')
if tank_type == '0.5L':
    Tank_volume = 0.3 # L
    weight_increase = 10 # 19
    Overlay_amount = [0,80] #g/day
    #Overlay_amount = 20
    #print(Overlay_amount)
    #Fout = 3.16 #200/(60*24) # pump out at 4%, ~ 70 g/day
    Fin = 0.125 # total inlet g/min
    Fout = Fin - weight_increase*Tank_volume*1000/144000 # Fout should just be the effluent since return stream does not affect it  # + Return #200/(60*24) # pump out at 4%, ~ 70 g/day
    #Fin = F_water + F_overlay # g/min 
    print(Fout, 'g/min')

K = reg[1]
Cs_max = reg[0]

y_init = [Tank_volume*1000,0] # vol in ml, %% overlay
t = np.linspace(0, 3000, 30) #mins

fig,(ax,ax2) = plt.subplots(1,2)
for i in range(len(Overlay_amount)):
    F_overlay = Overlay_amount[i]/(24*60) # g/min
    C_overlay = F_overlay*100/(Fin) #%g/g
    #F_water = Fin - F_overlay
    y1 = odeint(Overlay_Conc_In_Tank, y_init, t)
    V = y1[:,0]
    C_percent = y1[:,1] #percent OL
    C_grams = C_percent/100*V*OL_density # grams OL
    ax.plot(t, C_percent, linewidth=3, marker="o", markersize = 7)
    ax.plot(Time1, Capillary_Free_Oil1, linewidth=3, marker="o", markersize = 7)
    ax.plot(Time1, Capillary_Free_Oil2, linewidth=3, marker="o", markersize = 7)
    ax.set_xlabel("Time (mins)", fontsize=20)
    ax.set_ylabel("Overlay % in tank", fontsize=20)
    #ax2 = ax.twinx() #allows to make another plot in the same figure on different axis.
    ax2.plot(t, V, linewidth=3, marker=None, markersize = 7)
    ax2.set_ylabel("Volume (ml)", fontsize=20)
    #ax.legend(Overlay_amount)
    #ax2.spines['right'].set_position(('outward', 20))
  
plt.show()
'''
    #creates 2 plots separately, no need to call twinx(), because two plots are called in the for loop (ax,ax2).
    fig,(ax,ax2) = plt.subplots(1,2)
    for i in range(len(Overlay_amount)):
    F_overlay = Overlay_amount[i]/(24*60) # g/min
    C_overlay = F_overlay*1/(Fin)
    F_water = Fin - F_overlay
    y1 = odeint(Overlay_Conc_In_Tank, y_init, t)
    V = y1[:,0]
    C = y1[:,1]
    ax.plot(t, C*100, linewidth=3, marker="o", markersize = 7)
    ax.set_xlabel("Time (mins)", fontsize=20)
    ax.set_ylabel("Overlay % in tank", fontsize=20)
    #ax2 = ax.twinx() #allows to make another plot in the same figure on different axis.
    ax2.plot(t, V, linewidth=3, marker=None, markersize = 7)
    ax2.set_ylabel("Volume (ml)", fontsize=20)
  
    #creates 2 plots in the same figure by calling twinx(), only need to call 1 plot (ax) in the subplot function.
    fig,ax = plt.subplots()
    for i in range(len(Overlay_amount)):
    F_overlay = Overlay_amount[i]/(24*60) # g/min
    C_overlay = F_overlay*1/(Fin)
    F_water = Fin - F_overlay
    y1 = odeint(Overlay_Conc_In_Tank, y_init, t)
    V = y1[:,0]
    C = y1[:,1]
    ax.plot(t, C*100, linewidth=3, marker="o", markersize = 7)
    ax.set_xlabel("Time (mins)", fontsize=20)
    ax.set_ylabel("Overlay % in tank", fontsize=20)
    ax2 = ax.twinx() #allows to make another plot in the same figure on different axis.
    ax2.plot(t, V, linewidth=3, marker=None, markersize = 7)
    ax2.set_ylabel("Volume (ml)", fontsize=20)
'''

t = np.linspace(0,10,100)
A = np.ones(len(t))*5.2
A[50:] = 5.1