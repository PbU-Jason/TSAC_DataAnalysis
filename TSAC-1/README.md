# README

### Run

###### before running the code, please make sure upgrade the pandas & numexpr to latest version!

`python3 simAnalysis_tsac1.py <pixel_position> <sim_file> <output_energy_lower_cut> <output_energy_higher_cut> <anti_coincidence_mode>`

- `<pixel_position>`
  - TSAC-1_PixelPosition.csv
- `<sim_file>`
  - the sim file you want to analyze
- `<output_energy_lower_cut>`
  - the lower output energy you interested in
- `<output_energy_higher_cut>`
  - the higher output energy you interested in
- `<anti_coincidence_mode>`
  - `True` for turn on; `False` for turn off

### Output Example

```
simy@crab6:/disk1/dog/TSAC_1/src_Crab/jason_py$ nohup python3 simAnalysis_tsac1.py TSAC-1_PixelPosition.csv 
 
 ======================================================================
 sim file                      : Crab_pol_10ks_rotate_45.inc1.id1.sim
 source direction (theta, phi) : [('45', '0')]
 simulation time               : 10000.0
 energy threshold for GAGG     : 15
 energy threshold for BGO      : 20
 output energy range           : (160.0, 250.0)
 anti-coincidence mode         : ON
 events excluded by ACS        : 2244
 --------------------------------------------------
 detector 1 : upper GAGG
 detector 2 : lower GAGG
 (detector 3 : anti-coincidence shield made by BGO)
 --------------------------------------------------
 count rate :
 # consider energy threshold
 # consider output energy range for each detector
           Number Rate
 Detector
 1.0            0.5334
 2.0            0.1071
 --------------------------------------------------
 hit rate :
 # only consider energy threshold
      Number Rate
 Hit
 1         8.9079
 2         0.2100
 3         0.0107
 4         0.0014
 5         0.0001
 --------------------------------------------------
 hit distribution :
 # consider energy threshold
 # consider output energy range for all detectors (reconstruct event!)
               Number
 Detector Hit
 1        1      4835
          2       409
          3         2
          4         1
 12       2        82
          3         6
 2        1       865
          2        75
          3         2
 ======================================================================
```

