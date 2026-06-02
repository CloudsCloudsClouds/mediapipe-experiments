import sys
import json
import serial
import time

# MediaPipe Face Landmarker (ARKit 52) Blendshape Keys:
# _neutral, browDownLeft, browDownRight, browInnerUp, browOuterUpLeft, browOuterUpRight,
# cheekPuff, cheekSquintLeft, cheekSquintRight, eyeBlinkLeft, eyeBlinkRight,
# eyeLookDownLeft, eyeLookDownRight, eyeLookInLeft, eyeLookInRight, eyeLookOutLeft,
# eyeLookOutRight, eyeLookUpLeft, eyeLookUpRight, eyeSquintLeft, eyeSquintRight,
# eyeWideLeft, eyeWideRight, jawForward, jawLeft, jawOpen, jawRight, mouthClose,
# mouthDimpleLeft, mouthDimpleRight, mouthFrownLeft, mouthFrownRight, mouthFunnel,
# mouthLeft, mouthLowerDownLeft, mouthLowerDownRight, mouthPressLeft, mouthPressRight,
# mouthPucker, mouthRight, mouthRollLower, mouthRollUpper, mouthShrugLower,
# mouthShrugUpper, mouthSmileLeft, mouthSmileRight, mouthStretchLeft, mouthStretchRight,
# mouthUpperUpLeft, mouthUpperUpRight, noseSneerLeft, noseSneerRight


# Solo selecciona cuales mandar. Este es el default sin ojos aun.
SELECTED_SHAPES = ["jawOpen", "eyeBlinkLeft", "eyeBlinkRight", "mouthSmileLeft", "mouthSmileRight"]
# Los 8 minimos necesarios para conseguir direccion del ojo.
# SELECTED_SHAPES = ["eyeLookInLeft", "eyeLookOutLeft", "eyeLookUpLeft", "eyeLookDownLeft",
#     "eyeLookInRight",
#     "eyeLookOutRight",
#     "eyeLookUpRight",
#     "eyeLookDownRight"]


# Sobre la direccion del cuello.
TRANSFORM_KEYS = [
    "m00", "m01", "m02", "m03",
    "m10", "m11", "m12", "m13",
    "m20", "m21", "m22", "m23",
]

# Configuracion sobre el puerto y el baudrate.
# Consideren bajar/subir el baudrate si se tranca.
# En esp32 este esta excelente, probablemente sea menos en uno.
ser = serial.Serial('/dev/ttyUSB0', 115200, timeout=0.1)
last_send_time = 0
send_interval = 0.2

for line in sys.stdin:
    line = line.strip()
    if not line:
        continue

    try:
        data = json.loads(line)
    except json.JSONDecodeError:
        continue

    current_time = time.time()
    if current_time - last_send_time < send_interval:
        continue

    blendshapes = data.get("blendshapes", {})
    transform = data.get("transform", {})

    values = [f"{blendshapes.get(s, 0):.3f}" for s in SELECTED_SHAPES]
    if transform:
        values.extend(str(transform.get(k, 0)) for k in TRANSFORM_KEYS)

    # Formato de envio
    # $v1,v2,...,vm,m00,m01,...,tx,ty,tz#
    # Un paquete inicia con $
    # Primero lo primero se manda los valores en SELECTED_SHAPES
    # Luego se manda los valores en TRANSFORM_KEYS
    # Se manda primero los valores de blendshapes, luego los de transform, y termina con #
    packet = "$" + ",".join(values) + "#"
    # No calcula rotacion de esta transformacion.
    # Deberia hacer eso...
    ser.write(packet.encode("utf-8"))
    last_send_time = current_time
