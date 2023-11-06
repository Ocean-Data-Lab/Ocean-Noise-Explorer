import sys
sys.path.insert(0, './SpecGraph')

from Spectrogram import generateSpectrogram
from Spectrogram import generateSTSpectrogram
from Spectrogram import generateBroadbandSTSpectrogram
from SPDF import generateSPDF
from Octave import generateOctaveGraph

def getInitGraph(startDate, endDate, location, specs):
    return generateSpectrogram(startDate, endDate, location, specs)

def getUpdatedGraph(startDate, endDate, graphType, location, specs, f0=50):
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
