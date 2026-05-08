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
- [ ] Deteccion de gestos de el rostro
  - [ ] Enviar informacion sobre los gestos mediante serial 
- [ ] Deteccion de gestos del brazo
- [ ] Deteccion de apuntar a direccion con los brazos

Notar que esto por ahora son demos y no hay comunicacion con el robot mediante serial. Esto esta reservado un proyecto distinto utilizando ros (no viable por ahora).
