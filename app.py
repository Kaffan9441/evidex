# app.py — Evidex (Lawyer Tool) local UI
import io, os, json, csv, textwrap
from typing import List, Dict, Tuple
import streamlit as st
from PIL import Image
import numpy as np
import cv2
import pytesseract
import easyocr
import requests

# local modules you already have
from cv_detect import classify_layout_cv
from preprocess import preprocess_for_ocr

# ------------- Helpers -------------
@st.cache_resource
def get_easyocr_reader():
    return easyocr.Reader(['en'], gpu=False)

def tess_text_and_conf(pil_img: Image.Image) -> Tuple[str, float]:
    data = pytesseract.image_to_data(pil_img, lang="eng", output_type=pytesseract.Output.DICT)
    text = pytesseract.image_to_string(pil_img, lang="eng")
    confs = [int(c) for c in data.get("conf", []) if str(c).isdigit() and int(c) >= 0]
    mean_conf = round(sum(confs) / len(confs), 2) if confs else 0.0
    return text.strip(), mean_conf

def easy_text_and_conf(reader, img_path: str) -> Tuple[str, float]:
    results = reader.readtext(img_path, detail=1, paragraph=True)
    lines, confs = [], []
    for item in results:
        if isinstance(item, (list, tuple)):
            if len(item) == 3:
                _, text, conf = item
            elif len(item) == 2:
                _, text = item
                conf = 0.0
            else:
                continue
            lines.append(text)
            try:
                confs.append(float(conf))
            except Exception:
                pass
    txt = "\n".join(lines).strip()
    mean_conf = round(100.0 * (sum(confs) / len(confs)), 2) if confs else 0.0
    return txt, mean_conf

def best_ocr(img_bytes: bytes, tmp_path: str, use_preprocess: bool = True):
    # Save the upload to disk once (EasyOCR needs a path)
    with open(tmp_path, "wb") as f:
        f.write(img_bytes)

    # 1) CV layout
    cv_json = classify_layout_cv(tmp_path)

    # 2) Tesseract + EasyOCR (raw)
    pil = Image.open(io.BytesIO(img_bytes)).convert("RGB")
    tess_raw_text, tess_raw_conf = tess_text_and_conf(pil)
    reader = get_easyocr_reader()
    easy_raw_text, easy_raw_conf = easy_text_and_conf(reader, tmp_path)

    # 3) Optional pre-processing for OCR
    tess_prep_text = ""; tess_prep_conf = 0.0
    easy_prep_text = ""; easy_prep_conf = 0.0
    prep_path = None
    if use_preprocess:
        prep_path, _meta = preprocess_for_ocr(tmp_path)
        pil_prep = Image.open(prep_path).convert("RGB")
        tess_prep_text, tess_prep_conf = tess_text_and_conf(pil_prep)
        easy_prep_text, easy_prep_conf = easy_text_and_conf(reader, prep_path)

    # 4) Choose the best by confidence
    choices = [
        ("tesseract-raw", tess_raw_conf, tess_raw_text),
        ("tesseract-prep", tess_prep_conf, tess_prep_text),
        ("easyocr-raw",   easy_raw_conf, easy_raw_text),
        ("easyocr-prep",  easy_prep_conf, easy_prep_text),
    ]
    best_engine, best_conf, best_text = max(choices, key=lambda x: x[1])

    details = {
        "tess_raw": tess_raw_conf,
        "tess_prep": tess_prep_conf,
        "easy_raw": easy_raw_conf,
        "easy_prep": easy_prep_conf,
        "best_engine": best_engine,
        "best_conf": best_conf
    }
    return best_text, details, cv_json, prep_path

def call_ollama(model: str, prompt: str) -> str:
    resp = requests.post(
        "http://localhost:11434/api/generate",
        json={"model": model, "prompt": prompt, "stream": False, "format": "json"},
        timeout=180
    )
    resp.raise_for_status()
    return resp.json().get("response", "")

def build_llm_prompt(ocr_text: str, cv_ctx: dict, client_profile: dict) -> str:
    schema = {
      "ts": "<time string exactly as present (or null)>",
      "speaker": "Client | Other | Unknown",
      "from_client": "true | false | null",
      "message": "<cleaned text>"
    }
    return textwrap.dedent(f"""
    You are Evidex, a legal evidence parser. Input is OCR text from a smartphone screenshot plus a layout JSON.

    Return a SINGLE valid JSON value: an array of message objects matching this schema exactly:
    {json.dumps(schema, ensure_ascii=False)}

    Rules:
    - Use the layout JSON to confirm it's chat; ignore UI artifacts like "Read/Delivered" and app chrome.
    - Keep timestamps exactly as present if visible; else null.
    - Use the client profile for speaker attribution; if unsure, speaker="Unknown" and from_client=null.
    - Merge obvious OCR fragments; output ONLY the JSON array (no prose).

    LayoutJSON={json.dumps(cv_ctx, ensure_ascii=False)}
    ClientProfile={json.dumps(client_profile, ensure_ascii=False)}

    OCR_TEXT_START
    {ocr_text}
    OCR_TEXT_END
    """).strip()

def to_jsonl(items: List[Dict]) -> str:
    return "\n".join(json.dumps(obj, ensure_ascii=False) for obj in items)

def to_csv_bytes(items: List[Dict]) -> bytes:
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(["ts","speaker","from_client","message"])
    for r in items:
        w.writerow([r.get("ts"), r.get("speaker"), r.get("from_client"), r.get("message")])
    return buf.getvalue().encode("utf-8")

# ------------- UI -------------
st.set_page_config(page_title="Evidex (Lawyer Tool)", page_icon="📑", layout="wide")
st.title("📑 Evidex — Evidence-to-Report Tool")

colL, colR = st.columns([3,2], gap="large")
with colR:
    st.subheader("Settings")
    model = st.text_input("Ollama model", value=os.getenv("OLLAMA_TEXT_MODEL", "phi3:mini"))
    use_prep = st.checkbox("Use image pre-processing (deskew/threshold)", value=True)
    client_name = st.text_input("Client name", value="Affan Khan")
    aliases = st.text_input("Client aliases (comma-separated)", value="Affan")

with colL:
    st.subheader("Upload screenshots")
    files = st.file_uploader("PNG/JPG images", type=["png","jpg","jpeg"], accept_multiple_files=True)

go = st.button("Process & Build Report", type="primary", disabled=not files)

if go:
    all_items: List[Dict] = []
    debug_rows = []
    out_dir = "out"
    os.makedirs(out_dir, exist_ok=True)

    for i, f in enumerate(files, 1):
        st.write(f"### Image {i}: {f.name}")
        img_bytes = f.read()

        tmp_path = os.path.join(out_dir, f"upload_{i}.png")
        best_text, stats, cv_json, prep_path = best_ocr(img_bytes, tmp_path, use_preprocess=use_prep)

        cols = st.columns(3)
        with cols[0]:
            st.image(Image.open(io.BytesIO(img_bytes)), caption="Original", use_column_width=True)
        if prep_path and os.path.exists(prep_path):
            with cols[1]:
                st.image(prep_path, caption="Preprocessed", use_column_width=True)
        with cols[2]:
            st.code(json.dumps(cv_json, indent=2), language="json")
            st.json(stats)

        # Call LLM to turn OCR into structured messages
        client_profile = {
            "client_name": client_name,
            "aliases": [a.strip() for a in aliases.split(",") if a.strip()],
            "phone_numbers": [],
            "side_hint": "client likely left side if bubbles alternate"
        }
        prompt = build_llm_prompt(best_text, cv_json, client_profile)
        try:
            response = call_ollama(model, prompt).strip()
            data = json.loads(response)
            if isinstance(data, dict) and "messages" in data and isinstance(data["messages"], list):
                items = data["messages"]
            elif isinstance(data, list):
                items = data
            else:
                items = []
        except Exception as e:
            st.error(f"Model error: {e}")
            items = []
            # Save raw for debugging
            with open(os.path.join(out_dir, f"raw_llm_{i}.txt"), "w", encoding="utf-8") as rf:
                rf.write(response if 'response' in locals() else "")

        if items:
            st.success(f"Parsed {len(items)} messages.")
            st.dataframe(items, use_container_width=True)
            all_items.extend(items)
        else:
            st.warning("No messages parsed. Check raw LLM output in out/ folder.")

    # Exports
    if all_items:
        st.divider()
        st.subheader("Downloads")

        jsonl_bytes = to_jsonl(all_items).encode("utf-8")
        st.download_button("⬇️ JSONL (messages)", jsonl_bytes, file_name="chronology.jsonl", mime="application/jsonl")

        csv_bytes = to_csv_bytes(all_items)
        st.download_button("⬇️ CSV (messages)", csv_bytes, file_name="chronology.csv", mime="text/csv")

        # Simple Markdown report
        md_lines = ["# Evidex — Exhibit Timeline", ""]
        for i, m in enumerate(all_items, 1):
            ts = m.get("ts") or "—"
            who = "Client" if m.get("from_client") is True else ("Other" if m.get("from_client") is False else (m.get("speaker") or "Unknown"))
            msg = (m.get("message") or "").replace("\r"," ").replace("\n","  \n")
            md_lines += [f"**{i}. {who}**  ", f"- Time: {ts}  ", f"- Text: {msg}", ""]
        md_bytes = "\n".join(md_lines).encode("utf-8")
        st.download_button("⬇️ Markdown report", md_bytes, file_name="evidence_report.md", mime="text/markdown")

st.caption("Local only. Requires Tesseract, EasyOCR, Ollama running.")
