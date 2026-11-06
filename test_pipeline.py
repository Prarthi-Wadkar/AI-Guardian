"""
Offline test: checks chunking, search, query building, JSON parsing, fallback and cooldown
WITHOUT downloading any model or calling Groq. Run: python test_pipeline.py

The fake embedder below only counts shared words, so it is much cruder than the real one.
Passing this test means the plumbing works, not that retrieval quality is good.
"""
import json
import re
import zlib

import numpy as np

import guardian_rag as g


class FakeEmbedder:
    DIM = 512

    def encode(self, texts):
        out = np.zeros((len(texts), self.DIM), dtype="float32")
        for i, t in enumerate(texts):
            for w in re.findall(r"[a-z]+", t.lower()):
                out[i, zlib.crc32(w.encode()) % self.DIM] += 1.0
            n = np.linalg.norm(out[i])
            if n:
                out[i] /= n
        return out


def fake_llm_ok(system, user):
    return json.dumps({"spoken": "Hello, can I help you?", "action": "banana", "log": "test"})


def fake_llm_broken(system, user):
    raise RuntimeError("no internet")


def main():
    chunks = g.load_chunks()
    assert len(chunks) >= 8, f"expected several protocols, got {len(chunks)}"
    print(f"OK  loaded {len(chunks)} chunks")

    q = g.event_to_query({"type": "closed_hours", "location": "computer lab", "time": "23:45"})
    assert "night hours" in q
    print("OK  query:", q)

    bot = g.GuardianRAG(embedder=FakeEmbedder(), llm=fake_llm_ok, cooldown_s=60)
    r = bot.respond({"type": "closed_hours", "location": "computer lab", "time": "23:45"})
    assert r["action"] == "alert_human", r  # unknown action "banana" must become the safe default
    assert r["sources"], r
    print("OK  unknown action coerced to alert_human; sources:", r["sources"])

    assert bot.respond({"type": "closed_hours", "location": "computer lab", "time": "23:46"}) is None
    print("OK  cooldown blocks a repeat event")

    bot2 = g.GuardianRAG(embedder=FakeEmbedder(), llm=fake_llm_broken, language="Marathi")
    r2 = bot2.respond({"type": "unattended_object", "location": "corridor", "time": "11:30", "duration_s": 420})
    assert "बेवारस" in r2["spoken"], r2
    print("OK  fallback speaks Marathi from the protocol:", r2["spoken"])

    bot3 = g.GuardianRAG(embedder=FakeEmbedder(), llm=fake_llm_broken, min_score=0.99)
    r3 = bot3.respond({"type": "weird", "location": "x"})
    assert r3["action"] == "alert_human" and r3["sources"] == []
    print("OK  no-match case alerts a human")

    fenced = '```json\n{"spoken": "Hi", "action": "announce", "log": "x"}\n```'
    assert g.parse_llm_json(fenced)["action"] == "announce"
    print("OK  JSON wrapped in code fences is parsed")

    print("\nAll checks passed.")


if __name__ == "__main__":
    main()