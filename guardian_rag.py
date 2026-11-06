"""
guardian_rag.py  -  RAG-grounding layer for AI Guardian

What it does, in plain words:
  1. Your YOLO + suspicion code detects something   -> an "event" (loitering, after hours...)
  2. We turn the event into a sentence               -> the "query"
  3. We search our protocol book for matching rules  -> RETRIEVAL
  4. We give those rules + the event to Groq         -> GENERATION (grounded in the rules)
  5. YOUR code speaks the result (your local voice.py) and logs it

If Groq is down, rate-limited, or there is no API key, we fall back to reading the
"Say" line straight out of the best matching protocol, so the robot never goes silent.

Setup:  pip install -r requirements.txt   and put GROQ_API_KEY in config.py.
Demo:   python guardian_rag.py
"""
import glob
import json
import os
import re
import time
from dataclasses import dataclass

import numpy as np

KB_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "knowledge_base")
# Model names change over time. Check Groq's current model list and override via .env if needed.
GROQ_MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-20b")
EMBED_MODEL = os.getenv("EMBED_MODEL", "all-MiniLM-L6-v2")  # small, free, runs on CPU

ACTIONS = ("announce", "alert_human", "log_only")


# ----------------------------------------------------------------------------
# Step A: read the protocol book and cut it into chunks
# ----------------------------------------------------------------------------
@dataclass
class Chunk:
    title: str   # the "## heading" of the protocol
    text: str    # the body of that protocol
    source: str  # which file it came from


def load_chunks(kb_dir=KB_DIR, max_chars=900):
    """One chunk per '## heading' section. Very long sections are split further."""
    chunks = []
    for path in sorted(glob.glob(os.path.join(kb_dir, "*.md"))):
        with open(path, encoding="utf-8") as f:
            raw = f.read()
        sections = re.split(r"^## ", raw, flags=re.M)[1:]  # [0] is the file intro, skip it
        for section in sections:
            title, _, body = section.partition("\n")
            body = body.strip()
            if len(body) <= max_chars:
                chunks.append(Chunk(title.strip(), body, os.path.basename(path)))
                continue
            piece = ""
            for para in body.split("\n"):
                if len(piece) + len(para) > max_chars and piece:
                    chunks.append(Chunk(title.strip(), piece.strip(), os.path.basename(path)))
                    piece = ""
                piece += para + "\n"
            if piece.strip():
                chunks.append(Chunk(title.strip(), piece.strip(), os.path.basename(path)))
    return chunks


# ----------------------------------------------------------------------------
# Step B: turn text into vectors, and search them
# ----------------------------------------------------------------------------
class Embedder:
    """Turns text into vectors (numbers) so that similar meanings end up close together."""

    def __init__(self, model_name=EMBED_MODEL):
        from sentence_transformers import SentenceTransformer  # imported here so tests can skip it
        self.model = SentenceTransformer(model_name)

    def encode(self, texts):
        vecs = self.model.encode(list(texts), normalize_embeddings=True)
        return np.asarray(vecs, dtype="float32")


class Retriever:
    """FAISS index over the chunks. Vectors are normalised, so inner product = cosine similarity."""

    def __init__(self, chunks, embedder):
        import faiss
        self.chunks = chunks
        self.embedder = embedder
        vectors = embedder.encode([f"{c.title}. {c.text}" for c in chunks])
        self.index = faiss.IndexFlatIP(vectors.shape[1])
        self.index.add(vectors)

    def search(self, query, k=3):
        k = min(k, len(self.chunks))
        scores, ids = self.index.search(self.embedder.encode([query]), k)
        return [(self.chunks[i], float(s)) for s, i in zip(scores[0], ids[0]) if i != -1]


# ----------------------------------------------------------------------------
# Step C: turn a detection event into a search query
# ----------------------------------------------------------------------------
def event_to_query(event):
    """
    event example:
      {"type": "loitering", "duration_s": 95, "location": "hostel gate", "time": "23:40"}
    type is one of: loitering, closed_hours, unattended_object, circling, crowd, emergency
    """
    phrases = {
        "loitering": "a person is loitering and staying in one spot",
        "closed_hours": "a person is present while the place is closed",
        "unattended_object": "an unattended bag or object has been left alone",
        "circling": "the same person keeps passing the camera again and again",
        "crowd": "a crowd of people is gathering",
        "emergency": "someone appears hurt or there is a fire",
    }
    parts = [phrases.get(event.get("type"), event.get("type", "something unusual was detected"))]
    if event.get("location"):
        parts.append(f"at {event['location']}")
    if event.get("time"):
        parts.append(f"at {event['time']}")
        try:
            hour = int(str(event["time"]).split(":")[0])
            if hour >= 22 or hour < 6:
                parts.append("during night hours")
        except ValueError:
            pass
    if event.get("duration_s"):
        parts.append(f"for {int(event['duration_s'])} seconds")
    return " ".join(parts)


# ----------------------------------------------------------------------------
# Step D: generation with Groq (+ offline fallback)
# ----------------------------------------------------------------------------
SYSTEM_PROMPT = """You are the voice of AI Guardian, a small security robot.
Use ONLY the protocol excerpts you are given. Do not invent rules.
The robot never touches, chases or confronts anyone, and never accuses anyone of a crime.
If the excerpts do not cover the situation, choose "alert_human".
Reply with JSON only, with exactly these keys:
  "spoken": one or two short, polite sentences the robot says out loud (in {language}),
  "action": one of "announce", "alert_human", "log_only",
  "log": one short line for the incident log (English)."""


def _get_groq_key():
    """Reads GROQ_API_KEY from your config.py. Falls back to an environment variable."""
    try:
        import config
        return config.GROQ_API_KEY
    except (ImportError, AttributeError):
        return os.environ["GROQ_API_KEY"]


def groq_llm(system, user):
    """Calls Groq. Raises an error if there is no key or the call fails, and the caller falls back."""
    from groq import Groq
    client = Groq(api_key=_get_groq_key())
    resp = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
        temperature=0.2,
        max_tokens=1024,  # reasoning models spend tokens thinking, so leave room
    )
    return resp.choices[0].message.content


def fallback_from_chunk(chunk, language):
    """No LLM available: read the Say / Robot action lines straight from the best protocol."""
    lang = "Marathi" if language == "Marathi" else "English"
    say = re.search(rf"Say \({lang}\):\s*(.+)", chunk.text)
    act = re.search(r"Robot action:\s*(\w+)", chunk.text)
    return {
        "spoken": say.group(1).strip() if say else "A human is being alerted.",
        "action": act.group(1) if act and act.group(1) in ACTIONS else "alert_human",
        "log": f"Fallback protocol used: {chunk.title}",
    }


def parse_llm_json(raw):
    match = re.search(r"\{.*\}", raw or "", flags=re.S)  # first {...} block, ignoring fences or extra words
    data = json.loads(match.group(0) if match else raw)
    if data.get("action") not in ACTIONS:
        data["action"] = "alert_human"  # unknown action -> safest option
    data["spoken"] = str(data.get("spoken", "")).strip() or "A human is being alerted."
    data["log"] = str(data.get("log", "")).strip()
    return data


# ----------------------------------------------------------------------------
# The class your robot code will use
# ----------------------------------------------------------------------------
class GuardianRAG:
    def __init__(self, embedder=None, llm=None, language="English", cooldown_s=60, top_k=3, min_score=0.15):
        self.chunks = load_chunks()
        self.retriever = Retriever(self.chunks, embedder or Embedder())
        self.llm = llm or groq_llm
        self.language = language          # "English" or "Marathi"
        self.cooldown_s = cooldown_s      # protects the free Groq quota from repeated events
        self.top_k = top_k
        self.min_score = min_score        # below this, we trust no protocol and alert a human
        self._last_fired = {}

    def respond(self, event):
        """Returns a dict {spoken, action, log, sources}, or None if still in cooldown."""
        key = (event.get("type"), event.get("location"))
        now = time.time()
        if now - self._last_fired.get(key, 0) < self.cooldown_s:
            return None
        self._last_fired[key] = now

        query = event_to_query(event)
        hits = self.retriever.search(query, self.top_k)
        if not hits or hits[0][1] < self.min_score:
            return {"spoken": "I am not sure what is happening. I am alerting a human.",
                    "action": "alert_human", "log": f"No matching protocol for: {query}", "sources": []}

        excerpts = "\n\n".join(f"[{c.title}]\n{c.text}" for c, _ in hits)
        user = f"Event: {query}\n\nProtocol excerpts:\n{excerpts}"
        try:
            result = parse_llm_json(self.llm(SYSTEM_PROMPT.format(language=self.language), user))
        except Exception as err:  # no key, no internet, rate limit, bad JSON ...
            print(f"[guardian_rag] LLM unavailable ({type(err).__name__}): {str(err)[:300]}; using fallback.")
            result = fallback_from_chunk(hits[0][0], self.language)
        result["sources"] = [c.title for c, _ in hits]
        return result


if __name__ == "__main__":
    demo_events = [
        {"type": "loitering", "duration_s": 130, "location": "hostel gate", "time": "14:10"},
        {"type": "closed_hours", "location": "computer lab", "time": "23:45"},
        {"type": "unattended_object", "duration_s": 420, "location": "college corridor", "time": "11:30"},
    ]
    guardian = GuardianRAG()
    for ev in demo_events:
        out = guardian.respond(ev)
        print("\nEVENT :", ev)
        print("RESULT:", json.dumps(out, ensure_ascii=False, indent=2))
        if out:
            print("SPOKEN:", out["spoken"])  # in your project, pass this to your voice.py function