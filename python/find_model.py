#!/usr/bin/env python3
"""Find the best Windstorm Labs model for a language pair, with its licence.

Standard library only. Reads the public catalogue manifest
(https://windytranslate.com/models.json), the same data behind
https://windytranslate.com/models.

  python3 find_model.py en sw            # best English -> Swahili model
  python3 find_model.py en sw --all      # every candidate, best first
  python3 find_model.py en fr --notice   # also print the NOTICE text to ship
"""
import argparse
import json
import sys
import urllib.request

MANIFEST = "https://windytranslate.com/models.json"


def load(url=MANIFEST):
    req = urllib.request.Request(url, headers={"User-Agent": "windytranslate-examples/1.0"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.load(r)["models"]


def candidates(models, src, tgt):
    """Translation models that cover src -> tgt, best measured score first.
    Unscored models come after scored ones; never treat 'unscored' as good."""
    hits = [m for m in models if m.get("task") == "translation"
            and src in (m.get("srcLangs") or [m.get("src")])
            and tgt in (m.get("tgtLangs") or [m.get("tgt")])]
    def key(m):
        score = (m.get("score") or {}).get("chrf")
        return (score is None, -(score or 0), m.get("multiTarget", False))
    return sorted(hits, key=key)


def describe(m):
    score = m.get("score") or {}
    quality = (f"chrF++ {score['chrf']} ({score.get('band')}) on {score.get('benchmark', 'FLORES-200')}"
               if score.get("chrf") is not None else "not yet scored")
    flag = "" if m.get("licenceStatus") in (None, "matches-upstream") else f"  [licence note: {m['licenceStatus']}]"
    return (f"{m['repo']}\n  {m.get('name', '')}\n  quality: {quality}\n"
            f"  licence: {m.get('licence')}{flag}\n  page:    https://windytranslate.com/models/{m['id']}")


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("src")
    ap.add_argument("tgt")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--notice", action="store_true")
    a = ap.parse_args()
    found = candidates(load(), a.src.lower(), a.tgt.lower())
    if not found:
        sys.exit(f"No model for {a.src} -> {a.tgt}. Browse https://windytranslate.com/languages")
    for m in (found if a.all else found[:1]):
        print(describe(m))
        if a.notice:
            print("\n--- NOTICE (ship this with your product) ---\n" + m.get("notice", m.get("attribution", "")))
        print()


if __name__ == "__main__":
    main()
