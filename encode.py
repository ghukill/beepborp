import sys

from core import (
    phrase_to_ptttl,
    ptttl_to_buzzer_rtttl,
    play_string,
    decode_wav,
    record_string,
    DEFAULT_RECORD_SPEED,
    DEFAULT_PLAY_SPEED
)
phrase = sys.argv[1]
if len(sys.argv) == 3:
    speed = sys.argv[2]
else:
    speed = DEFAULT_PLAY_SPEED
TEMPFILE = 'data/temp.wav'
ptttl_str = phrase_to_ptttl(phrase, speed=speed)
print("ptttl:", ptttl_str)
print("rtttl:", ptttl_to_buzzer_rtttl(ptttl_str))
play_string(ptttl_str)
decoded_phrase = decode_wav(record_string(phrase, filename=TEMPFILE, speed=DEFAULT_RECORD_SPEED))
print(decoded_phrase)
