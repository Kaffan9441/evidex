from PIL import Image
import pytesseract
import easyocr
import numpy as np
import shutil, sys, os

IMG_PATH = "samples/sms1.png"

# --- sanity checks ---
if not os.path.exists(IMG_PATH):
    print(f"❌ Can't find {IMG_PATH}. Put a screenshot there and try again.")
    sys.exit(1)

if not shutil.which("tesseract"):
    print("❌ Tesseract not found on PATH. Install with Homebrew and try again.")
    sys.exit(1)

# --- Tesseract (great on clean printed text) ---
print("\n===== TESSERACT RESULT =====")
tess_text = pytesseract.image_to_string(Image.open(IMG_PATH), lang="eng")
data = pytesseract.image_to_data(Image.open(IMG_PATH), output_type=pytesseract.Output.DICT)

# SAFE CONFIDENCE CALC: handle ints/strings/missing
conf_vals = []
for c in data.get("conf", []):
    try:
        v = float(c)  # works whether c is "87.5" or 87.5 or "-1"
        if v >= 0:
            conf_vals.append(v)
    except (ValueError, TypeError):
        continue

tess_conf = round(sum(conf_vals)/len(conf_vals), 2) if conf_vals else 0.0
print(tess_text.strip())
print(f"\n[Tesseract mean word confidence ~ {tess_conf}%]")

# --- EasyOCR ---
print("\n===== EASYOCR RESULT =====")
reader = easyocr.Reader(['en'], gpu=False)  # CPU is fine
results = reader.readtext(IMG_PATH, detail=1, paragraph=True)

easy_text_lines, easy_confs = [], []
for bbox, text, conf in results:
    easy_text_lines.append(text)
    easy_confs.append(conf)
easy_text = "\n".join(easy_text_lines).strip()
easy_conf = round(100 * (sum(easy_confs)/len(easy_confs)), 2) if easy_confs else 0.0

print(easy_text)
print(f"\n[EasyOCR mean line confidence ~ {easy_conf}%]")

# --- summary ---
print("\n===== SUMMARY =====")
print(f"Chars: Tesseract={len(tess_text.strip())}  |  EasyOCR={len(easy_text)}")
print("Tip: Higher confidence + cleaner output wins. Pre-processing next.")
