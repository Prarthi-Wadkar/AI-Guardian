# AI Guardian

An AI-powered guardian system using YOLO11n object detection, OpenCV, and ElevenLabs text-to-speech, running on a camera-equipped robot.

## Setup

1. **Clone the repo**
   ```
   git clone <your-repo-url>
   cd ai-guardian
   ```

2. **Create and activate a virtual environment**
   ```
   python -m venv venv
   venv\Scripts\activate   # Windows
   source venv/bin/activate   # macOS/Linux
   ```

3. **Install dependencies**
   ```
   pip install -r requirements.txt
   ```

4. **Add your API key**

   Copy the example config and add your own ElevenLabs API key:
   ```
   cp config.example.py config.py
   ```
   Then open `config.py` and replace the placeholder with your actual key.
   `config.py` is gitignored — it will never be committed or visible to others.

5. **Run**
   ```
   python detect.py
   ```

## Project structure

- `detect.py` — main detection loop
- `explore.py` — exploration/movement logic
- `suspicion.py` — suspicious-activity logic
- `voice.py` — text-to-speech alerts via ElevenLabs
- `config.example.py` — template for your local config; copy to `config.py`
- `yolo11n.pt` — YOLO detection model weights

## Notes

- The `recordings/` folder (snapshot images from detections) is gitignored and stored locally only.