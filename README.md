# Windy Translate examples

Run Windstorm Labs' open translation models on your own machine: find the
right model for a language pair, translate with it, and self-host it behind a
small HTTP server. No API key, no account, and your text never leaves your
machine.

The catalogue (1,660 translation pair models, 3 multilingual models and 66
speech-to-text models, each with its measured score, licence and attribution)
is at **[windytranslate.com](https://windytranslate.com)** and as a single JSON
file at [`windytranslate.com/models.json`](https://windytranslate.com/models.json).
The weights are on Hugging Face under
[WindyTranslate](https://huggingface.co/WindyTranslate).

## 1. Find a model (standard library only)

```bash
python3 python/find_model.py en de
```

```
WindyTranslate/translate-en-de
  English to German
  quality: chrF++ 63.05 (Excellent) on FLORES-200 dev
  licence: CC-BY-4.0
  page:    https://windytranslate.com/models/translate-en-de
```

`--all` lists every candidate, best measured score first (unscored models come
last; "not yet scored" never means good). `--notice` prints the attribution
text to ship with your product.

## 2. Translate locally

```bash
pip install -r python/requirements.txt
python3 python/translate.py en fr "Where is the train station? The museum opens at ten."
```

Text is split into sentences before translation. Small pair models drop or
invent sentences when given a whole paragraph as one input, so don't skip this
step in your own code.

## 3. Self-host a model behind HTTP (Docker, CPU)

```bash
docker build --build-arg MODEL_REPO=WindyTranslate/translate-tc-big-en-fr -t wt-en-fr server/
docker run --rm -p 8080:8080 wt-en-fr
curl -s localhost:8080/translate -H 'Content-Type: application/json' \
     -d '{"text": "Where is the train station?"}'
curl -s localhost:8080/model      # licence, attribution, catalogue page
```

The image converts the model to [CTranslate2](https://github.com/OpenNMT/CTranslate2)
int8 at build time and runs offline afterwards. It ships the model's `NOTICE`
in `/models/ct2/NOTICE`. Request text is never logged.

## Licences: read this before you ship

- **This repository's code** is Apache-2.0 ([LICENSE](LICENSE)).
- **Each model has its own licence**, usually Apache-2.0 or CC-BY-4.0
  (OPUS-MT, Helsinki-NLP, University of Helsinki), sometimes MIT. CC-BY
  requires attribution. Every model page lists the exact licence, the upstream
  model and copy-paste attribution text; `find_model.py --notice` prints it.
- A few models are marked "licence under review" in the catalogue. Don't rely
  on those for commercial use until the note is removed.
- See [windytranslate.com/licensing](https://windytranslate.com/licensing).

## Quality

Scores are a FLORES-200 screening (48 sentences per pair), published for every
scored pair including the weak ones. Method and caveats:
[windytranslate.com/evaluation](https://windytranslate.com/evaluation).

## Hosted API

A hosted API is in early access, free while in beta:
[windytranslate.com/api](https://windytranslate.com/api).

---

From [Windstorm Labs](https://windstormlabs.com), part of the
[Windstorm Institute](https://windstorminstitute.org). Questions:
hello@windytranslate.com.
