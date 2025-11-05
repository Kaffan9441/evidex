import os, sys, json, requests, textwrap

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = os.getenv("OLLAMA_TEXT_MODEL", "phi3:mini")  # e.g. set to "mistral:7b" or "llama3.1:8b"

def call_ollama(prompt: str) -> str:
    payload = {
        "model": MODEL,
        "prompt": prompt,
        "stream": False,
        "format": "json"  # ask Ollama to return valid JSON
    }
    r = requests.post(OLLAMA_URL, json=payload, timeout=180)
    r.raise_for_status()
    return r.json().get("response", "")

def make_prompt(ocr_text: str, cv_ctx: dict, client_profile: dict) -> str:
    schema = {
      "ts": "<time string exactly as present (or null)>",
      "speaker": "Client | Other | Unknown",
      "from_client": "true | false | null",
      "message": "<cleaned text>"
    }
    instr = f"""
You are Evidex, a legal evidence parser. Input is OCR text from a smartphone screenshot plus a layout JSON.

Return a SINGLE valid JSON value: an array of message objects matching this schema exactly:
{json.dumps(schema, ensure_ascii=False)}

Rules:
- Use the layout JSON to confirm it's chat; ignore UI artifacts like "Read/Delivered" or app chrome.
- Keep timestamps exactly as seen if present, else null.
- Use the client profile for speaker attribution; if unsure, speaker="Unknown" and from_client=null.
- Merge obvious OCR fragments into one line.
- Output ONLY the JSON array. No prose, no code fences.

LayoutJSON={json.dumps(cv_ctx, ensure_ascii=False)}
ClientProfile={json.dumps(client_profile, ensure_ascii=False)}

OCR_TEXT_START
{ocr_text}
OCR_TEXT_END
""".strip()
    return instr

def main():
    if not (os.path.exists("last_best_ocr.txt") and os.path.exists("last_cv.json")):
        print("Run `python evidex_probe.py samples/sms1.png` first.")
        sys.exit(1)

    with open("last_best_ocr.txt", "r", encoding="utf-8") as f:
        ocr_text = f.read()
    with open("last_cv.json", "r", encoding="utf-8") as f:
        cv_ctx = json.load(f)

    client_profile = {
        "client_name": "Affan Khan",
        "aliases": ["Affan"],
        "phone_numbers": [],
        "side_hint": "client likely left side if bubbles alternate"
    }

    prompt = make_prompt(ocr_text, cv_ctx, client_profile)
    resp = call_ollama(prompt).strip()

    try:
        data = json.loads(resp)
        if isinstance(data, dict) and "messages" in data and isinstance(data["messages"], list):
            items = data["messages"]
        elif isinstance(data, list):
            items = data
        else:
            items = []
    except json.JSONDecodeError:
        items = []

    os.makedirs("out", exist_ok=True)
    with open("out/chronology.jsonl", "w", encoding="utf-8") as f:
        for obj in items:
            f.write(json.dumps(obj, ensure_ascii=False) + "\n")
    with open("out/tmp_response.txt", "w", encoding="utf-8") as f:
        f.write(resp)

    print(f"✅ Wrote {len(items)} messages → out/chronology.jsonl")
    if not items:
        print("Model returned non-JSON or empty. See out/tmp_response.txt")
    
if __name__ == "__main__":
    main()
