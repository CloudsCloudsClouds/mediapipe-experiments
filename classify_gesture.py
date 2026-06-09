#!/usr/bin/env python3
"""
classify_gesture.py — reads blendshape JSON from stdin, classifies facial
expressions into Arduino gesture commands, outputs gesture JSON to stdout.

Pipeline: face_capture.py | classify_gesture.py | gesture_serial.py
"""

import sys
import json
import time

# ===================== CONFIGURATION =====================

# Blendshape thresholds (0.0 - 1.0)
BLINK_THRESHOLD = 0.7
BROW_UP_THRESHOLD = 0.5
SMILE_THRESHOLD = 0.35
JAW_OPEN_THRESHOLD = 0.5
BROW_DOWN_THRESHOLD = 0.4
MOUTH_PRESS_THRESHOLD = 0.3
EYE_LOOK_THRESHOLD = 0.5
TALK_JAW_THRESHOLD = 0.3
TALK_OSCILLATIONS = 3

# Cooldown per gesture in seconds (gesture_id -> seconds)
GESTURE_COOLDOWN = {
    1: 1.0, 2: 1.0, 3: 1.5,
    4: 2.0, 5: 2.0,
    6: 2.0, 7: 2.0,
    8: 3.0, 9: 3.0, 10: 3.0,
    13: 2.0, 14: 1.5,
}

# Auto-blink
AUTO_BLINK_ENABLED = True
AUTO_BLINK_INTERVAL = 4.0

# Gesture priority list (highest first wins)
# (gesture_id, name)
GESTURE_PRIORITY = [
    (3, "parpadeo_doble"),
    (10, "sonrisa"),
    (8, "enojo"),
    (9, "sorpresa"),
    (14, "hablar"),
    (13, "abrir_mandibula"),
    (1, "parpadeo_der"),
    (2, "parpadeo_izq"),
    (6, "cejas_arriba"),
    (7, "cejas_abajo"),
    (4, "ojos_arriba"),
    (5, "ojos_abajo"),
]

# ===================== STATE =====================

state = "idle"
cooldown_until = 0.0
last_gesture_time = time.time()
last_sent_gesture = -1

# Talking detection (rolling window across all frames)
prev_jaw = None
oscillation_count = 0
jaw_direction = None

# ===================== HELPERS =====================

def avg(a, b):
    return (a + b) / 2.0

# ===================== MAIN LOOP =====================

for line in sys.stdin:
    line = line.strip()
    if not line:
        continue

    try:
        data = json.loads(line)
    except json.JSONDecodeError:
        continue

    blendshapes = data.get("blendshapes", {})
    now = time.time()

    # --- Always update talking detection (cross-frame) ---
    jaw_open = blendshapes.get("jawOpen", 0)
    if prev_jaw is not None:
        diff = jaw_open - prev_jaw
        if abs(diff) > 0.02:
            new_dir = "up" if diff > 0 else "down"
            if jaw_direction is not None and new_dir != jaw_direction:
                oscillation_count += 1
            jaw_direction = new_dir
    prev_jaw = jaw_open

    is_talking = (jaw_open > TALK_JAW_THRESHOLD and oscillation_count >= TALK_OSCILLATIONS)

    # --- State machine ---
    if state == "cooldown":
        if now >= cooldown_until:
            state = "idle"
        else:
            continue

    # --- Read blendshapes ---
    blink_l = blendshapes.get("eyeBlinkLeft", 0)
    blink_r = blendshapes.get("eyeBlinkRight", 0)
    brow_up = blendshapes.get("browInnerUp", 0)
    smile_l = blendshapes.get("mouthSmileLeft", 0)
    smile_r = blendshapes.get("mouthSmileRight", 0)
    brow_down_l = blendshapes.get("browDownLeft", 0)
    brow_down_r = blendshapes.get("browDownRight", 0)
    press_l = blendshapes.get("mouthPressLeft", 0)
    press_r = blendshapes.get("mouthPressRight", 0)
    look_up_l = blendshapes.get("eyeLookUpLeft", 0)
    look_up_r = blendshapes.get("eyeLookUpRight", 0)
    look_down_l = blendshapes.get("eyeLookDownLeft", 0)
    look_down_r = blendshapes.get("eyeLookDownRight", 0)

    # --- Evaluate gestures in priority order ---
    chosen_id = -1
    chosen_name = None

    for gid, gname in GESTURE_PRIORITY:
        triggered = False

        if gid == 3:
            triggered = (blink_l > BLINK_THRESHOLD and blink_r > BLINK_THRESHOLD)
        elif gid == 10:
            triggered = (avg(smile_l, smile_r) > SMILE_THRESHOLD)
        elif gid == 8:
            triggered = (brow_up > BROW_UP_THRESHOLD and avg(press_l, press_r) > MOUTH_PRESS_THRESHOLD)
        elif gid == 9:
            triggered = (jaw_open > JAW_OPEN_THRESHOLD and brow_up > BROW_UP_THRESHOLD * 0.8)
        elif gid == 14:
            triggered = is_talking
        elif gid == 13:
            triggered = (jaw_open > JAW_OPEN_THRESHOLD + 0.2)
        elif gid == 1:
            triggered = (blink_r > BLINK_THRESHOLD > blink_l)
        elif gid == 2:
            triggered = (blink_l > BLINK_THRESHOLD > blink_r)
        elif gid == 6:
            triggered = (brow_up > BROW_UP_THRESHOLD)
        elif gid == 7:
            triggered = (max(brow_down_l, brow_down_r) > BROW_DOWN_THRESHOLD)
        elif gid == 4:
            triggered = (max(look_up_l, look_up_r) > EYE_LOOK_THRESHOLD)
        elif gid == 5:
            triggered = (max(look_down_l, look_down_r) > EYE_LOOK_THRESHOLD)

        if triggered:
            chosen_id = gid
            chosen_name = gname
            break

    # --- Auto-blink fallback ---
    if chosen_id == -1 and AUTO_BLINK_ENABLED and (now - last_gesture_time) > AUTO_BLINK_INTERVAL:
        chosen_id = 3
        chosen_name = "parpadeo_doble"

    # --- Rest fallback (only send transition to rest once) ---
    if chosen_id == -1:
        if last_sent_gesture not in (-1, 0):
            chosen_id = 0
            chosen_name = "reposo"
        else:
            continue

    # --- Apply cooldown and send ---
    state = "cooldown"
    cooldown_until = now + GESTURE_COOLDOWN.get(chosen_id, 2.0)
    last_gesture_time = now
    last_sent_gesture = chosen_id

    print(json.dumps({"gesture": chosen_id, "name": chosen_name}), flush=True)
