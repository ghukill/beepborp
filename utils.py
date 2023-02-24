import matplotlib.pyplot as plt
from scipy import signal


def find_closest_key_value(fft_idx):
    d = {
        22: ' ',
        31: 'a',
        35: 'b',
        40: 'c',
        42: 'd',
        47: 'e',
        53: 'f',
        60: 'g',
        63: 'h',
        71: 'i',
        80: 'j',
        85: 'k',
        95: 'l',
        107: 'm',
        120: 'n',
        127: 'o',
        143: 'p',
        160: 'q',
        170: 'r',
        191: 's',
        214: 't',
        240: 'u',
        255: 'v',
        286: 'w',
        321: 'x',
        340: 'y',
        382: 'z'
    }
    closest_key = min(d.keys(), key=lambda x: abs(x - fft_idx))
    closest_value = d[closest_key]
    if abs(closest_key - fft_idx) > 500:
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
