#!/usr/bin/env python3
"""Translate text with the best Windstorm Labs pair model, locally.

  pip install -r requirements.txt
  python3 translate.py en fr "Where is the train station?"

The model is downloaded once from Hugging Face, then everything runs on your
machine. Multi-sentence text is split into sentences first: small translation
models drop or invent sentences when a whole paragraph is one input.
"""
import re
import sys

from transformers import MarianMTModel, MarianTokenizer

from find_model import candidates, load


def sentences(text):
    """A simple splitter: sentence-ending punctuation followed by a space."""
    return [s for s in re.split(r"(?<=[.!?。！？])\s+", text.strip()) if s]


def main():
    if len(sys.argv) < 4:
        sys.exit(__doc__)
    src, tgt, text = sys.argv[1], sys.argv[2], " ".join(sys.argv[3:])
    found = [m for m in candidates(load(), src, tgt) if m.get("library") == "transformers"]
    if not found:
        sys.exit(f"No transformers model for {src} -> {tgt}; see https://windytranslate.com/languages "
                 "(some pairs ship as CTranslate2 builds, see ../server)")
    m = found[0]
    if m.get("multiTarget"):
        sys.exit(f"{m['repo']} is multi-target; see its page for the >>xxx<< target token: "
                 f"https://windytranslate.com/models/{m['id']}")
    sub = {"subfolder": m["subfolder"]} if m.get("subfolder") else {}
    tok = MarianTokenizer.from_pretrained(m["repo"], **sub)
    model = MarianMTModel.from_pretrained(m["repo"], **sub)
    batch = tok(sentences(text), return_tensors="pt", padding=True)
    out = model.generate(**batch, num_beams=4, max_new_tokens=256)
    print(" ".join(tok.batch_decode(out, skip_special_tokens=True)))
    print(f"\n[{m['repo']} · {m.get('licence')} · https://windytranslate.com/models/{m['id']}]", file=sys.stderr)


if __name__ == "__main__":
    main()
