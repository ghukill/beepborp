import matplotlib.pyplot as plt
import numpy as np
from scipy import signal

def isolate_sine_wave_beeps(audio_data, lowcut, highcut):
    # apply a bandpass filter
    nyquist = 0.5 * 44100 # hardcode 44.1khz
    low = lowcut / nyquist
    high = highcut / nyquist
    b, a = signal.butter(5, [low, high], btype='band')
    filtered_data = signal.filtfilt(b, a, audio_data)
    
    return filtered_data

def find_closest_key_value(input_key):
    d = {
        1000: ' ',
        336: 'a',
        299: 'b',
        266: 'c',
        252: 'd',
        224: 'e',
        200: 'f',
        178: 'g',
        168: 'h',
        150: 'i',
        134: 'j',
        126: 'k',
        112: 'l',
        100: 'm',
        89: 'n',
        84: 'o',
        75: 'p',
        67: 'q',
        63: 'r',
        56: 's',
        50: 't',
        45: 'u',
        42: 'v',
        38: 'w',
        33: 'x',
        32: 'y',
        28: 'z',
     }
    closest_key = min(d.keys(), key=lambda x: abs(x - input_key))
    closest_value = d[closest_key]
    if abs(closest_key - input_key) > 500:
        return " "
    else:
        return closest_value

def plot_peaks(a, prominence=1):
    plt.close()
    plt.plot(a)
    peaks, _ = signal.find_peaks(a, prominence=prominence)
    plt.plot(peaks, a[peaks], "x")
    plt.show()

def clean_tone(tone):
    order = 5
    fs = 1000.0  # Sample rate, in Hz
    cutoff = 50.0  # Cutoff frequency of the filter, in Hz

    # Define the filter
    nyquist = 0.5 * fs
    normal_cutoff = cutoff / nyquist
    b, a = signal.butter(order, normal_cutoff, btype='low', analog=False)

    # Apply the filter to the dirty signal
    clean_signal = signal.filtfilt(b, a, tone)
    return clean_signal