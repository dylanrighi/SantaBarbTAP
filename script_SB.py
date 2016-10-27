"""
Script to run GNOME for the SantaBarbara BOEM project

created 
"""
import os
from datetime import datetime, timedelta

import numpy
np = numpy

from gnome import scripting
from gnome.basic_types import datetime_value_2d

from gnome.utilities.remote_data import get_datafile

from gnome.model import Model

from gnome.map import MapFromBNA
from gnome.environment import Wind, Tide
from gnome.spill import point_line_release_spill
from gnome.movers import RandomMover, GridCurrentMover, GridWindMover, IceMover, IceWindMover

from gnome.outputters import Renderer
from gnome.outputters import NetCDFOutput

# define base directory
#base_dir = os.path.dirname(__file__)
# my laptop basedir
# base_dir = 'C:\Users\glen.watabayashi\pygnomeTAP'
base_dir = "C:\Users\dylan.righi\Science\SantaBarbTAP"
# Gonzo
#base_dir = '/data/dylan/SantaBarb/'


def make_model(images_dir=os.path.join(base_dir, 'images')):
    print 'initializing the model'

    # start_time = datetime(1985, 7, 1, 13, 30)
    start_time = datetime(1985, 1, 2, 0, 0)

    # model time-step in seconds
    model = Model(start_time=start_time,
                  duration=timedelta(hours = 3*24 + 23),
                  time_step=15 * 60,             
                  uncertain=False)

    print 'adding the map'
    mapfile = get_datafile(os.path.join(base_dir,'coast_SBbig.bna'))
    model.map = MapFromBNA(mapfile, refloat_halflife=6)  # hours

    print 'adding outputters'
    renderer = Renderer(mapfile, images_dir, size=(800, 600))
    renderer.viewport = ((-122, 33), (-117, 35))
    model.outputters += renderer

    netcdf_file = os.path.join(base_dir, 'script_SB')
    scripting.remove_netcdf(netcdf_file)

    model.outputters += NetCDFOutput(netcdf_file, which_data='all')

    print 'adding a spill'
    end_time = start_time + timedelta(hours=24)
    spill = point_line_release_spill(num_elements=1000,
                                     start_position=(202.294666,
                                                     71.922333, 0.0),
                                     release_time=start_time,
                                     end_release_time=end_time)
    model.spills += spill

    print 'adding a RandomMover:'
    model.movers += RandomMover(diffusion_coef=50000)

    print 'adding a current mover:'
    # currents from ROMS Santa Barbara run, provided by UCLA
    curr_file = os.path.join(base_dir, 'BOEM', 'Currentfilelist.txt')
    print curr_file
    topology_file = os.path.join(base_dir, 'TopologyCurrent.DAT')
    model.movers += GridCurrentMover(curr_file, topology_file)
    # model.movers += GridCurrentMover(curr_file)


    print 'adding a wind mover:'
    # winds from the ROMS Arctic run, provided by Walter Johnson
    wind_file = os.path.join(base_dir, 'BOEM', 'Windfilelist.txt')
    print wind_file
    topology_file = os.path.join(base_dir, 'TopologyCurrent.DAT')
    model.movers += GridWindMover(wind_file, topology_file)
    # model.movers += GridWindMover(wind_file, topology_file)

  #  print 'adding an ice mover:'
  #  ice from the ROMS Arctic run, provided by Walter Johnson
  #  ice_file = os.path.join(base_dir, 'data_gnome', 'ROMS_h2ouv', 'arctic_filelist.txt')
  #  topology_file = os.path.join(base_dir, 'data_gnome', 'arctic_subset_newtopo2.DAT')
  #  model.movers += IceMover(ice_file, topology_file)
  #  model.movers += IceMover(ice_file)
  #  print ice_file

   
    return model

if __name__ == "__main__":
    scripting.make_images_dir()

    model = make_model()
    #model.duration = timedelta(hours=24*30)
    # model.full_run(log=True)
    model.full_run()
    for sc in model.spills.items():
        print "sc:", sc
