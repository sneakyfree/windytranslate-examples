#!/usr/bin/env python3
"""A small self-hosted translation server for one Windstorm Labs pair model.

CTranslate2 (int8) for speed, the model's own tokenizer, standard-library HTTP.
Your text never leaves the machine.

  POST /translate   {"text": "..."}  ->  {"translation": "...", "model": "...", "sentences": n}
  GET  /model       licence, attribution and catalogue page of the served model
  GET  /health      {"status": "ok"}

Env: MODEL_REPO (e.g. WindyTranslate/translate-en-fr), CT2_DIR (converted
model, default /models/ct2), PORT (default 8080), THREADS (default 4).
"""
import json
import os
import re
import signal
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from threading import Lock

import ctranslate2
from transformers import AutoTokenizer

REPO = os.environ["MODEL_REPO"]
CT2_DIR = os.environ.get("CT2_DIR", "/models/ct2")
PORT = int(os.environ.get("PORT", "8080"))
MAX_CHARS = 5000

tokenizer = AutoTokenizer.from_pretrained(os.environ.get("TOKENIZER_DIR", REPO))
translator = ctranslate2.Translator(CT2_DIR, device="cpu", compute_type="int8",
                                    intra_threads=int(os.environ.get("THREADS", "4")))
lock = Lock()
INFO = {"repo": REPO, "page": f"https://windytranslate.com/models/{REPO.split('/', 1)[1]}"}
try:
    INFO.update(json.load(open(os.path.join(CT2_DIR, "windy_model.json"))))
except OSError:
    pass


def split(text):
    """One sentence per input: small pair models drop or invent sentences when
    given a whole paragraph. Line breaks are kept."""
    lines = text.split("\n")
    return [[s for s in re.split(r"(?<=[.!?])\s+|(?<=[。！？])\s*", line.strip()) if s.strip()] for line in lines]


def translate(text):
    lines = split(text)
    flat = [s for line in lines for s in line]
    if not flat:
        return "", 0
    tokens = [tokenizer.convert_ids_to_tokens(tokenizer.encode(s)) for s in flat]
    with lock:
        results = translator.translate_batch(tokens, beam_size=4, max_decoding_length=256)
    outs = iter(tokenizer.decode(tokenizer.convert_tokens_to_ids(r.hypotheses[0]), skip_special_tokens=True)
                for r in results)
    return "\n".join(" ".join(next(outs) for _ in line) for line in lines), len(flat)


class Handler(BaseHTTPRequestHandler):
    def _send(self, code, body):
        data = json.dumps(body, ensure_ascii=False).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        if self.path == "/health":
            return self._send(200, {"status": "ok"})
        if self.path == "/model":
            return self._send(200, INFO)
        self._send(404, {"error": "not found"})

    def do_POST(self):
        if self.path != "/translate":
            return self._send(404, {"error": "not found"})
        try:
            body = json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0))) or b"{}")
            text = body["text"]
            if not isinstance(text, str) or not text.strip() or len(text) > MAX_CHARS:
                raise ValueError
        except (ValueError, KeyError, json.JSONDecodeError):
            return self._send(400, {"error": f"send JSON {{\"text\": \"...\"}} with 1-{MAX_CHARS} characters"})
        out, n = translate(text)
        self._send(200, {"translation": out, "model": REPO, "sentences": n})

    def log_message(self, fmt, *args):  # no request text in logs
        pass


if __name__ == "__main__":
    signal.signal(signal.SIGTERM, lambda *_: sys.exit(0))  # PID 1 in a container: stop promptly
    print(f"serving {REPO} on :{PORT}", flush=True)
    ThreadingHTTPServer(("0.0.0.0", PORT), Handler).serve_forever()
