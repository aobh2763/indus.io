import os
import time
from collections import deque
from threading import Lock, RLock
from typing import Any

import cv2
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from ultralytics import YOLO


app = FastAPI(
    title="Indus Vision Scanner",
    description="Textile defect detection microservice for the indus.io production pipeline.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DEFAULT_MODEL_PATH = os.getenv("MODEL_PATH", "textile_defect_model.pt")
MODEL_CONFIG_PATH = os.getenv("MODEL_CONFIG_PATH", "/app/.scanner-model")
SOURCE_CONFIG_PATH = os.getenv("SOURCE_CONFIG_PATH", "/app/.scanner-source")
DEFAULT_CAMERA_URL = os.getenv("CAMERA_URL", "0")
CONFIDENCE_THRESHOLD = float(os.getenv("CONFIDENCE_THRESHOLD", "0.5"))


def available_models() -> list[str]:
    return sorted(
        file_name
        for file_name in os.listdir("/app")
        if file_name.endswith(".pt") and os.path.isfile(os.path.join("/app", file_name))
    )


def safe_model_path(model_name: str) -> str:
    file_name = os.path.basename(model_name.strip())
    model_path = os.path.join("/app", file_name)

    if not file_name.endswith(".pt") or not os.path.isfile(model_path):
        raise ValueError(f"Model not found: {file_name}")

    return model_path


def load_model_path() -> str:
    if os.path.exists(MODEL_CONFIG_PATH):
        with open(MODEL_CONFIG_PATH, "r", encoding="utf-8") as model_file:
            saved_model = model_file.read().strip()
            if saved_model:
                return safe_model_path(saved_model)

    return safe_model_path(DEFAULT_MODEL_PATH)


def save_model_path(model_path: str) -> None:
    with open(MODEL_CONFIG_PATH, "w", encoding="utf-8") as model_file:
        model_file.write(os.path.basename(model_path))


def load_camera_url() -> str:
    if os.path.exists(SOURCE_CONFIG_PATH):
        with open(SOURCE_CONFIG_PATH, "r", encoding="utf-8") as source_file:
            saved_source = source_file.read().strip()
            if saved_source:
                return saved_source

    return DEFAULT_CAMERA_URL


def save_camera_url(url: str) -> None:
    with open(SOURCE_CONFIG_PATH, "w", encoding="utf-8") as source_file:
        source_file.write(url.strip())


active_model_path = load_model_path()
model = YOLO(active_model_path)
model_lock = RLock()
state_lock = Lock()
recent_events: deque[dict[str, Any]] = deque(maxlen=20)
scanner_state: dict[str, Any] = {
    "camera_url": load_camera_url(),
    "status": "booting",
    "frames_processed": 0,
    "defects_detected": 0,
    "last_latency_ms": 0,
    "last_fps": 0,
    "last_seen": None,
    "last_error": None,
    "model": os.path.basename(active_model_path),
    "confidence_threshold": CONFIDENCE_THRESHOLD,
}


class CameraSource(BaseModel):
    url: str


class ModelSelection(BaseModel):
    model: str


def normalize_source(source: str) -> int | str:
    return int(source) if source.isdigit() else source


def update_state(**updates: Any) -> None:
    with state_lock:
        scanner_state.update(updates)


def snapshot_state() -> dict[str, Any]:
    with state_lock:
        return dict(scanner_state)


def serialize_detection(
    active_model: YOLO,
    box: Any,
    index: int,
    frame_width: int,
    frame_height: int,
) -> dict[str, Any]:
    confidence = float(box.conf[0])
    class_id = int(box.cls[0])
    label = active_model.names.get(class_id, f"class-{class_id}")
    x1, y1, x2, y2 = [float(value) for value in box.xyxy[0].tolist()]

    return {
        "id": f"{int(time.time() * 1000)}-{index}",
        "label": "textile defect" if label == "0" else label,
        "confidence": round(confidence, 3),
        "severity": "critical" if confidence >= 0.85 else "warning",
        "bbox": {
            "x": round(x1 / frame_width, 4),
            "y": round(y1 / frame_height, 4),
            "width": round((x2 - x1) / frame_width, 4),
            "height": round((y2 - y1) / frame_height, 4),
        },
        "timestamp": time.time(),
    }


def register_detections(detections: list[dict[str, Any]], latency_ms: int, fps: float) -> None:
    now = time.time()
    with state_lock:
        scanner_state["status"] = "detecting" if detections else "scanning"
        scanner_state["frames_processed"] += 1
        scanner_state["defects_detected"] += len(detections)
        scanner_state["last_latency_ms"] = latency_ms
        scanner_state["last_fps"] = round(fps, 1)
        scanner_state["last_seen"] = now
        scanner_state["last_error"] = None

        for detection in detections:
            recent_events.appendleft(detection)


def generate_frames():
    source = normalize_source(snapshot_state()["camera_url"])
    cap = cv2.VideoCapture(source)

    if not cap.isOpened():
        update_state(status="offline", last_error=f"Could not open camera source: {source}")
        return

    update_state(status="scanning", last_error=None)

    try:
        while True:
            frame_started_at = time.time()
            success, frame = cap.read()

            if not success:
                update_state(status="offline", last_error="Camera frame could not be read")
                break

            with model_lock:
                active_model = model
                results = active_model.predict(
                    source=frame,
                    show=False,
                    stream=False,
                    conf=CONFIDENCE_THRESHOLD,
                    verbose=False,
                )
            result = results[0]
            frame_height, frame_width = frame.shape[:2]
            detections = [
                serialize_detection(active_model, box, index, frame_width, frame_height)
                for index, box in enumerate(result.boxes)
            ]
            annotated_frame = result.plot()

            latency_ms = int((time.time() - frame_started_at) * 1000)
            fps = 1000 / latency_ms if latency_ms else 0
            register_detections(detections, latency_ms, fps)

            ret, buffer = cv2.imencode(".jpg", annotated_frame)
            if not ret:
                continue

            yield (
                b"--frame\r\n"
                b"Content-Type: image/jpeg\r\n\r\n" + buffer.tobytes() + b"\r\n"
            )
    finally:
        cap.release()


@app.get("/")
def read_root():
    return {
        "service": "indus-vision-scanner",
        "status": snapshot_state()["status"],
        "docs": "/docs",
    }


@app.get("/health")
def health():
    state = snapshot_state()
    return {
        "ok": state["status"] not in {"offline", "error"},
        "status": state["status"],
        "model": state["model"],
        "camera_url": state["camera_url"],
        "last_error": state["last_error"],
    }


@app.get("/status")
def status():
    return snapshot_state()


@app.get("/events")
def events(limit: int = Query(default=8, ge=1, le=20)):
    with state_lock:
        return {"events": list(recent_events)[:limit]}


@app.get("/models")
def models():
    return {
        "models": available_models(),
        "active": snapshot_state()["model"],
    }


@app.post("/model")
def set_model(payload: ModelSelection):
    global model

    next_model_path = safe_model_path(payload.model)

    with model_lock:
        model = YOLO(next_model_path)

    save_model_path(next_model_path)
    update_state(
        model=os.path.basename(next_model_path),
        status="model-updated",
        frames_processed=0,
        defects_detected=0,
        last_latency_ms=0,
        last_fps=0,
        last_error=None,
    )
    with state_lock:
        recent_events.clear()

    return snapshot_state()


@app.post("/source")
def set_source(payload: CameraSource):
    next_url = payload.url.strip()
    save_camera_url(next_url)
    update_state(
        camera_url=next_url,
        status="source-updated",
        frames_processed=0,
        defects_detected=0,
        last_error=None,
    )
    with state_lock:
        recent_events.clear()

    return snapshot_state()


@app.post("/set_camera")
def set_camera(url: str):
    return set_source(CameraSource(url=url))


@app.get("/video_feed")
def video_feed():
    return StreamingResponse(
        generate_frames(),
        media_type="multipart/x-mixed-replace; boundary=frame",
    )
