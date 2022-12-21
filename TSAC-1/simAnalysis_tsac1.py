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
#====================

### selection ###
pixel_position_file = sys.argv[1]              # sys.argv[1] is pixel position file
sim_file = sys.argv[2]                         # sys.argv[2] is sim file
output_low_energy_limit = float(sys.argv[3])   # sys.argv[3] is output low energy limit
output_high_energy_limit = float(sys.argv[4])  # sys.argv[4] is output high energy limit
anti_coincidence_mode = sys.argv[5]            # sys.argv[5] is anti-coincidence mode, 'True' or 'False'

# pixel_position_file = 'TSAC-1_PixelPosition.csv'
# sim_file = 'Crab_pol_10ks_rotate_45.inc1.id1.sim'
# output_low_energy_limit = 160
# output_high_energy_limit = 250
# anti_coincidence_mode = 'True'
# # anti_coincidence_mode = 'False'
#====================

### fixed variables ###
energy_threshold_gagg = 15 # kev
energy_threshold_bgo = 20 # kev

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
   
def CountRate_and_HitRate_and_HitDistribution(PixelPositionDF, Time, TotalEventsList, EnergyThresholdGAGG, EnergyThresholdBGO, OutputLowEnergyLimit, OutputHighEnergyLimit):
    event_count = 0
    total_hits_above_energy_threshold_list = []
    anti_coincidence_events = 0 # for anti-coincidence 
    for each_event_list in TotalEventsList:
        event_count += 1
        bgo_flag = 0 # for anti-coincidence 
        total_hits_above_energy_threshold_list_temp = [] # for anti-coincidence 
        for each_event in each_event_list:
            x = format(float(each_event[0]), '.5f')
            y = format(float(each_event[1]), '.5f')
            z = format(float(each_event[2]), '.5f')
            fit_pixel = PixelPositionDF.loc[(PixelPositionDF['X'] == x) & (PixelPositionDF['Y'] == y) & (PixelPositionDF['Z'] == z)]
            if fit_pixel.iat[0, 3] == '3': # '3' is for BGO
                if each_event[3] >= EnergyThresholdBGO:
                    bgo_flag = 1
                    total_hits_above_energy_threshold_list_temp.append([event_count, fit_pixel.iat[0, 3], each_event[3], '1'])
            else:
                if each_event[3] >= EnergyThresholdGAGG:
                    total_hits_above_energy_threshold_list_temp.append([event_count, fit_pixel.iat[0, 3], each_event[3], '1'])
        
        # check anti-coincidence
        if anti_coincidence_mode == 'True':
            if bgo_flag == 0:
                for i in total_hits_above_energy_threshold_list_temp:
                    total_hits_above_energy_threshold_list.append(i)
            else:
                anti_coincidence_events += 1
        elif anti_coincidence_mode == 'False':
            for i in total_hits_above_energy_threshold_list_temp:
                total_hits_above_energy_threshold_list.append(i)
        else:
            print('please select anti-coincidence mode!')
                    
    total_hits_above_energy_threshold_array = np.array(total_hits_above_energy_threshold_list)
    total_hits_above_energy_threshold_df = pd.DataFrame(total_hits_above_energy_threshold_array, columns = ['Event', 'Detector', 'Energy', 'Hit'])   
    total_hits_above_energy_threshold_df = total_hits_above_energy_threshold_df.astype(float)

    combined_hits_above_energy_threshold_df = total_hits_above_energy_threshold_df.groupby(['Event', 'Detector']).agg({'Energy': 'sum', 'Hit': 'count'}).reset_index()
    combined_hits_above_energy_threshold_in_output_energy_df = combined_hits_above_energy_threshold_df[(combined_hits_above_energy_threshold_df['Energy'] >= OutputLowEnergyLimit) & (combined_hits_above_energy_threshold_df['Energy'] <= OutputHighEnergyLimit)]
    
    # consider energy threshold & output energy range for each detector
    count_rate_df = combined_hits_above_energy_threshold_in_output_energy_df.groupby('Detector').size().to_frame('Number Rate')
    count_rate_df['Number Rate'] = count_rate_df['Number Rate'].div(Time)
    
    # only consider energy threshold
    hit_rate_df = combined_hits_above_energy_threshold_df.groupby('Hit').size().to_frame('Number Rate')
    hit_rate_df['Number Rate'] = hit_rate_df['Number Rate'].div(Time)
    
    # consider energy threshold & output energy range for all detector (reconstruct event!)
    combined_hits_above_energy_threshold_change_format_df = combined_hits_above_energy_threshold_df.copy()
    combined_hits_above_energy_threshold_change_format_df['Detector'] = combined_hits_above_energy_threshold_change_format_df['Detector'].astype(int)
    combined_hits_above_energy_threshold_change_format_df['Detector'] = combined_hits_above_energy_threshold_change_format_df['Detector'].astype("string")
    combined_hits_above_energy_threshold_merge_detector_df = combined_hits_above_energy_threshold_change_format_df.groupby('Event').agg({'Detector': 'sum','Energy': 'sum', 'Hit': 'sum'}).reset_index()
    combined_hits_above_energy_threshold_merge_detector_in_output_energy_df = combined_hits_above_energy_threshold_merge_detector_df[(combined_hits_above_energy_threshold_merge_detector_df['Energy'] >= OutputLowEnergyLimit) & (combined_hits_above_energy_threshold_merge_detector_df['Energy'] <= OutputHighEnergyLimit)]
    hit_distribution_df = combined_hits_above_energy_threshold_merge_detector_in_output_energy_df.groupby(['Detector', 'Hit']).size().to_frame('Number')
    
    return anti_coincidence_events, count_rate_df, hit_rate_df, hit_distribution_df, total_hits_above_energy_threshold_df, combined_hits_above_energy_threshold_df

def PrintOutput(SimFile, Direction, Time, AntiCoincidenceEvents, CountRateDF, HitRateDF, HitDistributionDF):
    print('======================================================================')
    print('sim file                      :', SimFile)
    print('source direction (theta, phi) :', Direction)
    print('simulation time               :', float(Time[0]))
    print('energy threshold for GAGG     :', energy_threshold_gagg) 
    print('energy threshold for BGO      :', energy_threshold_bgo) 
    print('output energy range           :', (output_low_energy_limit, output_high_energy_limit))
    if anti_coincidence_mode == 'True':
        print('anti-coincidence mode         : ON')
        print('events excluded by ACS        :', anti_coincidence_events)
    else:
        print('anti-coincidence mode         : OFF')
        print('events excluded by ACS        :', anti_coincidence_events)
    print('--------------------------------------------------')
    print('detector 1 : upper GAGG')
    print('detector 2 : lower GAGG')
    print('(detector 3 : anti-coincidence shield made by BGO)')
    print('--------------------------------------------------')
    print('count rate :')
    print('# consider energy threshold')
    print('# consider output energy range for each detector')
    print(CountRateDF)
    print('--------------------------------------------------')
    print('hit rate :')
    print('# only consider energy threshold')
    print(HitRateDF)
    print('--------------------------------------------------')
    print('hit distribution :')
    print('# consider energy threshold')
    print('# consider output energy range for all detectors (reconstruct event!)')
    print(HitDistributionDF)
    print('======================================================================')
    return
#====================

### main code ###
if __name__ == "__main__":
    pixel_position_df, direction, time, total_events_list = ExtractUsefulInfo(pixel_position_file, sim_file)
    anti_coincidence_events, count_rate_df, hit_rate_df, hit_distribution_df, total_hits_above_energy_threshold_df, combined_hits_above_energy_threshold_df = CountRate_and_HitRate_and_HitDistribution(pixel_position_df, float(time[0]), total_events_list, energy_threshold_gagg, energy_threshold_bgo, output_low_energy_limit, output_high_energy_limit)
    PrintOutput(sim_file, direction, time, anti_coincidence_events, count_rate_df, hit_rate_df, hit_distribution_df)
#====================


