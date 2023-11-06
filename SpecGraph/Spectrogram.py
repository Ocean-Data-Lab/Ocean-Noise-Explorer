import matplotlib
import pandas as pd
import hvplot.xarray
import holoviews as hv
import ooipy
import datetime
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

def generateSTSpectrogramGraph(startDate, endDate, location, overlap, nperseg, avg_time):
    print(startDate)
    print(type(startDate))
    start = pd.Timestamp(startDate)
    print(start)
    print(type(start))
    start_time = start.to_pydatetime()
    print(start_time)
    print(type(start_time))
    end = pd.Timestamp(endDate)
    end_time = end.to_pydatetime()
    print(location)
    node_t =location.title()
    print(node_t)
    node = node_t.replace(" ","_")
    print(node)
    hdata_lf = ooipy.get_acoustic_data_LF(start_time, end_time, node)
    print(hdata_lf)
    print(avg_time)
    print(type(avg_time))
    print(nperseg)
    print(type(nperseg))
    print(overlap)
    print(type(overlap))
    spec = hdata_lf.compute_spectrogram(avg_time=int(avg_time),L=int(nperseg),overlap=int(overlap)/100)
    print(spec)
    graph = spec.hvplot(x='time', y='frequency', rasterize=True, cmap='jet', width=1000, height=500)
    print(graph)
    plot = hv.render(graph)
    return plot

def generateSTSpectrogram(startDate, endDate, location, overlap, nperseg, avg_time):
    plot = generateSTSpectrogramGraph(startDate, endDate, location, overlap, nperseg, avg_time)
    jso = json.dumps(json_item(plot))
    return jso

def generateBroadbandSTSpectrogramGraph(startDate, endDate, location, locType, overlap, nperseg, avg_time):
    print(startDate)
    print(type(startDate))
    start = pd.Timestamp(startDate)
    print(start)
    print(type(start))
    start_time = start.to_pydatetime()
    print(start_time)
    print(type(start_time))
    end = pd.Timestamp(endDate)
    end_time = end.to_pydatetime()
    print(location)
    node_t =location.title()
    print(node_t)
    node = "error case"
    if node_t == 'Oregon_Shelf' or node_t == 'Oregon_Offshore' or node_t == 'Oregon Shelf' or node_t == 'Oregon Offshore' :
        node_temp = node_t.replace(" ","_")
        node = node_temp + '_Base_Seafloor'
    elif node_t == 'Axial Base' or node_t == 'Axial_Base':
        node_temp = node_t.replace(" ","_")
        node = node_temp + "_" + str(locType)
    elif node_t == 'Oregon Slope' or node_t == 'Slope Base' or node_t == 'Oregon_Slope' or node_t == 'Slope_Base':
        node_temp = 'Oregon_Slope_Base'
        node = node_temp + "_" + str(locType)
    #node = node_t.replace(" ","_")

    #print(node)
    hdata = ooipy.get_acoustic_data(start_time, end_time, node)
    print(hdata)
    print(avg_time)
    print(type(avg_time))
    print(nperseg)
    print(type(nperseg))
    print(overlap)
    print(type(overlap))
    spec = hdata.compute_spectrogram(avg_time=int(avg_time),L=int(nperseg),overlap=int(overlap)/100)
    print(spec)
    graph = spec.hvplot(x='time', y='frequency', rasterize=True, cmap='jet', clim = (20,70), width=1000, height=500)
    print(graph)
    plot = hv.render(graph)
    return plot

def generateBroadbandSTSpectrogram(startDate, endDate, location, locType, overlap, nperseg, avg_time):
    plot = generateBroadbandSTSpectrogramGraph(startDate, endDate, location, locType, overlap, nperseg, avg_time)
    jso = json.dumps(json_item(plot))
    return jso

def generateSpectrogramCsvValue(slice_data, location):
    slice_frame = slice_data.to_dataframe()
    slice_frame = slice_frame.reset_index()
    csv = slice_frame.to_csv(index=False)
    return csv
