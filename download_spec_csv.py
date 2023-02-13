import xarray as xr
import numpy as np
import pandas as pd
from tqdm import tqdm

fn = 'lf_specs.zarr'
specs = xr.open_dataset(fn)

# ****************************************************************
# This part is used to generate csv for the spectrogram data
# ****************************************************************
def generateSpectrogramCsvValue(slice_data, location):
    slice_frame = slice_data.to_dataframe()
    slice_frame = slice_frame.reset_index()
    csv = slice_frame.to_csv(index=False)
    with open("Spectrogram_" + location + ".csv", "w") as file:
        file.write(csv)

# ****************************************************************
# This part is used to generate csv for the octave band data
# ****************************************************************
def median(df, location):
    return df[location].median()

def firstQuartile(df, location):
    result = df[location].quantile([0.25]).fillna(0)
    return int(result)

def thirdQuartile(df, location):
    result = df[location].quantile([0.75]).fillna(0)
    return int(result)

def getLowerBound(df, location):
    Q1 = df[location].quantile(0.25)
    Q3 = df[location].quantile(0.75)
    IQR = Q3 - Q1
    return Q1 - (1.5 * IQR)

def getUpperBound(df, location):
    Q1 = df[location].quantile(0.25)
    Q3 = df[location].quantile(0.75)
    IQR = Q3 - Q1
    return Q3 + (1.5 * IQR)

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
    octave_dataframe = pd.DataFrame(
        {location: octave_f0_value, 'date': dates_lst}, columns=[location, 'date'])
    return octave_dataframe

def generateCsvOctave(slice_data, location, f0=50):
    df_octave = generateDfForOctaveBox(f0, slice_data, location)
    temp = df_octave.groupby('date').apply(lambda x: pd.Series({
        'median': median(x, location),
        'firstQuartile': firstQuartile(x, location),
        'thirdQuartile': thirdQuartile(x, location),
        'min': getLowerBound(x, location),
        'max': getUpperBound(x, location)
    }))
    temp = temp.reset_index()
    csv = temp.to_csv(index=False)
    with open("Octave_" + location + ".csv", "w") as file:
        file.write(csv)

# ****************************************************************
# This part is used to generate csv for the SPDF  data
# ****************************************************************
def get_spdf(spec, fs_hz, fmax=None, spl_bins=np.linspace(0, 120, 481),
             percentiles=[1, 5, 10, 50, 90, 95, 99]):
    if fmax is None:
        fmax = spec.frequency[-1]

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
    with open("SPDF_" + location + ".csv", "w") as file:
        file.write(csv)


# ******** specify your wanted variables here ********
starttime = "2017-02-01 00"  # 00 is the hours
endtime = "2017-04-18 00"  # 00 is the hours
frequency = 80  # specify only when you are downloading the octave band data
location = "eastern_caldera" # location name, you can select from: "axial_base", "eastern_caldera", "central_ caldera", "slope_base", "southern_hydrate"
slice_data = specs[location].loc[starttime:endtime, :]


# ******** uncomment the following line to download the csv data ********
generateSpectrogramCsvValue(slice_data, location)  # download corresponding sectrogram data
# generateCsvOctave(slice_data, location, frequency) # download corresponding octave data
# generateCsvSPDF(slice_data) # download corresponding SPDF data
