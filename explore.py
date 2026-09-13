# explore.py
# Day 2: Look inside the raw `results` object instead of using .plot()
# Goal: understand box coordinates, class IDs, class names, and confidence scores

import cv2
from ultralytics import YOLO
import config


def main():
    print("Loading model...")
    model = YOLO(config.MODEL_PATH)

    cap = cv2.VideoCapture(config.CAMERA_SOURCE)
    if not cap.isOpened():
        print("ERROR: Could not open camera source.")
        return

    print("Camera connected. Press 'q' to quit.")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        results = model(frame, conf=config.CONFIDENCE_THRESHOLD, verbose=False)

        # results[0].boxes holds all detected objects for this frame
        boxes = results[0].boxes

        print(f"\n--- New frame: {len(boxes)} object(s) detected ---")

        for box in boxes:
            # Class ID is a number (e.g., 0). model.names converts it to a label (e.g., "person")
            class_id = int(box.cls[0])
            class_name = model.names[class_id]

            # Confidence score, as a plain float between 0 and 1
            confidence = float(box.conf[0])

            # Bounding box coordinates: top-left (x1,y1) and bottom-right (x2,y2) in pixels
            x1, y1, x2, y2 = box.xyxy[0]

            print(
                f"Class: {class_name} | "
                f"Confidence: {confidence:.2f} | "
                f"Box: ({int(x1)}, {int(y1)}) to ({int(x2)}, {int(y2)})"
            )

        # Still show the normal annotated view so you have visual reference
        cv2.imshow("AI Guardian - Explore (Day 2)", results[0].plot())

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()