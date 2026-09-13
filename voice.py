from elevenlabs.client import ElevenLabs
import config
import tempfile
import os

def speak(situation):
    if situation == "normal":
        text = "la..la..la...la.... nothing to see here just being myself!"
    elif situation == "suspicious_person_seen":
        text = "Prarthi! I see someone, and they are looking at me!"
    elif situation == "loitering":
        text = "Go away! Shuu...Shuu.. shuuuu!"
    elif situation == "chair_seen":
        text = "Pick me up Prarthi! I wanna sit there!"

    client = ElevenLabs(api_key=config.ELEVENLABS_API_KEY)

    audio_generator = client.text_to_speech.convert(
        text=text,
        voice_id=config.ELEVENLABS_VOICE_ID,
        model_id="eleven_flash_v2_5"
    )

    # Join the streamed chunks into a single bytes object
    audio = b"".join(audio_generator)

    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as f:
        f.write(audio)
        temp_path = f.name

    os.startfile(temp_path)

if __name__ == "__main__":
    speak("normal")