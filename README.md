# Evidex (Lawyer Tool)
OCR + CV + LLM → structured chat evidence + CSV/JSONL/Markdown.

## Local
brew install tesseract
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py

## Deploy (Streamlit Cloud)
Push to GitHub, choose `app.py`, then set Secrets:
USE_OLLAMA = 0
LLM_BASE_URL = https://api.openai.com/v1
LLM_API_KEY = <your key>
LLM_MODEL = gpt-4o-mini
