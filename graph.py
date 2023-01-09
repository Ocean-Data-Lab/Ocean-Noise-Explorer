import sys
sys.path.insert(0, './SpecGraph')

from Spectrogram import generateSpectrogram
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
