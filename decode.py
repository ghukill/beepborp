# """
# Decode audio file
# """

# import numpy as np
# from scipy.io import wavfile
# from scipy.signal import find_peaks, peak_widths

# from scipy.fftpack import fft, fftshift

# def signal_power_spectrum(signal, sample_rate):
#     window = np.hanning(len(signal))
#     spectrum = np.abs(fftshift(fft(signal*window)))**2
#     freqs = np.linspace(-sample_rate/2, sample_rate/2, len(signal))
#     return freqs, spectrum

# def decode(filename):

#     # Load WAV file
#     sample_rate, signal = wavfile.read(filename)

#     # Compute the power spectrum of the signal
#     freqs, spectrum = signal_power_spectrum(signal, sample_rate)

#     # Find the peaks in the spectrum
#     peaks, _ = find_peaks(spectrum, height=np.max(spectrum)/2)

#     # Compute the widths of the peaks
#     widths, _, _, _ = peak_widths(spectrum, peaks)

#     # Compute the center frequencies of the peaks
#     center_frequencies = freqs[peaks]

#     # Find the indices of the zero-crossings in the signal
#     zero_crossings = np.where(np.diff(np.sign(signal)))[0]

#     # Split the signal into segments based on the zero-crossings
#     segments = np.split(signal, zero_crossings[1:])

#     # For each segment, compute the power spectrum and find the peak frequency
#     for segment in segments:
#         if len(segment) > 0:
#             # Compute the power spectrum of the segment
#             seg_freqs, seg_spectrum = signal_power_spectrum(segment, sample_rate)
            
#             # Find the peaks in the spectrum
#             seg_peaks, _ = find_peaks(seg_spectrum, height=np.max(seg_spectrum)/2)
            
#             # Compute the widths of the peaks
#             seg_widths, _, _, _ = peak_widths(seg_spectrum, seg_peaks)
            
#             # Compute the center frequencies of the peaks
#             seg_center_frequencies = seg_freqs[seg_peaks]
            
#             # Find the peak frequency with the widest width
#             max_width_idx = np.argmax(seg_widths)
#             peak_frequency = seg_center_frequencies[max_width_idx]
            
#             # Print the peak frequency
#             print(f"Peak frequency: {peak_frequency}")

def na_from_wav(filename):

    import numpy as np
    from wave import open as open_wave

    waveFile = open_wave(filename,'rb')
    nframes = waveFile.getnframes()
    wavFrames = waveFile.readframes(nframes)
    ys = numpy.fromstring(wavFrames, dtype=numpy.int16)
    return ys