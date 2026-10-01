#!/usr/bin/env python3
"""Download a pair model, convert it to CTranslate2 int8, and record its
licence and attribution from the catalogue (used at image build time)."""
import json
import os
import subprocess
import sys
import urllib.request

repo, out = os.environ["MODEL_REPO"], os.environ.get("CT2_DIR", "/models/ct2")
subprocess.run(["ct2-transformers-converter", "--model", repo, "--output_dir", out,
                "--quantization", "int8", "--force"], check=True)
req = urllib.request.Request("https://windytranslate.com/models.json",
                             headers={"User-Agent": "windytranslate-examples/1.0"})
models = json.load(urllib.request.urlopen(req, timeout=60))["models"]
m = next((m for m in models if m["repo"] == repo), None)
if m is None:
    sys.exit(f"{repo} is not in the catalogue")
info = {k: m.get(k) for k in ("repo", "name", "licence", "attribution", "baseModel", "score")}
info["page"] = f"https://windytranslate.com/models/{m['id']}"
json.dump(info, open(os.path.join(out, "windy_model.json"), "w"), indent=2)
open(os.path.join(out, "NOTICE"), "w").write(m.get("notice") or m["attribution"])
print(f"prepared {repo} ({info['licence']})")
