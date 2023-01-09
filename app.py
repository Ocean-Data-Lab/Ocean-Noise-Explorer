from graph import getInitGraph
from graph import getUpdatedGraph
from flask import Flask, request
from flask_cors import CORS, cross_origin
from flask.helpers import send_from_directory
from bokeh.io.export import get_screenshot_as_png
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from ImageToBlob import serve_pil_image
from Spectrogram import generateSpectrogramGraph
from Spectrogram import generateSpectrogramCsvValue
from SPDF import generateCsvSPDF
from Octave import generateOctave
from Octave import generateCsvOctave
import holoviews as hv
import pandas as pd
import xarray as xr
import sys
from gevent.pywsgi import WSGIServer

sys.path.insert(0, './CTPgraph')
sys.path.insert(0, './utils')
sys.path.insert(0, './SpecGraph')
sys.path.insert(0, './WindAndRainGraph')

from CTPgraph import generateCTP
from CTPgraph import generateCTPgraph
from CTPgraph import downloadCtdCsv
from CTPgraph import generateCTDLine
from CTPgraph import generateCTDLineGraph

from WindAndRain import generatingWindSpeedGraph
from WindAndRain import generatingPrecipitationGraph
from WindAndRain import generatingWind
from WindAndRain import generatePrecipitation
from WindAndRain import downloadWindRainCsv


app = Flask(__name__, static_folder="build", static_url_path="")
CORS(app)


fn = 'lf_specs.zarr'
specs = xr.open_dataset(fn)

# ***** GENERATE GRAPH *****
# get CTP graph based on location selected
@app.route('/api/getCTP', methods=['POST'])
@cross_origin()
def getCTP():
    request_data = request.get_json()
    startDate = request_data["startDate"]
    endDate = request_data["endDate"]
    location = request_data['location']

    # fix the input date
    startDate = startDate.split(' ')[0]
    endDate = endDate.split(' ')[0]

    return generateCTP(location, startDate, endDate)

# get CTP graph based on location selected
@app.route('/api/getCTPLine', methods=['POST'])
@cross_origin()
def getCTPLine():
    request_data = request.get_json()
    location = request_data['location']
    date = request_data['date']
    return generateCTDLine(location, date)

@app.route('/api/getInitGraph', methods=['POST'])
@cross_origin()
def getInit():
    request_data = request.get_json()
    startDate = request_data['startDate']
    endDate = request_data['endDate']
    location = request_data['location']
    result = getInitGraph(startDate, endDate, location, specs)
    return result


@app.route('/api/getUpdatedGraph', methods=['POST'])
@cross_origin()
def getUpdate():
    request_data = request.get_json()
    startDate = request_data['startDate']
    endDate = request_data['endDate']
    location = request_data['location']
    graphType = request_data['graphType']
    # for Octave Band only
    f0 = int(request_data['frequency'])
    return getUpdatedGraph(startDate, endDate, graphType, location, specs, f0)

# get wind and rain graph
@app.route('/api/getWindRainGraph', methods=['POST'])
@cross_origin()
def getWindRainGraph():
    request_data = request.get_json()
    graphType = request_data['graphType']
    start_Time = request_data['startDate']
    end_Time = request_data['endDate']
    location = request_data['location']
    # fix the input date
    start_Time['date'] = start_Time['date'].split(' ')[0]
    end_Time['date'] = end_Time['date'].split(' ')[0]

    if graphType == "WindSpeed":
        windSpeedType = request_data['windSpeedType']
        return generatingWindSpeedGraph(start_Time, end_Time, location, windSpeedType)
    else:
        return generatingPrecipitationGraph(start_Time, end_Time, location)

# ***** DOWNLOAD *****
# get png of format blob for download
@app.route('/api/downloadPng', methods=['POST'])
@cross_origin()
def downloadPNG():
    options = Options()
    options.headless = True
    driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
    ctdRightDate=''
    with app.app_context():
        request_data = request.get_json()
        startDate = request_data['startDate']
        endDate = request_data['endDate']
        location = request_data['location']
        graphtype = request_data['currType']

        ctdType = request_data['ctdType']
        if 'ctdRightDate' in request_data:
            ctdRightDate = request_data['ctdRightDate']

        if location == "oregon_offshore" or location == "oregon_shelf":
            graphType = request_data['meteGrahphType']
            if graphType == 'WindSpeed':
                plot = generatingWind(startDate, endDate, location, graphType)
            else:
                plot = generatePrecipitation(startDate, endDate, location)
        elif graphtype == 'Spectrogram':
            plot = generateSpectrogramGraph(startDate, endDate, location, specs)
        elif graphtype == "Octave Band":
            frequency = request_data['frequency']
            plot = generateOctave(location, startDate, endDate, frequency, specs)
        else:
            if(ctdType == 'left'):
                plot = generateCTPgraph(startDate, endDate, location)
            else:
                plot = generateCTDLineGraph(ctdRightDate, location)

        image = get_screenshot_as_png(plot, width=900, height=400, driver=driver)
        return serve_pil_image(image)

@app.route('/api/downloads', methods=['POST'])
@cross_origin()
def download():
    # with app.app_context():
        request_data = request.get_json()
        startDate = request_data['startDate']
        endDate = request_data['endDate']
        location = request_data['location']
        # ********** download wind rain csv **********
        if location == "oregon_offshore" or location == "oregon_shelf":
            graphType = request_data['meteGrahphType']
            return downloadWindRainCsv(startDate, endDate, location, graphType)
        starttime = pd.Timestamp(startDate)
        endtime = pd.Timestamp(endDate)
        # ********** downloadCTD csv **********
        if request_data['selectedValue'] == 'CTD':
            return downloadCtdCsv(location, startDate, endDate)

        type = request_data['currType']
        frequency = request_data['frequency']
        slice_data = specs[location].loc[starttime:endtime, :]
        if type == 'Spectrogram':
            return generateSpectrogramCsvValue(slice_data, location)
        elif type == 'Octave Band':
            return generateCsvOctave(slice_data, location, frequency)
        else:
            return generateCsvSPDF(slice_data)


# ***** RENDER *****
# render front-end build
@app.route('/')
@cross_origin()
def serve():
    return send_from_directory(app.static_folder, 'index.html')

if __name__ == '__main__':
    app.run()
    # http_server = WSGIServer(('', 8000), app)
    # http_server.serve_forever()
