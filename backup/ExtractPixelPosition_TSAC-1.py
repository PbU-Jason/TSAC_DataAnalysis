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
# simFile = 'Crab_pol_10ks_rotate_0.inc1.id1.sim' # rotate 0 deg
simFile = 'Crab_pol_10ks_rotate_45.inc1.id1.sim' # rotate +45 deg along y-axis (right hand rule)
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
            
            if line[0] == 'H': # only pick up those info start with 'H'Tsim
                info = [list(filter(None, i.split(';'))) for i in line.split()] # ignore space, none & ;
                x = format(float(info[2][0]), '.5f') # save x to str with .5f
                y = format(float(info[3][0]), '.5f') # save y to str with .5f
                z = format(float(info[4][0]), '.5f') # save z to str with .5f
                if [x, y, z] not in scatter_list:
                    StoreList.append([x, y, z])
        StoreList.sort(key = itemgetter(2, 0, 1)) # order by z -> x -> y
    return

def UpperSurface(X, Y, Z):
    return (1/np.sqrt(2)) * X + 0 * Y + (1/np.sqrt(2)) * Z - (2.953) # 2.953 from rotating 0 deg
    
def LowerSurface(X, Y, Z):
    return (1/np.sqrt(2)) * X + 0 * Y + (1/np.sqrt(2)) * Z - (0.695) # 0.695 from rotating 0 deg

def BGO_SideSurface(X, Y, Z):
    return (1/np.sqrt(2)) * X + 0 * Y + (1/np.sqrt(2)) * Z - (2.850) # 2.850 from rotating 0 deg

def BGO_BottomSurface(X, Y, Z):
    return (1/np.sqrt(2)) * X + 0 * Y + (1/np.sqrt(2)) * Z - (-1.15) # -1.15 from rotating 0 deg

def Categorise(row):
    if abs(UpperSurface(float(row['X']), float(row['Y']), float(row['Z']))) <=  1e-5:
        return 1
    elif abs(LowerSurface(float(row['X']), float(row['Y']), float(row['Z']))) <=  1e-5:
        return 2
    elif abs(BGO_SideSurface(float(row['X']), float(row['Y']), float(row['Z']))) <=  1e-5 or abs(BGO_BottomSurface(float(row['X']), float(row['Y']), float(row['Z']))) <=  1e-5:
        return 3
    else:
        return 'error'
#====================

### main code ###
ExtractPosition(simFile, scatter_list)

scatter_array = np.array(scatter_list)
df = pd.DataFrame(scatter_array, columns = ['X', 'Y', 'Z'])
df['Detector'] = df.apply(Categorise, axis=1)
df.to_csv('TSAC-1_PixelPosition.csv')

upper, lower, bgo = df.groupby('Detector')
upper = upper[1]
lower = lower[1]
bgo = bgo[1]

fig = plt.figure(dpi=300)
ax = fig.add_subplot(111, projection='3d')
ax.scatter(upper['X'].astype(float), upper['Y'].astype(float), upper['Z'].astype(float), color='blue')
ax.scatter(lower['X'].astype(float), lower['Y'].astype(float), lower['Z'].astype(float), color='green')
ax.scatter(bgo['X'].astype(float), bgo['Y'].astype(float), bgo['Z'].astype(float), color='red')
plt.show()
#====================