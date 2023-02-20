"""

"""

import os
import string
import sys
import time
import warnings

import numpy as np
from ptttl.audio import ptttl_to_wav
from scipy.signal import find_peaks
import simpleaudio as sa

from scratch import isolate_sine_wave_beeps, find_closest_key_value

warnings.simplefilter("ignore", DeprecationWarning)

INPUTFILE="bach.ptttl"
OUTPUTFILE="output.wav"
DEFAULT_SPEED=32
FP_PROM=1


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

def record_string(s, filename=OUTPUTFILE, speed=DEFAULT_SPEED):
    ptttl_str = phrase_to_ptttl(s, speed=speed)
    ptttl_to_wav(ptttl_str, filename)
    return filename

def phrase_to_ptttl(phrase, speed=DEFAULT_SPEED):

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

    # # NOTE: testing signal cleanup
    # a = isolate_sine_wave_beeps(a, 100, 1000)

    # get zeros
    zeros = np.where(a==0)

    tone_len = 10755 # NOTE: hardcodes len to 44.1khz @ 8 beats @ 123 bpm
    tone_count = round((len(a) / tone_len))
    tones = np.array_split(a, tone_count)

    # count peaks via scipy
    peak_counts = []
    for tone in tones:
        # peak_counts.append(len(find_peaks(tone)[0]))
        peak_counts.append(len(find_peaks(tone, prominence=FP_PROM)[0]))

    return peak_counts

def decode_wav(filename):
    t0 = time.time()
    a = array_from_wav(filename)
    peaks = peak_count_in_tone(a)
    alpha_peaks = [
        32,
        36,
        41,
        43,
        48,
        54,
        61,
        64,
        72,
        81,
        86,
        96,
        108,
        121,
        128,
        144,
        161,
        171,
        192,
        215,
        241,
        256,
        287,
        322,
        341,
        383
    ]
    h = dict(zip(alpha_peaks, string.ascii_lowercase))
    h[0] = " " # spaces for all non ascii chars
    # decoded_phrase = ''.join([h.get(c, '') for c in peaks])
    decoded_phrase = ''.join([find_closest_key_value(h, c) for c in peaks])
    print(f"decode elapsed: {time.time()-t0}")
    return peaks, decoded_phrase

def play_and_decode_phrase(phrase, speed=DEFAULT_SPEED):
    TEMPFILE = 'temp.wav'
    ptttl_str = phrase_to_ptttl(phrase, speed=speed)
    play_string(ptttl_str)
    peaks, decoded_phrase = decode_wav(record_string(phrase, filename=TEMPFILE, speed=8))
    # os.remove(TEMPFILE)
    return peaks, decoded_phrase


if __name__ == "__main__":
    try:
        if len(sys.argv) == 3:
            speed = sys.argv[2]
        else:
            speed = 32
        results = play_and_decode_phrase(sys.argv[1], speed=speed)
        print(results[1])
    except Exception as e:
        print(str(e))
