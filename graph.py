import sys
sys.path.insert(0, './SpecGraph')

from Spectrogram import generateSpectrogram
from Spectrogram import generateSTSpectrogram
from Spectrogram import generateBroadbandSTSpectrogram
from SPDF import generateSPDF
from Octave import generateOctaveGraph
import xarray as xr

fn_obs = 'obs_specs.zarr'
specs_obs = xr.open_dataset(fn_obs).sortby('time')



location_mapper = {'axial_base':'AXBA1', 'slope_base':'HYSB1', 
                   'central_caldera':'AXCC1','eastern_caldera':'AXEC2','southern_hydrate': 'HYS14',
                   'axial_ashes':'AXAS1', 'axial_international':'AXID1'}

def getInitGraph(startDate, endDate, location, specs):
    return generateSpectrogram(startDate, endDate, location, specs)

def getUpdatedGraph(startDate, endDate, graphType, hydrophoneType, location, specs, f0=50):
    if hydrophoneType == 'OBS':
        specs = specs_obs
        loc_str = location_mapper[location]
        location = loc_str
        
    if graphType == 'Spectrogram':
        return generateSpectrogram(startDate, endDate, location, specs)
    elif graphType == 'SPDF':
        return generateSPDF(startDate, endDate, location, specs)
    else:
        return generateOctaveGraph(location, startDate, endDate, f0, specs)
    
def getSTUpdatedGraph(startDate, endDate, graphType, location, locType, overlap, nperseg, avg_time):
    if graphType == "ST Spectrogram":
        return generateSTSpectrogram(startDate, endDate, location, overlap, nperseg, avg_time)
    elif graphType == "Broadband":
        return generateBroadbandSTSpectrogram(startDate, endDate, location, locType, overlap, nperseg, avg_time)
