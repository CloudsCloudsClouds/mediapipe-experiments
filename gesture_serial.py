#!/usr/bin/env python3
"""
gesture_serial.py — reads gesture JSON from stdin, sends plain text
commands over serial to the Arduino.

Protocol: sends the gesture number as a decimal string + newline.
  "3\\n"  -> Arduino triggers double blink
  "0\\n"  -> Arduino goes to rest position

Pipeline: face_capture.py | classify_gesture.py | gesture_serial.py
"""

import sys
import json
import serial
import time

SERIAL_PORT = "/dev/ttyUSB0"
BAUD_RATE = 9600
SEND_INTERVAL = 0.2

try:
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=0.1)
except serial.SerialException as e:
    print(f"[gesture_serial] {e}", file=sys.stderr)
    sys.exit(1)

last_send_time = 0.0

for line in sys.stdin:
    line = line.strip()
    if not line:
        continue

    try:
        data = json.loads(line)
    except json.JSONDecodeError:
        continue

    gesture = data.get("gesture", -1)
    if gesture < 0:
        continue

    now = time.time()
    if now - last_send_time < SEND_INTERVAL:
        continue

    cmd = f"{gesture}\n"
    ser.write(cmd.encode("utf-8"))
    last_send_time = now
