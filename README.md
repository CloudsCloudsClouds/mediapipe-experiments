# Experimentos de mediapipe para el proyecto del robot

Utilizo [`uv`](https://docs.astral.sh/uv/). Instalenlo. Tambien utilizo venv por buena medida

Sel setup para tener esto corriendo es.

1. [Instalar `uv`](https://docs.astral.sh/uv/getting-started/installation/)
2. Crear venv y usarlo
```
uv venv
source .venv/bin/activate
# O el que utilizen segun su OS, o cmd
```
3. Correr las demos

- [x] Deteccion de cabeza en general - `uv run face_detection.py`
- ~~[x] Deteccion de gestos de el rostro - `uv run face_gestures.py`~~
  - ~~[-] Enviar informacion sobre los gestos mediante serial - `uv run face_gestures_servo.py`~~
  - ~~Mejor utilizar `uv run face_capture.py`, este desacopla la logica de deteccion de rostros.~~
  - ~~[x] Añadido `serial_bridge.py`, que decide QUE mandar por serial. Desacoplamiento.~~
- [x] Deteccion de rostro, conversion de datos a grados y envio por serial.
  - `uv run face_capture.py set_directions.py serial_bridge.py`
  - `face_capture.py` Deteccion de gestos, y  "dumpea" los datos en stdout en formato json
  - `set_directions.py` Lee datos de stdout y los convierte en grados. Configurable de que llaves, ojos, rangos, eso.
  - `serial_bridge.py` Envio de datos mediante serial. Configurable del puerto, baud, etc.
- [-] Deteccion de gestos del brazo
  - Postergado por el momento
- [/] Deteccion de apuntar a direccion con los brazos
  - Actualmente en trabajo

Notar que esto por ahora son demos y no hay comunicacion con el robot mediante serial. Esto esta reservado un proyecto distinto utilizando ros (no viable por ahora).
