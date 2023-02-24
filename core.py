"""

"""

import sys
import time
import warnings

import numpy as np
from ptttl.audio import ptttl_to_wav
import simpleaudio as sa

from utils import find_closest_key_value

warnings.simplefilter("ignore", DeprecationWarning)

INPUTFILE="bach.ptttl"
OUTPUTFILE="output.wav"
DEFAULT_SPEED=32
FP_PROM=1000


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

def tones_from_array(a):

    tone_len = 10755 # NOTE: hardcodes len to 44.1khz @ 8 beats @ 123 bpm
    tone_count = round((len(a) / tone_len))
    tones = np.array_split(a, tone_count)

    return tones

def decode_wav(filename):
    t0 = time.time()
    a = array_from_wav(filename)
    tones = tones_from_array(a)
    chars = []
    for tone in tones:
        tone_fft = np.fft.rfft(tone)
        if np.min(tone_fft) > -1_000_000: # cutoff that suggests no distinct sin wave
            char = ' '
        else:
            char = find_closest_key_value(np.argmin(tone_fft))
        chars.append(char)
    decoded_phrase = ''.join(chars)
    print(f"decode elapsed: {time.time()-t0}")
    return decoded_phrase

def play_and_decode_phrase(phrase, speed=DEFAULT_SPEED):
    TEMPFILE = 'temp.wav'
    ptttl_str = phrase_to_ptttl(phrase, speed=speed)
    play_string(ptttl_str)
    decoded_phrase = decode_wav(record_string(phrase, filename=TEMPFILE, speed=8))
    return decoded_phrase


if __name__ == "__main__":
    try:
        if len(sys.argv) == 3:
            speed = sys.argv[2]
        else:
            speed = 32
        results = play_and_decode_phrase(sys.argv[1], speed=speed)
        print(results)
    except Exception as e:
        print(str(e))
