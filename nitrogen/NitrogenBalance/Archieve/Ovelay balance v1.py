import matplotlib.pyplot as plt
import pandas as pd
import os
import numpy as np
from scipy.integrate import odeint

#Myrcene balance around inlet and effluent outlet
def Overlay_Conc_In_Tank(y, t):
    dydt = (Fin*C_overlay - LLSmax*y/(K+y)*Fe)/300
    return dydt

#varying Overlay addition rate. 
Overlay_amount = np.array([0,10,30,50,60]) #g/day
#print(Overlay_amount)
F_overlay = Overlay_amount/(24*60) # g/min
Fe = 70/(60*24) # pump out at 4%, ~ 70 g/day
F_water = Fe # g/min
Fin = F_water + F_overlay # g/min
C_overlay = F_overlay*1/(Fin) 
K = 0.05
LLSmax = 0.9

y_init1 = np.empty(np.size(Overlay_amount))
y_init1.fill(0.2) #intial merycene 20%
t = np.linspace(0, 24*120, 30) #600 mins (10hrs)

y1 = odeint(Overlay_Conc_In_Tank, y_init1, t)

plt.plot(t,y1, linestyle="-", linewidth = 3, marker='o', markersize = 8)
plt.ylabel("No initial overlay",color="black",fontsize=25)
loc = (0,10,30,50,60)
plt.legend(Overlay_amount)
plt.show()