import numpy as np
import pandas as pd
import seaborn as sns
import statsmodels.api as sm
import matplotlib.pyplot as plt

#%matplotlib inline
broth_overlay = pd.read_csv('overlay data.csv')
print(broth_overlay.columns.values)
x = broth_overlay['Time']
y = broth_overlay['% Overlay In Effluent']

reverse_settler = ['H12922-3']
VDS_settler = [ 'H12922-4']
reverse = broth_overlay[broth_overlay['Hermes'].isin(reverse_settler)]
x1 = reverse['Time']
y1 = reverse['% Overlay In Effluent']

VDS = broth_overlay[broth_overlay['Hermes'].isin(VDS_settler)]
x2 = VDS['Time']
y2 = VDS['% Overlay In Effluent']

print(x1)
print(y1)
fig, ax = plt.subplots()
ax.scatter(x1, y1, 200, color='blue')
ax.scatter(x2, y2, 200, color='red')
ax = sns.regplot(x=x, y=y, color='gray')
ax.set(xlabel = 'Time (hr)', ylabel = 'Effluent Overlay %')
plt.show()