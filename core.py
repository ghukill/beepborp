""""""

import time
import warnings

import numpy as np
from ptttl.audio import ptttl_to_wav
import simpleaudio as sa
from wave import open as open_wave

warnings.simplefilter("ignore", DeprecationWarning)

INPUTFILE = "data/bach.ptttl"
OUTPUTFILE = "data/output.wav"
DEFAULT_PLAY_SPEED = 32
DEFAULT_RECORD_SPEED = 8
WAV_FRAMES = 10756  # NOTE: hardcodes len to 44.1khz @ 8 beats @ 123 bpm
FFT_CUTOFF = -1_000_000  # NOTE: cutoff that suggests no distinct sin wave
LETTER_TO_NOTES = {
    "a": "c3",
    "b": "d3",
    "c": "e3",
    "d": "f3",
    "e": "g3",
    "f": "a3",
    "g": "b3",
    "h": "c4",
    "i": "d4",
    "j": "e4",
    "k": "f4",
    "l": "g4",
    "m": "a4",
    "n": "b4",
    "o": "c5",
    "p": "d5",
    "q": "e5",
    "r": "f5",
    "s": "g5",
    "t": "a5",
    "u": "b5",
    "v": "c6",
    "w": "d6",
    "x": "e6",
    "y": "f6",
    "z": "g6"
}
FFT_IDX_TO_LETTER = {  # fft index calculated for letters a-z, based on 44.1khz, 123 bpm, 8 duration
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


def record_string(s, filename=OUTPUTFILE, speed=DEFAULT_PLAY_SPEED):
    ptttl_str = phrase_to_ptttl(s, speed=speed)
    ptttl_to_wav(ptttl_str, filename)
    return filename


def phrase_to_ptttl(phrase, speed=DEFAULT_PLAY_SPEED):
    melody_notes = []
    for char in phrase:
        melody_notes.append(LETTER_TO_NOTES.get(char.lower().strip(), "p"))
    melody = ",".join(melody_notes)
    return f"""{phrase}:
b=123, d={speed}, o=1:
{melody}
"""


def array_from_wav(filename):
    waveFile = open_wave(filename, 'rb')
    nframes = waveFile.getnframes()
    wavFrames = waveFile.readframes(nframes)
    ys = np.fromstring(wavFrames, dtype=np.int16)
    return ys


def tones_from_array(a):
    tone_len = WAV_FRAMES
    tone_count = round((len(a) / tone_len))
    tones = np.array_split(a, tone_count)
    return tones


def get_letter_from_fft_idx(fft_idx):
    """
    Based on the index of the largest FFT peak, access the closest letter to that index
    """

    closest_key = min(FFT_IDX_TO_LETTER.keys(), key=lambda x: abs(x - fft_idx))
    closest_value = FFT_IDX_TO_LETTER[closest_key]
    if abs(closest_key - fft_idx) > 500:
        return " "
    else:
        return closest_value


def decode_wav(filename):
    t0 = time.time()
    a = array_from_wav(filename)
    tones = tones_from_array(a)
    chars = []
    for tone in tones:
        tone_fft = np.fft.rfft(tone)
        if np.min(tone_fft) > -FFT_CUTOFF:
            char = ' '
        else:
            char = get_letter_from_fft_idx(np.argmin(tone_fft))
        chars.append(char)
    decoded_phrase = ''.join(chars)
    print(f"decode elapsed: {time.time() - t0}")
    return decoded_phrase
