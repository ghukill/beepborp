import os
import sys
from core import decode_wav, convert_file_to_wav

input_file = sys.argv[1]

if not input_file.endswith('wav2'):
    TEMP_FILE = "data/convert_temp.wav"
    input_file = convert_file_to_wav(input_file, output_file=TEMP_FILE)
    decoded_phrase = decode_wav(input_file)
    # os.remove(TEMP_FILE)
else:
    decoded_phrase = decode_wav(input_file)

print(decoded_phrase)