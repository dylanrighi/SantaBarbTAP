"""
TAP Setup.py

Master set up script for a TAP run

All the data required to set up and build TAP cubes + site.txt file should be in here

"""

import os, sys, datetime
import numpy as np
import netCDF4 as nc4

RootDir =  os.path.split(__file__)[0]
print "Loading TAP Setup data from:", RootDir

## Cube Builder Data
ReceptorType = "Grid" # should be either "Grid" or "Polygons" (only grid is supported at the moment)
CubeType = "Volume" # should be either "Volume" or "Cumulative"

## CubeDataType options are: 'float32', 'uint16', or 'uint8'
##   float32 gives better precision for lots of LEs
##   uint8 saves disk space -- and is OK for about 1000 LEs
##   uint16 is a mid-point -- probably good to 10,000 LEs or so
CubeDataType = 'float32' 

## Batch GNOME Data:
## You can use multiple machines in parallel to do many runs
NumTrajMachines = 2

# Files with time series records in them used by GNOME
# These are used to compute the possible time files. The format is:
# It is a list of one or more time files. each file is desribed with a tuple:
#  (file name, allowed_gap_length, type)
#    file_name is a string
#    allowed_gap_length is in hours. It indicates how long a gap in the time
#         series records you will allow GNOME to interpolate over.
#    type is a string describing the type of the time series file. Options
#         are: "Wind", "Hyd" for Wind or hydrology type files
# if set to None, model start an end times will be used
#TimeSeries = [("WindData.OSM", datetime.timedelta(hours = 6), "Wind" ),]
TimeSeries = None

# time span of your data set
# BOEM sample data files
DataStartEnd = (datetime.datetime(2004, 1, 1, 1),
                datetime.datetime(2004,7,10,23)
                )


DataGaps = ( )
# Data_Dir = 'C:\Users\dylan.righi\Science\SantaBarbTAP\data_ROMS\\roms_surface'
# fn = os.path.join(Data_Dir,'roms_surface_2004.txt')


Data_Dir = 'C:\Users\dylan.righi\Science\SantaBarbTAP\data_gnome\\roms_gnome'
# Data_Dir = 'C:\Users\dylan.righi\Science\SantaBarbTAP\data_ROMS\\roms_surface'
c_filelist = os.path.join(Data_Dir,'filelist.txt')
c_Topology = os.path.join(Data_Dir,'Topology_1.3.10.DAT')
c_fn = os.path.join(Data_Dir,'roms_surface_2004.txt')

w_Data_Dir = 'C:\Users\dylan.righi\Science\SantaBarbTAP\data_gnome\wrf_gnome'
# w_Data_Dir = 'C:\Users\dylan.righi\Science\SantaBarbTAP\data_ROMS\wrf'
w_filelist = os.path.join(w_Data_Dir,'filelist.txt')
w_Topology = os.path.join(w_Data_Dir,'wrf_topo_1.3.10.DAT')
w_fn = os.path.join(w_Data_Dir,'wrf_2004.txt')



# specification for how you want seasons to be defined:
#  a list of lists:
#  [name, (months) ]
#    name is a string for the season name  
#    months is a tuple of integers indicating which months are in that season
Seasons = [
          ["AllYear", [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]]
          # ["Winter", [12, 1, 2, 3, 4, 5]],
          # ["Summer",  [6, 7, 8, 9, 10, 11 ]], 
          # ["Spring",  [3, 4, 5 ]], 
          # ["Summer",  [6, 7, 8 ]], 
          # ["Faller",  [9, 10, 11]],
          ]              

# You don't need to do anything with this
StartTimeFiles = [(os.path.join(RootDir, s[0]+'Starts.txt'), s[0]) for s in Seasons]

# number of start times you want in each season:
#NumStarts = 5000
NumStarts = 20

# # kludge for iterating runs
# r0= int(sys.argv[2])
# r1= int(sys.argv[3])
# print 'RunLims : ', r0,r1
# RunStarts = range(r0,r1)

RunStarts = range(0,NumStarts)

# section for defining already run Trajectory files for BuildCubes
RunFiles = []


# # Length of release in hours  (0 for instantaneous)
ReleaseLength = 2*24  # in hours

# number of Lagrangian elements you want in the GNOME run
NumLEs = 1000
                            
# we only have "MediumCrude"  in the data for now (see OilWeathering.py)
OilWeatheringType = None
# OilWeatheringType = 'FL_Straits_MediumCrude'  # use None for no weathering -- weathering can be
#                           # post-processed by the TAP viewer for instantaneous
#                           # releases

# name of the GNOME SAV file you want to use
# note: GNOME locks it (for a very brief time when loading) 
# which means you need a separate copy for each
# instance of GNOME you want to run (OR just don't start multiple GNOMES too quickly)
# not using this anymore...
# PyGnome_script = "script_SB"


#If ReceptorType is Grid, you need these, it defines the GRID
class Grid:
	pass
Grid.min_lat = 31.0 # decimal degrees
Grid.max_lat = 36.0
Grid.dlat = 0.1       #  

Grid.min_long = -122.0
Grid.max_long = -116.0
Grid.dlong = 0.1       # 17km wide cells at 70N, 15 at 75N, 23 at 65N

# Grid.num_lat = 45
# Grid.num_long = 90
Grid.num_lat = int(np.ceil(np.abs(Grid.max_lat - Grid.min_lat)/Grid.dlat) + 1)
Grid.num_long = int(np.ceil(np.abs(Grid.max_long - Grid.min_long)/Grid.dlong) + 1)


TrajectoriesPath = "Trajectories_n" + str(NumLEs) # relative to RootDir

CubesPath = "Cubes_n" + str(NumLEs)

CubesRootNames = ["Arc_" for i in StartTimeFiles] # built to match the start time files

CubeStartSitesFilename = os.path.join(RootDir, "SB_sites_test.txt")


# # kludge for iterating runs
r0= int(sys.argv[2])
r1= int(sys.argv[3])
print 'RunSites : ', r0,r1
RunSites = range(r0,r1)


# this code reads the file
CubeStartSites = [x.split("#", 1)[0].strip() for x in open(CubeStartSitesFilename).readlines()]
CubeStartSites = [x for x in CubeStartSites if x]

CubeStartFilter = []   # January

MapName = "BOEM SB TAP"
MapFileName, MapFileType = ("coast_SBbig.bna", "BNA")


days = [1, 3, 5, 7, 10, 14, 20]
OutputTimes = [24*i for i in days] # output times in hours(calculated from days

OutputUserStrings = ["1 day",
                     "3 days",
                     "5 days",
                     "7 days",
                     "10 days",
                     "14 days",
                     "20 days",
#                     "30 days",
#                     "60 days",
#                     "70 days",
#                     "90 days",
#                     "120 days",
#                     "180 days",
                     ]

# this is calculated from the OutputTimes
TrajectoryRunLength = OutputTimes[-1]
# TrajectoryRunLength = 24 * 20

PresetLOCS = ["5 barrels", "10 barrels", "20 barrels"]
PresetSpillAmounts = ["1000 barrels", "100 barrels"]


## TAP Viewer Data (for SITE.TXT file)
##
TAPViewerSource = RootDir # where the TAP view, etc lives.
## setup for the Viewer"
TAPViewerPath = "TapView_n" + str(NumLEs)

