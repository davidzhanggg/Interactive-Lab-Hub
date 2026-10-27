from ultralytics import YOLO
from pathlib import Path
from datetime import datetime
import json

PHOTO_DIR = Path("dream_photos")
LOG_FILE = Path("dream_log.jsonl")

model = YOLO("yolo26n_ncnn_model", task="detect")

images = sorted(
    p for p in PHOTO_DIR.iterdir()
    if p.suffix.lower() in {".jpg", ".jpeg", ".png"}
)

if not images:
    raise SystemExit("No photos found!")

with LOG_FILE.open("w") as log:
    for image in images:
        results = model.predict(
            source=str(image),
            conf=0.25,
            verbose=False
        )

        objects = []

        for box in results[0].boxes:
            label = model.names[int(box.cls[0])]
            confidence = float(box.conf[0])

            objects.append({
                "name": label,
                "confidence": round(confidence, 2)
            })

        reading = {
            "timestamp": datetime.now().isoformat(),
            "image": image.name,
            "objects": objects
        }

        log.write(json.dumps(reading) + "\n")
        log.flush()

        print(f"{image.name}: {[o['name'] for o in objects]}")

print(f"\nProcessed {len(images)} photos.")
print(f"Results saved to {LOG_FILE}")