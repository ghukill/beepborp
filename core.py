""""""

import os
import re
import time
import warnings

import librosa
import matplotlib.pyplot as plt
import numpy as np
from ptttl.audio import ptttl_to_wav
import requests
from scipy import signal
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
SR = 44100 # sampling rate
WINDOW = 1 # window size for librosa

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

    # add header and leader
    phrase = f"goober {phrase} tronic"

    # build melody
    for char in phrase:
        melody_notes.append(LETTER_TO_NOTES.get(char.lower().strip(), "p"))
    melody = ",".join(melody_notes)
    return f"""{phrase}:d={speed},o=1,b=123:{melody}"""

def ptttl_to_buzzer_rtttl(ptttl_str):
    """Convert ptttl to rtttl with octave bumped"""
    name, header, melody = re.match(r'(.+?)(:.*:)(.*)',ptttl_str).groups()
    def increment(match):
        return str(int(match.group(0)) + 1)

    melody_bumped = re.sub(r'\d+', increment, melody)
    return "bpbp" + header + melody_bumped

def send_phrase_to_ha(ptttl_str):
    """
    Requires env var HA_ENDPOINT to be set"
    """
    rtttl_str = ptttl_to_buzzer_rtttl(ptttl_str)
    ha_endpoint = os.getenv("HA_ENDPOINT")
    if ha_endpoint is None:
        raise Exception("env var HA_ENDPOINT must be set")
    url = f"{ha_endpoint.rstrip('/')}/api/webhook/play_rtttl"
    print(f"sending: {rtttl_str} to {url}")
    response = requests.post(
        url,
        json={
            "rtttl":rtttl_str
        },
        headers={
            "Content-Type":"application/json"
        }
    )
    print(response.status_code)


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


def extract_msg_from_array(raw_array):
    # load
    header, leader = np.load('data/header.npy'), np.load('data/leader.npy')
    # rec, _ = librosa.load('data/rec.wav', sr=SR, mono=False)

    # find header and leader index in recording
    header_c = signal.correlate(raw_array, header[:SR * WINDOW], mode='valid', method='fft')
    leader_c = signal.correlate(raw_array, leader[:SR * WINDOW], mode='valid', method='fft')

    # get start end points
    msg_start, msg_end = (np.argmax(header_c) + len(header) + WAV_FRAMES), np.argmax(leader_c)
    msg = raw_array[msg_start:msg_end]

    return msg



def decode_wav(filename):
    t0 = time.time()
    a = array_from_wav(filename)

    # extract header and leader
    a = extract_msg_from_array(a)

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


def convert_file_to_wav(filename, output_file=None):
    if output_file is None:
        output_file = "data/convert_temp.wav"
    if os.path.exists(output_file):
        os.remove(output_file)
    cmd = f"ffmpeg -loglevel quiet -i {filename} -ar 44100 {output_file}"
    os.system(cmd)
    return output_file