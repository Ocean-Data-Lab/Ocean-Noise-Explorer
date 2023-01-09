import matplotlib
import pandas as pd
import hvplot.xarray
import holoviews as hv
from bokeh.embed import json_item
import json
from flask import jsonify
import hvplot.pandas
import sys
sys.path.insert(0, './utils')
matplotlib.use('Agg')


def generateSpectrogramGraph(startDate, endDate, location, specs):
    starttime = pd.Timestamp(startDate)
    endtime = pd.Timestamp(endDate)
    base_data = specs[location]
    data_chunk = base_data.loc[starttime:endtime, :]
    graph = data_chunk.hvplot(
        x='time', y='frequency', rasterize=True, cmap='jet', width=1000, height=500)
    plot = hv.render(graph)
    return plot

def generateSpectrogram(startDate, endDate, location, specs):
    plot = generateSpectrogramGraph(startDate, endDate, location, specs)
    jso = json.dumps(json_item(plot))
    return jso

def generateSpectrogramCsvValue(slice_data, location):
    slice_frame = slice_data.to_dataframe()
    slice_frame = slice_frame.reset_index()
    csv = slice_frame.to_csv(index=False)
    return csv
