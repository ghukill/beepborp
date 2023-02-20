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

def find_closest_key_value(dictionary, input_key):
    closest_key = min(dictionary.keys(), key=lambda x: abs(x - input_key))
    closest_value = dictionary[closest_key]
    if abs(closest_key - input_key) > 500:
        return ""
    else:
        return closest_value
