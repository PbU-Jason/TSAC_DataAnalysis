#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Nov 19 21:47:26 2022

@author: jasonpbu
"""

### package ###
import numpy as np
import pandas as pd 
import matplotlib.pyplot as plt
from operator import itemgetter
#====================

### selection ###
simFile = 'LongGRB_45_60.inc1.id1.sim'
#====================

### fixed variables ###
scatter_list = []
#====================

### function ###
def ExtractPosition(File, StoreList):
    with open(File) as f:
        while True:
            line = f.readline()
            if not line:
                break
            
            if line[0] == 'H':
                info = [list(filter(None, i.split(';'))) for i in line.split()]
                x = format(float(info[2][0]), '.3f')
                y = format(float(info[3][0]), '.3f')
                z = format(float(info[4][0]), '.3f')
                if [x, y, z] not in scatter_list:
                    StoreList.append([x, y, z])
        StoreList.sort(key = itemgetter(2, 0, 1))
    return
    
def Categorise(row):  
    if row['Z'] == format(4.437, '.3f'):
        return 1
    elif row['X'] == format(4.437, '.3f'):
        return 2
    elif row['Y'] == format(4.437, '.3f'):
        return 3
    elif row['X'] == format(-4.437, '.3f'):
        return 4
    elif row['Y'] == format(-4.437, '.3f'):
        return 5
    else:
        return 'error'
#====================

### main code ###
ExtractPosition(simFile, scatter_list)

scatter_array = np.array(scatter_list)
df = pd.DataFrame(scatter_array, columns = ['X', 'Y', 'Z'])

fig = plt.figure(dpi=300)
ax = fig.add_subplot(111, projection='3d')
ax.scatter(df['X'].astype(float), df['Y'].astype(float), df['Z'].astype(float))
plt.show()

df['Detector'] = df.apply(Categorise, axis=1)
df.to_csv('PixelPosition.csv')
#====================