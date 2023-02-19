"""

"""

import os
import string
import sys
import warnings

import numpy as np
from ptttl.audio import ptttl_to_wav
import simpleaudio as sa

warnings.simplefilter("ignore", DeprecationWarning)

INPUTFILE="bach.ptttl"
OUTPUTFILE="output.wav"


def read_ptttl(filename):
    with open(filename, 'r') as fh:
        return fh.read()

def play_test():
    return play_string(read_ptttl(INPUTFILE))

def play_ptttl(filename):
    play_string(read_ptttl(filename))

def play_string(s):
    ptttl_to_wav(s, OUTPUTFILE)
    wave_obj = sa.WaveObject.from_wave_file(OUTPUTFILE)
    play_obj = wave_obj.play()
    play_obj.wait_done()

def record_string(s, filename=OUTPUTFILE):
    ptttl_str = phrase_to_ptttl(s)
    ptttl_to_wav(ptttl_str, filename)
    return filename

def phrase_to_ptttl(phrase, speed=8):

    h = {
        "a":"c3",
        "b":"d3",
        "c":"e3",
        "d":"f3",
        "e":"g3",
        "f":"a3",
        "g":"b3",
        "h":"c4",
        "i":"d4",
        "j":"e4",
        "k":"f4",
        "l":"g4",
        "m":"a4",
        "n":"b4",
        "o":"c5",
        "p":"d5",
        "q":"e5",
        "r":"f5",
        "s":"g5",
        "t":"a5",
        "u":"b5",
        "v":"c6",
        "w":"d6",
        "x":"e6",
        "y":"f6",
        "z":"g6"
    }
    
    melody_notes = []
    for char in phrase:
        melody_notes.append(h.get(char.lower().strip(), "p"))
    melody = ",".join(melody_notes)
    
    return f"""{phrase}:
b=123, d={speed}, o=1:

{melody}
"""

def array_from_wav(filename):

    from wave import open as open_wave

    waveFile = open_wave(filename,'rb')
    nframes = waveFile.getnframes()
    wavFrames = waveFile.readframes(nframes)
    ys = np.fromstring(wavFrames, dtype=np.int16)
    return ys

def peak_count_in_tone(a):
    """
    identify tones by 0 markers
    count peaks in tone
    """

    # get zeros
    zeros = np.where(a==0)

    # # get tones by finding length of tone
    # # NOTE: needs improvment, somtimes leading noise
    # for i in range(len(zeros[0])):
    #     if zeros[0][i+1] - zeros[0][i] > 100:
    #         tone_len = zeros[0][i+1]
    #         break
    tone_len = 10755 # DEBUG based on output defaults, this works better
    tone_count = round((len(a) / tone_len))
    tones = np.array_split(a, tone_count)
    
    # TODO: improve with scipy peak counting
    # https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.find_peaks.html
    peak_counts = []
    for tone in tones:
        prev = tone[0] or 0.001
        threshold = 0.5
        peaks = []
        for num, i in enumerate(tone[1:], 1):
            if (i - prev) / prev > threshold:
                peaks.append(num)
            prev = i or 0.001
        peak_counts.append(len(peaks))

    return peak_counts

def decode_wav(filename):
    
    a = array_from_wav(filename)
    peaks = peak_count_in_tone(a)
    alpha_peaks = [
        130,
        146,
        164,
        173,
        195,
        219,
        243,
        257,
        290,
        323,
        343,
        383,
        433,
        478,
        507,
        568,
        633,
        671,
        746,
        832,
        923,
        973,
        1082,
        1182,
        1253,
        1372]
    h = dict(zip(alpha_peaks, string.ascii_lowercase))
    h[0] = " " # spaces for all non ascii chars
    decoded_phrase = ''.join([h.get(c, '') for c in peaks])
    return peaks, decoded_phrase

def play_and_decode_phrase(phrase, speed=16):
    TEMPFILE = 'temp.wav'
    ptttl_str = phrase_to_ptttl(phrase, speed=speed)
    play_string(ptttl_str)
    peaks, decoded_phrase = decode_wav(record_string(phrase, filename=TEMPFILE))
    os.remove(TEMPFILE)
    return peaks, decoded_phrase


if __name__ == "__main__":
    results = play_and_decode_phrase(sys.argv[1], speed=32)
    print(results[1])
