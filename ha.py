import sys

from core import (
    phrase_to_ptttl,
    DEFAULT_PLAY_SPEED,
    send_phrase_to_ha
)
phrase = sys.argv[1]
if len(sys.argv) == 3:
    speed = sys.argv[2]
else:
    speed = DEFAULT_PLAY_SPEED
TEMPFILE = 'data/temp.wav'
ptttl_str = phrase_to_ptttl(phrase, speed=speed)
send_phrase_to_ha(ptttl_str)
