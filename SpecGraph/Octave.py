import matplotlib
import zipfile
import numpy as np
import pandas as pd
import hvplot.xarray
from tqdm import tqdm
import holoviews as hv
import xarray as xr
from bokeh.embed import json_item
from bokeh.plotting import figure
import json
from matplotlib import pyplot as plt
from io import BytesIO
import io
from matplotlib.backends.backend_agg import FigureCanvasAgg
import base64
from flask import send_file, jsonify
import hvplot.pandas
from holoviews import opts
from matplotlib.colors import Normalize
import matplotlib.colors as colors
from matplotlib.lines import Line2D

matplotlib.use('Agg')

import sys
sys.path.insert(0, './utils')
from GetBoxPlotData import median
from GetBoxPlotData import firstQuartile
from GetBoxPlotData import thirdQuartile
from GetBoxPlotData import getLowerBound
from GetBoxPlotData import getUpperBound


# ***** generate graph *****
def get_freq_band(f0, spec):
    f_lo = f0/(2**(1/6))
    f_hi = f0*(2**(1/6))
    spec_band = spec.loc[:, f_lo:f_hi]
    spec_band_lin = 10**(spec_band/10)
    spec_band_lin_mean = spec_band_lin.median('frequency')
    spec_band_mean = 10*np.log10(spec_band_lin_mean)
    return spec_band_mean


def generateDfForOctaveBox(f0, slice_data, location):
    octave_band_f0 = get_freq_band(f0, slice_data)
    octave_f0_value = octave_band_f0.values.tolist()
    octave_band_f0_time = octave_band_f0.coords['time'].values
    dates_lst = [str(x.astype('datetime64[D]')) for x in octave_band_f0_time]
    ovtave_dataframe = pd.DataFrame(
        {location: octave_f0_value, 'date': dates_lst}, columns=[location, 'date'])
    return ovtave_dataframe


def generateOctave(location, startDate, endDate, f0, specs):
    starttime = pd.Timestamp(startDate)
    endtime = pd.Timestamp(endDate)
    slice_data = specs[location].loc[starttime:endtime,:]
    df_octave = generateDfForOctaveBox(f0, slice_data, location)
    boxplot = df_octave.hvplot.box(y=location, by='date', ylabel=location,
                                   width=1000, height=500, legend=False, outlier_color='white')
    boxplot.opts(title="Octave Band", xrotation=90)
    plot = hv.render(boxplot)
    return plot


def generateOctaveGraph(location, startDate, endDate, f0, specs):
    plot = generateOctave(location, startDate, endDate, f0, specs)
    jso = json.dumps(json_item(plot))
    return jso

# ***** get download *****
def generateCsvOctave(slice_data, location, f0=50):
    df_octave = generateDfForOctaveBox(f0, slice_data, location)
    temp = df_octave.groupby('date').apply(lambda x: pd.Series({
        'median': median(x, location),
        'firstQuartile': firstQuartile(x, location),
        'thirdQuartile': thirdQuartile(x, location),
        'min': getLowerBound(x, location),
        'max': getUpperBound(x, location)
    }))
    csv = temp.to_csv(index=False)
    return csv

    # temp = temp.reset_index()


    # temp = temp.to_dict('records')
    # return jsonify({"data": temp})
