.PHONY: face-gesture face-stream pose-gesture pose-stream classify

face-gesture:
	uv run python face_capture.py | uv run python classify_gesture.py | uv run python gesture_serial.py

face-stream:
	uv run python face_capture.py | uv run python set_directions.py | uv run python serial_bridge.py

pose-gesture:
	uv run python pose_capture.py | uv run python classify_gesture.py | uv run python gesture_serial.py

pose-stream:
	uv run python pose_capture.py | uv run python set_directions.py | uv run python serial_bridge.py

classify:
	uv run python classify_gesture.py
