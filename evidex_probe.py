import os, sys, json, shutil
from PIL import Image
import pytesseract, easyocr

from cv_detect import classify_layout_cv
from preprocess import preprocess_for_ocr

def mean_tesseract_conf(image):
    data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
    vals = []
    for c in data.get("conf", []):
        try:
            v = float(c)
            if v >= 0: vals.append(v)
        except: pass
    return round(sum(vals)/len(vals), 2) if vals else 0.0

def run_easyocr(path):
    reader = easyocr.Reader(['en'], gpu=False)
    results = reader.readtext(path, detail=1, paragraph=True)

    lines, confs = [], []
    for item in results:
        if isinstance(item, (list, tuple)):
            if len(item) == 3:
                _, text, conf = item               # (bbox, text, conf)
            elif len(item) == 2:
                _, text = item                     # (bbox, text)
                conf = 0.0
            else:
                continue
            lines.append(text)
            try:
                confs.append(float(conf))
            except Exception:
                pass

    text = "\n".join(lines).strip()
    conf = round(100.0 * (sum(confs) / len(confs)), 2) if confs else 0.0
    return text, conf

def main():
    img_path = sys.argv[1] if len(sys.argv) > 1 else "samples/sms1.png"
    if not os.path.exists(img_path):
        print(f"❌ Can't find {img_path}."); sys.exit(1)

    # 1) CV
    cv_json = classify_layout_cv(img_path)
    print("\n===== CV LAYOUT JSON ====="); print(json.dumps(cv_json, indent=2))
    with open('last_cv.json', 'w') as f: json.dump(cv_json, f, indent=2)

    # 2) RAW OCR
    if not shutil.which("tesseract"):
        print("\n❌ Tesseract not found. brew install tesseract"); sys.exit(1)

    print("\n===== TESSERACT (RAW) =====")
    pil_raw = Image.open(img_path)
    tess_raw_text = pytesseract.image_to_string(pil_raw, lang="eng", config="--psm 6")
    tess_raw_conf = mean_tesseract_conf(pil_raw)
    print(tess_raw_text.strip()); print(f"\n[Tesseract RAW mean word confidence ~ {tess_raw_conf}%]")

    print("\n===== EASYOCR (RAW) =====")
    easy_raw_text, easy_raw_conf = run_easyocr(img_path)
    print(easy_raw_text); print(f"\n[EasyOCR RAW mean line confidence ~ {easy_raw_conf}%]")

    # 3) PREPROCESS → OCR
    print("\n===== PREPROCESS → path & stats =====")
    prep_path, stats = preprocess_for_ocr(img_path)
    print(f"Preprocessed: {prep_path}  (deskew ~ {stats['deskew_deg']}°)")

    print("\n===== TESSERACT (PREP) =====")
    from PIL import Image as _I
    pil_prep = _I.open(prep_path)
    tess_prep_text = pytesseract.image_to_string(pil_prep, lang="eng", config="--psm 6")
    tess_prep_conf = mean_tesseract_conf(pil_prep)
    print(tess_prep_text.strip()); print(f"\n[Tesseract PREP mean word confidence ~ {tess_prep_conf}%]")

    print("\n===== EASYOCR (PREP) =====")
    easy_prep_text, easy_prep_conf = run_easyocr(prep_path)
    print(easy_prep_text); print(f"\n[EasyOCR PREP mean line confidence ~ {easy_prep_conf}%]")

    # 4) pick best & save
    choices = [
        ("tesseract-raw",  tess_raw_conf,  tess_raw_text),
        ("tesseract-prep", tess_prep_conf, tess_prep_text),
        ("easyocr-raw",    easy_raw_conf,  easy_raw_text),
        ("easyocr-prep",   easy_prep_conf, easy_prep_text),
    ]
    best_engine, best_conf, best_text = max(choices, key=lambda x: x[1])
    print("\n===== SUMMARY =====")
    print(f"CV type: {cv_json.get('type')} (conf {cv_json.get('confidence')})")
    print(f"Best OCR: {best_engine}  (tess_raw {choices[0][1]}% | tess_prep {choices[1][1]}% | easy_raw {choices[2][1]}% | easy_prep {choices[3][1]}%)")
    with open('last_best_ocr.txt','w',encoding='utf-8') as f: f.write(best_text)
    print("Saved best OCR text → last_best_ocr.txt ; saved CV JSON → last_cv.json")

if __name__ == "__main__":
    main()
