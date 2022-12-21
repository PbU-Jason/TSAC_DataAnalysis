#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Nov 19 23:35:49 2022

@author: jasonpbu
"""

### package ###
import re
import sys
import numpy as np
import pandas as pd 
import matplotlib.pyplot as plt
#====================

### selection ###
pixel_position_file = sys.argv[1]              # sys.argv[1] is pixel position file
sim_file = sys.argv[2]                         # sys.argv[2] is sim file
energy_threshold = float(sys.argv[3])          # sys.argv[3] is energy threshold
output_low_energy_limit = float(sys.argv[4])   # sys.argv[4] is output low energy limit
output_high_energy_limit = float(sys.argv[5])  # sys.argv[5] is output high energy limit

# pixel_position_file = '/Users/jasonpbu/Desktop/TSAC/DataAnalysis/TSAC-2/rate_analysis/PixelPosition.csv'              # sys.argv[1] is pixel position file
# sim_file = '/Users/jasonpbu/Desktop/TSAC/DataAnalysis/TSAC-2/rate_analysis/LongGRB_45_60.inc1.id1.sim'                         # sys.argv[2] is sim file
# energy_threshold = 15          # sys.argv[3] is energy threshold
# output_low_energy_limit = 50   # sys.argv[4] is output low energy limit
# output_high_energy_limit = 300  # sys.argv[5] is output high energy limit
#====================

### fixed variables ###
pattern_Beam = re.compile(r"BeamType FarFieldPointSource (-*[0-9]+\.*[0-9]*) (-*[0-9]+\.*[0-9]*)")
pattern_SE = re.compile(r"SE") # each event starts
pattern_HTsim = re.compile(r"""
                           HTsim\s(\d+);              # label
                           \s*(-?\d+\.\d+);           # x
                           \s*(-?\d+\.\d+);           # y
                           \s*(-?\d+\.\d+);           # z
                           \s*(-?\d+\.\d+);           # energy
                           \s*(\d\.\d{5}e[+-]\d{2});  # time
                           """, re.VERBOSE)
                           
pattern_EN = re.compile(r"EN")                   # total events end
pattern_TE = re.compile(r"TE ([0-9]+\.*[0-9]*)") # simulation time
#====================

### function ###
def ExtractUsefulInfo(PixelPositionFile, SimFile):
    pixel_position_df = pd.read_csv(PixelPositionFile, dtype=str)
    pixel_position_df = pixel_position_df.drop([str(list(pixel_position_df.keys())[0])], axis=1) # drop index in .csv
    with open(SimFile) as f:
        direction_bool = True
        first_SE_bool = False
        total_events_list = []
        each_event_list = []
        while True:
            line = f.readline()
            if not line:
                break
            
            if pattern_Beam.match(line):
                direction = pattern_Beam.findall(line)
                direction_bool = False
            
            if pattern_TE.match(line):
                time = pattern_TE.findall(line)
                
            if pattern_HTsim.match(line):
                hit_info = pattern_HTsim.findall(line)
                each_event_list.append([float(hit_info[0][1]), float(hit_info[0][2]), float(hit_info[0][3]), float(hit_info[0][4])])
            
            if (pattern_SE.match(line) and first_SE_bool) or pattern_EN.match(line): # collect all hit info above SE (ignore first) or EN
                total_events_list.append(each_event_list)
                each_event_list = []  
            if pattern_SE.match(line): # to ignore first SE
                first_SE_bool = True
               
        if direction_bool:
            direction = 'bkg'
    return pixel_position_df, direction, time, total_events_list
   
def CountRate_and_HitDistribution(PixelPositionDF, Time, TotalEventsList, EnergyThreshold, OutputLowEnergyLimit, OutputHighEnergyLimit):
    event_count = 0
    total_hits_above_energy_threshold_list = []
    for each_event_list in TotalEventsList:
        event_count += 1
        for each_event in each_event_list:
            if each_event[3] >= EnergyThreshold:
                x = format(float(each_event[0]), '.3f')
                y = format(float(each_event[1]), '.3f')
                z = format(float(each_event[2]), '.3f')
                fit_pixel = PixelPositionDF.loc[(PixelPositionDF['X'] == x) & (PixelPositionDF['Y'] == y) & (PixelPositionDF['Z'] == z)]
                total_hits_above_energy_threshold_list.append([event_count, fit_pixel.iat[0, 3], each_event[3], '1'])
        
    total_hits_above_energy_threshold_array = np.array(total_hits_above_energy_threshold_list)
    total_hits_above_energy_threshold_df = pd.DataFrame(total_hits_above_energy_threshold_array, columns = ['Event', 'Detector', 'Energy', 'Hit'])   
    total_hits_above_energy_threshold_df = total_hits_above_energy_threshold_df.astype(float)

    combined_hits_above_energy_threshold_df = total_hits_above_energy_threshold_df.groupby(['Event', 'Detector']).agg({'Energy': 'sum', 'Hit': 'count'}).reset_index()
    combined_hits_above_energy_threshold_in_output_energy_df = combined_hits_above_energy_threshold_df[(combined_hits_above_energy_threshold_df['Energy'] >= OutputLowEnergyLimit) & (combined_hits_above_energy_threshold_df['Energy'] <= OutputHighEnergyLimit)]
    
    count_rate_df = combined_hits_above_energy_threshold_in_output_energy_df.groupby('Detector').size().to_frame('Count Rate')
    count_rate_df['Count Rate'] = count_rate_df['Count Rate'].div(Time)
    
    hit_distribution_df = combined_hits_above_energy_threshold_df.groupby('Hit').size().to_frame('Number Rate')
    hit_distribution_df['Number Rate'] = hit_distribution_df['Number Rate'].div(Time)
    return count_rate_df, hit_distribution_df

def PrintOutput(SimFile, Direction, Time, CountRateDF, HitDistributionDF):
    print('==================================================')
    print('sim file            :', SimFile)
    print('source direction    :', Direction)
    print('simulation time     :', float(Time[0]))
    print('energy threshold    :', energy_threshold) 
    print('output energy range :', (output_low_energy_limit, output_high_energy_limit))
    print('--------------------')
    print('count rate          :')
    print(CountRateDF)
    print('--------------------')
    print('hit distribution    :')
    print(HitDistributionDF)
    print('==================================================')
    return
#====================

### main code ###
if __name__ == "__main__":
    pixel_position_df, direction, time, total_events_list = ExtractUsefulInfo(pixel_position_file, sim_file)
    count_rate_df, hit_distribution_df = CountRate_and_HitDistribution(pixel_position_df, float(time[0]), total_events_list, energy_threshold, output_low_energy_limit, output_high_energy_limit)
    PrintOutput(sim_file, direction, time, count_rate_df, hit_distribution_df)
#====================


