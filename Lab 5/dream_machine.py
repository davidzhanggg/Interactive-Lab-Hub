
import argparse
import json
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

import qwiic_button

BASE_DIR = Path(__file__).resolve().parent

PHOTO_DIR = BASE_DIR / "dream_photos"
LOG_FILE = BASE_DIR / "dream_log.jsonl"
STORY_FILE = BASE_DIR / "dream_story.txt"
AUDIO_FILE = BASE_DIR / "dream.wav"
STATE_FILE = BASE_DIR / "dream_state.json"

OVERNIGHT_SCRIPT = BASE_DIR / "dream_overnight.py"
MORNING_SCRIPT = BASE_DIR / "dream_morning.py"

VALID_PHOTOS = {".jpg", ".jpeg", ".png"}


def save_state(state):
    STATE_FILE.write_text(
        json.dumps({
            "state": state,
            "updated_at": datetime.now().isoformat()
        }, indent=2),
        encoding="utf-8"
    )


def load_state():
    if not STATE_FILE.exists():
        return "READY"

    data = json.loads(STATE_FILE.read_text(encoding="utf-8"))
    return data.get("state", "READY")


def show(message):
    print(f"\n[Dream Machine] {message}", flush=True)


def count_photos():
    if not PHOTO_DIR.exists():
        return 0

    return sum(
        1 for p in PHOTO_DIR.iterdir()
        if p.is_file() and p.suffix.lower() in VALID_PHOTOS
    )


def start_processing():
    """Start YOLO processing in a separate process."""
    count = count_photos()

    if count == 0:
        show("No photos found. Add photos before starting.")
        return None

    if not OVERNIGHT_SCRIPT.exists():
        show("dream_overnight.py not found.")
        return None

    # Old outputs must not be confused with the new session.
    for path in (LOG_FILE, STORY_FILE, AUDIO_FILE):
        if path.exists():
            path.unlink()

    show(f"Good night! I'll dream about your day.")
    show(f"Processing {count} photos...")

    save_state("PROCESSING")

    try:
        return subprocess.Popen(
            [sys.executable, str(OVERNIGHT_SCRIPT)],
            cwd=BASE_DIR
        )
    except OSError as exc:
        save_state("READY")
        show(f"Could not start processing: {exc}")
        return None


def reveal_dream(replay=False):
    """Generate or replay a narrated dream."""
    if not replay and not LOG_FILE.exists():
        show("Dream log not found.")
        return False

    command = [sys.executable, str(MORNING_SCRIPT)]

    if replay:
        command.append("--replay")
        show("Replaying your dream...")
    else:
        show("Good morning! Creating your dream...")

    try:
        subprocess.run(
            command,
            cwd=BASE_DIR,
            check=True
        )
        return True

    except subprocess.CalledProcessError as exc:
        show(f"Dream narration failed: {exc}")
        return False


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Prepare for a new night"
    )
    args = parser.parse_args()

    if args.reset:
        save_state("READY")
        show("Reset complete. Ready for a new night.")
        return

    button = qwiic_button.QwiicButton()

    if not button.begin():
        sys.exit("Qwiic Button not found. Check I2C connection.")

    state = load_state()
    process = None

    # Recover state after the controller was restarted.
    if state == "PROCESSING":
        show("Previous processing session was interrupted.")
        show("Check the log and reset before starting again.")
        state = "ERROR"
        save_state(state)

    show("AI Dream Machine started.")
    show(f"Current state: {state}")

    if state == "READY":
        show("Press button to start dreaming.")
    elif state == "DREAM_READY":
        show("Press button to reveal your dream.")
    elif state == "FINISHED":
        show("Press button to replay your dream.")
    else:
        show("Run python dream_machine.py --reset to retry.")

    # Track previous state to detect a new button press.
    last_pressed = button.is_button_pressed()

    try:
        while True:
            # Check whether photo processing finished.
            if state == "PROCESSING" and process is not None:
                result = process.poll()

                if result is not None:
                    process = None

                    if (
                        result == 0
                        and LOG_FILE.exists()
                        and LOG_FILE.stat().st_size > 0
                    ):
                        state = "DREAM_READY"
                        save_state(state)
                        show("Dream memories saved!")
                        show("Press the button in the morning.")
                    else:
                        state = "ERROR"
                        save_state(state)
                        show("Photo processing failed.")

            pressed = button.is_button_pressed()

            # Only act on a new press, not while holding.
            if pressed and not last_pressed:

                if state == "READY":
                    process = start_processing()

                    if process is not None:
                        state = "PROCESSING"

                elif state == "PROCESSING":
                    show("Still processing photos...")

                elif state == "DREAM_READY":
                    state = "REVEALING"
                    save_state(state)

                    success = reveal_dream()

                    if success:
                        state = "FINISHED"
                        save_state(state)
                        show("Dream complete!")
                    else:
                        state = "DREAM_READY"
                        save_state(state)

                elif state == "FINISHED":
                    reveal_dream(replay=True)

                else:
                    show("Reset required before starting again.")

            last_pressed = pressed
            time.sleep(0.05)

    except KeyboardInterrupt:
        show("Controller stopped.")

        if process is not None and process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()


if __name__ == "__main__":
    main()
