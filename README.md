# AI Guardian: RAG grounding layer

Detection (YOLO11n + suspicion.py) says WHAT happened.
This layer decides WHAT TO SAY AND DO, using a protocol book instead of guessing.
Voice is paused until the robot is assembled: for now the demo prints what the robot WOULD say.
There is no ElevenLabs and no voice API key. Later, a local offline voice (Vosk for listening,
a local text-to-speech engine for speaking) will play result["spoken"].

## Setup
1. Activate the venv and run: pip install -r requirements.txt
2. Add one line to config.py (and a placeholder to config.example.py):
       GROQ_API_KEY = "your_key_here"
3. Check the plumbing (no key, no big model needed): python test_pipeline.py
4. Run the demo (first run downloads a ~90 MB embedding model): python guardian_rag.py

Without a key, or when Groq is down or rate-limited, it falls back to the matching
protocol's "Say" line, so the robot still has something to say.

## Plug it into suspicion.py
    from guardian_rag import GuardianRAG
    guardian = GuardianRAG(language="English")      # or "Marathi"

    # where your loitering alert fires (adapt the names to your code):
    result = guardian.respond({"type": "loitering", "duration_s": elapsed,
                               "location": "main gate", "time": now.strftime("%H:%M")})
    if result:                       # None means "same event, still cooling down"
        # voice is paused: print or log result["spoken"] for now.
        # once the robot is built, pass it to the local voice speaker
        # result["action"] is announce / alert_human / log_only
        # result["log"] and result["sources"] are good for your incident log

Event types: loitering, closed_hours, unattended_object, circling, crowd, emergency.

## How it works (the 5 lines to explain in an interview)
1. The protocol book is split into one chunk per "##" section.
2. Each chunk becomes a vector (sentence-transformers). FAISS stores them.
3. A detection event becomes a sentence, then a vector, and FAISS returns the closest protocols (retrieval).
4. Groq gets the event plus only those protocols and must answer in JSON (generation).
5. Safety nets: unknown action becomes alert_human, weak match becomes alert_human, cooldown protects the free Groq quota.

## Edit these first
- knowledge_base/protocols.md: rewrite for the real place the robot will guard. Check the Marathi lines yourself.
- Thresholds (loitering seconds, night hours) live in your suspicion.py, not here.
