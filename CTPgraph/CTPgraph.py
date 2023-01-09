from bokeh.embed import json_item
import numpy as np
import pandas as pd
import holoviews as hv
from holoviews import opts
import xarray as xr
import json
import io
import sys
hv.extension('bokeh')
sys.path.append('../utils')

axial_base_data = pd.read_csv("https://storage.googleapis.com/shiplocationdata/axial_base_2015-01-01_2022-01-01.csv")
oregon_offshore_data = pd.read_csv("https://storage.googleapis.com/shiplocationdata/oregon_offshore_2015-01-01_2022-01-01.csv")
oregon_shelf_data = pd.read_csv("https://storage.googleapis.com/shiplocationdata/oregon_shelf_2015-01-01_2022-01-01.csv")
oregon_slope_data = pd.read_csv("https://storage.googleapis.com/shiplocationdata/oregon_slope_2015-01-01_2022-01-01.csv")


def generateCTPgraph(startDate, endDate, location):
    if location == 'axial_base':
        data = axial_base_data
    elif location == 'oregon_offshore':
        data = oregon_offshore_data
    elif location == 'oregon_shelf':
        data = oregon_shelf_data
    elif location == 'oregon_slope':
        data = oregon_slope_data


    locationName = location.replace("_"," ").title()
    #truncates data to date data.
    time = pd.date_range(startDate, endDate)
    #get indexs of the dates in data
    dateColumns = data.columns
    startIndex = dateColumns.get_loc(startDate)
    endIndex = dateColumns.get_loc(endDate)+1
    dateData = data.iloc[:,startIndex:endIndex]
    depth = np.arange(3000)
    ds = xr.Dataset(
        data_vars=dict(
            SoundSpeed=(["depth","time"], dateData)
        ),
        coords=dict(
            time=(["time"], time),
            depth=(["depth"], depth),
        ),
        attrs=dict(description="Sound Data"),
    )
    #holoviews wrapper
    hv_ds = hv.Dataset(ds)[:,:]
    soundspeed = hv_ds.to(hv.Image, kdims=["time","depth"])
    soundPlot = soundspeed.opts(
        opts.Image(
            title=locationName + " Speed of Sound with Depth vs Time",
            width=600, height=500,
            tools=['hover'],

            ylabel='Depth [m]',
            invert_yaxis=True,
            ylim=(0,250),

            xlabel='Date',

            cmap='viridis',
            colorbar=True,
        )
    )
    plot = hv.render(soundPlot)
    return plot

def generateCTDLineGraph(dateTime, location, y = None):
    if location == 'axial_base':
            data = axial_base_data
    elif location == 'oregon_offshore':
        data = oregon_offshore_data
    elif location == 'oregon_shelf':
        data = oregon_shelf_data
    elif location == 'oregon_slope':
        data = oregon_slope_data


    date = pd.to_datetime(dateTime)
    strDate = str(date.date())
    scatterPlot = hv.Scatter(data[strDate], label=f'{strDate}: Speed of Sound [m/s] vs Depth[m]')
    line = scatterPlot.opts(
        opts.Scatter(
            framewise=True,
            width=400, height=450,
            tools=['hover'],
            invert_axes=True,

            ylabel='Speed of Sound [m/s]',
            yaxis='right',
            invert_yaxis=True,
            ylim=(1460, 1520),

            xlabel='Depth',
            xlim=(0,200),
        ),
    )
    plot = hv.render(line)
    return plot

# return CTD left graph
def generateCTP(location, startDate, endDate):
    graph = generateCTPgraph(startDate, endDate, location)
    return json.dumps(json_item(graph))

# return CTD right graph
def generateCTDLine(location, date):
    graph = generateCTDLineGraph(date, location)
    return json.dumps(json_item(graph))


def downloadCtdCsv(location, startDate, endDate):

    if location == 'axial_base':
        data = axial_base_data
    elif location == 'oregon_offshore':
        data = oregon_offshore_data
    elif location == 'oregon_shelf':
        data = oregon_shelf_data
    elif location == 'oregon_slope':
        data = oregon_slope_data

    # result_csv = fetch_google_cloud_bucket_file(fileName)
    # result_csv_s = io.StringIO(result_csv.decode())
    # data = pd.read_csv(result_csv_s)
    dateColumns = data.columns
    startIndex = dateColumns.get_loc(startDate)
    endIndex = dateColumns.get_loc(endDate) + 1
    dateData = data.iloc[:, startIndex:endIndex]
    csv = dateData.to_csv(index=False)
    return csv
