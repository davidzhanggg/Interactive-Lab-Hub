
import json
import requests
import subprocess
import shutil
import argparse
from pathlib import Path

# Configuration
LOG_FILE = Path("dream_log.jsonl")
OUTPUT_FILE = Path("dream_story.txt")
AUDIO_FILE = Path("dream.wav")

MODEL = "qwen3.5:0.8b"

VOICE_MODEL = (
    "/home/pi/Interactive-Lab-Hub/Lab 3/voices/"
    "en_US-lessac-medium.onnx"
)


def load_observations():
    """Read YOLO detections from the previous day's photos."""
    if not LOG_FILE.exists():
        raise FileNotFoundError(f"Cannot find {LOG_FILE}")

    observations = []

    with LOG_FILE.open("r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue

            entry = json.loads(line)
            objects = entry.get("objects", [])

            if objects:
                labels = [
                    obj["name"].replace("_", " ")
                    for obj in objects
                ]
                description = ", ".join(labels)
            else:
                description = "No recognizable objects"

            observations.append(
                f"Photo {len(observations) + 1}: {description}"
            )

    return observations


def generate_dream(observations):
    """Ask Qwen to generate a creative dream."""
    if not observations:
        raise ValueError("No photo observations found.")

    photo_log = "\n".join(observations)

    prompt = f"""
You are a creative AI Dream Machine that turns a person's
daily photos into a funny, surreal dream.

Here are the objects detected in the photos:
{photo_log}

Write a short dream story inspired by these observations.

Rules:
1. Write between 100 and 150 words.
2. Use simple, natural, conversational English.
3. Use second-person narration ("You...") throughout.
4. Include at least 5 detected objects, integrating them naturally.
5. Make the dream surreal, imaginative, and slightly funny.
6. Create a coherent adventure with a beginning, middle, and end.
7. Do not list objects or use underscores in the story.
8. Avoid overly poetic or complicated descriptions.
9. Give the dream a short, creative title.
10. Output only the title and the dream story.
"""

    print("Asking Qwen to generate your dream...")

    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": MODEL,
            "prompt": prompt,
            "stream": False,
            "think": False,
            "options": {
                "temperature": 0.9,
                "num_ctx": 4096,
                "num_predict": 300
            }
        },
        timeout=600
    )

    response.raise_for_status()
    return response.json()["response"].strip()


def narrate_dream(dream, regenerate_audio=True):
    """Convert a dream to speech and play it using Piper."""

    if regenerate_audio:
        if not shutil.which("piper"):
            raise RuntimeError(
                "Piper executable not found. Install piper-tts."
            )

        if not Path(VOICE_MODEL).exists():
            raise FileNotFoundError(
                f"Voice model not found: {VOICE_MODEL}"
            )

        print("\nGenerating dream narration...")

        subprocess.run(
            [
                "piper",
                "--model", VOICE_MODEL,
                "--output_file", str(AUDIO_FILE)
            ],
            input=dream,
            text=True,
            encoding="utf-8",
            check=True
        )

        print(f"Audio saved to {AUDIO_FILE}")

    if not AUDIO_FILE.exists():
        raise FileNotFoundError(
            f"Audio file not found: {AUDIO_FILE}"
        )

    print("Playing your dream...")

    subprocess.run(
        ["aplay", str(AUDIO_FILE)],
        check=True
    )


def main():
    parser = argparse.ArgumentParser(
        description="Generate and narrate an AI dream."
    )

    parser.add_argument(
        "--replay",
        action="store_true",
        help="Replay the saved dream without generating a new one."
    )

    args = parser.parse_args()

    if args.replay:
        if not OUTPUT_FILE.exists():
            raise FileNotFoundError(
                "No saved dream found. Generate one first."
            )

        dream = OUTPUT_FILE.read_text(encoding="utf-8")

        print("\n===== SAVED DREAM =====\n")
        print(dream)

        # Reuse existing audio if available
        narrate_dream(
            dream,
            regenerate_audio=not AUDIO_FILE.exists()
        )

    else:
        # Step 1: Load observations
        observations = load_observations()

        print(
            f"Loaded observations from "
            f"{len(observations)} photos.\n"
        )

        # Step 2: Generate a dream using Qwen
        dream = generate_dream(observations)

        print("\n===== YOUR DREAM =====\n")
        print(dream)

        # Step 3: Save dream
        OUTPUT_FILE.write_text(dream, encoding="utf-8")
        print(f"\nDream saved to {OUTPUT_FILE}")

        # Step 4: Generate and play narration
        narrate_dream(dream)


if __name__ == "__main__":
    main()
