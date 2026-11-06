# voice.py - temporary stub. Voice is paused until the robot is assembled.
LINES = {
    "normal": "la..la..la...la.... nothing to see here just being myself!",
    "suspicious_person_seen": "Prarthi! I see someone, and they are looking at me!",
    "loitering": "Go away! Shuu...Shuu.. shuuuu!",
    "chair_seen": "Pick me up Prarthi! I wanna sit there!",
}

def speak(situation):
    text = LINES.get(situation, situation)  # unknown key: treat it as plain text
    print(f"[VOICE PAUSED] {text}")

if __name__ == "__main__":
    speak("normal")