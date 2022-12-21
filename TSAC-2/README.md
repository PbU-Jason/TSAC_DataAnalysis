# README

`python3 RateAnalysis.py <pixel_position> <sim_file> <energy_threshold> <output_energy_lower_cut> <output_energy_higher_cut>`

- `<pixel_position>`
  - PixelPosition.csv
- `<sim_file>`
  - the sim file you want to analyze
- `<energy_threshold>`
  - 15
- `<output_energy_lower_cut>`
  - 50
- `<output_energy_higher_cut>`
  - 300

### Example

```
simy@vela3:/disk1/pbu$ python3 RateAnalysis.py PixelPosition.csv shortGRB_45_120.inc1.id1.sim 15 50 300
/home/simy/.local/lib/python3.8/site-packages/pandas/core/computation/expressions.py:20: UserWarning: Pandas requires version '2.7.3' or newer of 'numexpr' (version '2.7.1' currently installed).
  from pandas.core.computation.check import NUMEXPR_INSTALLED
==================================================
sim file            : shortGRB_45_120.inc1.id1.sim
source direction    : [('45', '120')]
simulation time     : 0.5
energy threshold    : 15
output energy range : (50, 300)
--------------------
count rate          :
          Count Rate
Detector            
1.0          22794.0
2.0           9118.0
3.0          20156.0
4.0          12888.0
5.0           4392.0
--------------------
hit distribution    :
     Number Rate
Hit             
1        67436.0
2         1872.0
3           40.0
==================================================

```

