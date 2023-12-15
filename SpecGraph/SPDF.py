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


# ***** generate graph *****
def generateSPDF(startDate, endDate, location, specs, sensorType):
    starttime = pd.Timestamp(startDate)
    endtime = pd.Timestamp(endDate)
    base_data = specs[location]
    spec_slice = base_data.loc[starttime:endtime, :]
    spdf = get_spdf(spec_slice, sensorType, fs_hz=200)
    return plot_spdf(spdf, sensorType, log=False)


def get_spdf(spec, sensorType, fs_hz,  fmax=None, spl_bins=np.linspace(0, 120, 481),
             percentiles=[1, 5, 10, 50, 90, 95, 99]):
    if fmax is None:
        fmax = spec.frequency[-1]
    
    if sensorType == 'OBS':
        spl_bins = np.linspace(-400, -200, 481)

    n_freq_bin = int(len(spec.frequency) * fmax/(fs_hz/2)) + 1

    spdf_dct = {'freq': np.array(np.linspace(0, fmax, n_freq_bin)),
                'spl': spl_bins[:-1],
                'pdf': np.empty((n_freq_bin, 480)),
                'number_psd': len(spec.time)}

    for p in percentiles:
        spdf_dct[str(p)] = np.empty(n_freq_bin)

    for idx, freq_bin in enumerate(tqdm(spec.values.transpose()[:n_freq_bin - 1])):
        hist, _ = np.histogram(freq_bin, bins=spl_bins, density=True)
        spdf_dct['pdf'][idx] = hist
        spdf_dct['50'][idx] = np.median(freq_bin)
        for p in percentiles:
            spdf_dct[str(p)][idx] = np.nanquantile(freq_bin, p/100)

    return spdf_dct


def plot_spdf(spdf, sensorType, vmin=0.003, vmax=0.2, vdelta=0.0025, save=False, filename=None, log=True, title='Spectral PDF'):
    cbarticks = np.arange(vmin, vmax+vdelta, vdelta)
    fig, ax = plt.subplots(figsize=(9, 5))
    im = ax.contourf(spdf['freq'], spdf['spl'], np.transpose(spdf['pdf']),
                     cbarticks, norm=colors.Normalize(vmin=vmin, vmax=vmax),
                     cmap='jet', extend='max', alpha=0.50, linewidth=0)
    print(im)

    # plot some percentiles:
    plt.plot(spdf['freq'], spdf['1'], color='black')
    plt.plot(spdf['freq'], spdf['5'], color='black')
    plt.plot(spdf['freq'], spdf['10'], color='black')
    plt.plot(spdf['freq'], spdf['50'], color='black')
    plt.plot(spdf['freq'], spdf['90'], color='black')
    plt.plot(spdf['freq'], spdf['95'], color='black')
    plt.plot(spdf['freq'], spdf['99'], color='black')

    plt.ylabel(r'spectral level (dB rel $1 \mathrm{\frac{μ Pa^2}{Hz}}$)')
    plt.xlabel('frequency (Hz)')
    if sensorType == "OBS":
        plt.ylim([-400,-200])
    else:
        plt.ylim([36, 100])
        
    plt.xlim([0, 90])
    if log:
        plt.xscale('log')

    plt.colorbar(im, ax=ax, ticks=[vmin, vmin + (vmax-vmin)/4, vmin + (vmax-vmin)/2,
                 vmin + 3*(vmax-vmin)/4,  vmax],  pad=0.03, label='probability', format='%.3f')
    plt.tick_params(axis='y')
    plt.grid(True)
    plt.title(title)
    handles, labels = plt.gca().get_legend_handles_labels()
    line = Line2D(
        [0], [0], label='percentiles: 1, 5, 10, 50, 90, 95, 99', color='k')
    handles.extend([line])
    plt.legend(handles=handles, loc='upper right')
    plt.tight_layout()
    plt.xlim((200/512, 100))
    my_stringIObytes = io.BytesIO()
    plt.savefig(my_stringIObytes, format='jpg')
    my_stringIObytes.seek(0)
    img_base64 = base64.b64encode(my_stringIObytes.read())
    return jsonify({'image': str(img_base64)})

# ***** get download *****
def generateCsvSPDF(spec_slice):
    spdf = get_spdf(spec_slice, fs_hz=200)
    freq = spdf['freq']
    L1 = spdf['1']
    L5 = spdf['5']
    L10 = spdf['10']
    L50 = spdf['50']
    L90 = spdf['90']
    L95 = spdf['95']
    L99 = spdf['99']
    spdf_df = pd.DataFrame(zip(freq, L1, L5, L10, L50, L90, L95, L99), columns=[
                           'Frequency', 'Level 1', 'Level 5', 'Level 10', 'Level 50', 'Level 90', 'Level 95', 'Level 99'])
    csv = spdf_df.to_csv(index=False)
    return csv

    # spdf_df = spdf_df.fillna(0)
    # spdf_dict = spdf_df.to_dict('records')
    # return jsonify({"data": spdf_dict})
