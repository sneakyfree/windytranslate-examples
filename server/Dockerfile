# Self-hosted translation server for one Windstorm Labs pair model (CPU, int8).
#   docker build --build-arg MODEL_REPO=WindyTranslate/translate-en-fr -t wt-en-fr server/
#   docker run --rm -p 8080:8080 wt-en-fr
#   curl -s localhost:8080/translate -H 'Content-Type: application/json' -d '{"text":"Where is the train station?"}'
FROM python:3.11-slim
ARG MODEL_REPO=WindyTranslate/translate-tc-big-en-fr
ENV MODEL_REPO=${MODEL_REPO} CT2_DIR=/models/ct2 HF_HOME=/models/hf PORT=8080
RUN pip install --no-cache-dir "ctranslate2>=4.4,<5" "transformers>=4.40,<5" sentencepiece sacremoses \
    && pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu
WORKDIR /app
COPY prepare.py server.py ./
# Convert once at build time; the tokenizer stays cached in HF_HOME, so the
# running container needs no network.
RUN python prepare.py && python -c "import os; from transformers import AutoTokenizer; AutoTokenizer.from_pretrained(os.environ['MODEL_REPO'])"
ENV HF_HUB_OFFLINE=1
EXPOSE 8080
CMD ["python", "server.py"]
