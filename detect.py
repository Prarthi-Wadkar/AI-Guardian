# detect.py
# Phase 1: The Brain
# Goal: read camera feed -> run YOLO on each frame -> show detections live
# No "suspicious" logic yet. Just confirm the model SEES things correctly.

import cv2
import time
from ultralytics import YOLO
import config

def main():
    print("Loading model...")
    model = YOLO(config.MODEL_PATH)

    print(f"Connecting to camera source: {config.CAMERA_SOURCE}")
    cap = cv2.VideoCapture(config.CAMERA_SOURCE)

    if not cap.isOpened():
        print("ERROR: Could not open camera source.")
        print("Check your CAMERA_SOURCE in config.py")
        return

    print("Camera connected. Press 'q' to quit.")

    prev_time = time.time()

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to grab frame. Stream may have dropped.")
            break

        # Run YOLO detection on this frame
        results = model(frame, conf=config.CONFIDENCE_THRESHOLD, verbose=False)

        # results[0].plot() draws boxes + labels on the frame automatically
        annotated_frame = results[0].plot()

        # FPS calculation
        if config.SHOW_FPS:
            curr_time = time.time()
            fps = 1 / (curr_time - prev_time)
            prev_time = curr_time
            cv2.putText(
                annotated_frame,
                f"FPS: {fps:.1f}",
                (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 255, 0),
                2,
            )

        cv2.imshow("AI Guardian - Brain (Phase 1)", annotated_frame)

        # Press 'q' to quit
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
