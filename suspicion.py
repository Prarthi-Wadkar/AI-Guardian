# suspicion.py
# Day 3: time-based suspicion
# Day 4: loitering detection (NEW)
# Day 5: sound alert on trigger (NEW)
# Day 6: snapshot logging on trigger (NEW)

import cv2
import os
from ultralytics import YOLO
from playsound import playsound
import config
from datetime import datetime


def play_alert_sound():
    """Day 5: play a short sound when something triggers."""
    try:
        playsound(config.SOUND_ALERT_FILE)
    except Exception as e:
        print(f"Could not play sound: {e}")


def save_snapshot(frame):
    """Day 6: save the current frame with a timestamped filename."""
    if not os.path.exists(config.RECORDINGS_FOLDER):
        os.makedirs(config.RECORDINGS_FOLDER)

    timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{config.RECORDINGS_FOLDER}/alert_{timestamp_str}.jpg"
    cv2.imwrite(filename, frame)
    print(f"Saved snapshot: {filename}")


def main():
    print("Loading model...")
    model = YOLO(config.MODEL_PATH)

    cap = cv2.VideoCapture(config.CAMERA_SOURCE)
    if not cap.isOpened():
        print("ERROR: Could not open camera source.")
        return

    print("Camera connected. Press 'q' to quit.")

    # Day 4: timestamp that persists ACROSS frames — lives outside the loop
    person_first_seen_time = None

    # Day 6: tracks whether we've already saved a snapshot for THIS loitering
    # event, so we don't save hundreds of images per second once triggered
    snapshot_taken_for_this_event = False

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        results = model(frame, conf=config.CONFIDENCE_THRESHOLD, verbose=False)
        boxes = results[0].boxes

        # Day 4: reset EVERY frame — this is the per-frame flag, short memory
        person_seen_this_frame = False

        for box in boxes:
            class_id = int(box.cls[0])
            class_name = model.names[class_id]

            if class_name != "person":
                continue  # skip anything that isn't a person, check the next box

            person_seen_this_frame = True

            # --- Day 3: time-based suspicion ---
            current_hour = datetime.now().hour
            is_suspicious_time = (
                current_hour >= config.SUSPICIOUS_HOUR_START
                or current_hour <= config.SUSPICIOUS_HOUR_END
            )
            if is_suspicious_time:
                print(f"⚠️ SUSPICIOUS TIME: Person detected at {datetime.now().strftime('%H:%M:%S')}")

            # --- Day 4: loitering ---
            if person_first_seen_time is None:
                
                person_first_seen_time = datetime.now()
            else:
                duration = (datetime.now() - person_first_seen_time).total_seconds()

                if duration > config.LOITER_SECONDS:
                    print(f"⚠️ LOITERING: person present for {duration:.1f}s")

                    
                    if not snapshot_taken_for_this_event:
                        play_alert_sound()
                        save_snapshot(frame)
                        snapshot_taken_for_this_event = True

       
        if not person_seen_this_frame:
           
            person_first_seen_time = None
            snapshot_taken_for_this_event = False

        cv2.imshow("AI Guardian", results[0].plot())

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()