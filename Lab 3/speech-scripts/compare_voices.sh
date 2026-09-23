#!/usr/bin/env bash

TEXT="Hi David! Its time to go home"

VOICES_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/voices"

echo "=== eSpeak ==="
espeak -ven+f2 -k5 -s150 --stdout "$TEXT" | aplay

sleep 1

echo "=== Festival ==="
echo "$TEXT" | festival --tts

sleep 1

echo "=== Piper ==="
python3 -m piper \
  --model en_US-lessac-medium \
  --data-dir "$VOICES_DIR" \
  --output-raw \
  -- "$TEXT" \
| aplay -r 22050 -f S16_LE -t raw -
