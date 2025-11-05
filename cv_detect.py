import cv2, numpy as np, json

def _binarize(img_bgr):
    """
    1) grayscale  2) contrast boost (CLAHE)  3) light blur
    4) adaptive threshold to ink=WHITE (255), bg=BLACK (0)
    5) remove tiny specks
    """
    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    g2 = clahe.apply(gray)
    blur = cv2.GaussianBlur(g2, (3,3), 0)
    thr = cv2.adaptiveThreshold(
        blur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY_INV, 31, 15
    )
    thr = cv2.morphologyEx(thr, cv2.MORPH_OPEN, np.ones((3,3), np.uint8), iterations=1)
    return thr

def classify_layout_cv(image_path: str) -> dict:
    """
    Layout-only classifier (no OCR/AI). Measures ink density left/center/right
    and component counts to decide: chat / letter / other. Returns strict JSON.
    """
    img = cv2.imread(image_path)
    if img is None:
        return {"type":"other","confidence":0.0,"hints":{"error":"cannot_read_image"}}

    H, W = img.shape[:2]
    thr = _binarize(img)

    # --- DENSITIES -----------------------------------------------------------
    # column ink density normalized to [0..1]
    col_sum = (thr.sum(axis=0) / 255.0) / max(H, 1)
    L = col_sum[:int(0.40*W)].mean() if W > 0 else 0.0
    C = col_sum[int(0.40*W):int(0.60*W)].mean() if W > 0 else 0.0
    R = col_sum[int(0.60*W):].mean() if W > 0 else 0.0

    # --- CONNECTED COMPONENTS ------------------------------------------------
    contours, _ = cv2.findContours(thr, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    areas = [cv2.contourArea(c) for c in contours]
    mid = [a for a in areas if 50 <= a <= 5000]   # ignore specks/huge blocks
    comp_count = len(mid)

    # --- SCORES --------------------------------------------------------------
    # Two-sided bias (alternating bubbles)
    lr_gap   = ((L + R)/2.0) - C                       # >0 when sides > center
    lr_score = float(min(max(lr_gap / 0.05, 0.0), 1.0))

    # Single-side bias (only left or only right visible)
    side_max = max(L, R)
    side_min = min(L, R)
    rel_side_ratio = side_max / (C + 1e-6)             # e.g., 1.15 == 15% heavier than center
    # class as single-sided if dominant side is >=12% over center and the other side is small
    single_side_pattern = (rel_side_ratio >= 1.12) and (side_min <= 0.8 * side_max)
    side_dom_score = float(min(max((rel_side_ratio - 1.0) / 0.20, 0.0), 1.0))  # map 1.00–1.20 → 0–1

    # Components: more mid blobs → more chat-like
    comp_score = float(min(comp_count / 120.0, 1.0))

    # Light bonuses typical of phone chat screenshots
    HWR = H / max(W, 1)                          # portrait if >= ~1.6
    portrait_bonus   = 0.10 if HWR >= 1.6 else 0.0
    many_comp_bonus  = 0.15 if comp_count >= 70 else 0.0

    # Combine chat score (cap at 1.0)
    chat_bias  = max(lr_score, side_dom_score)   # either two-sided or single-sided works
    chat_score = min(1.0, 0.50*chat_bias + 0.35*comp_score + portrait_bonus + many_comp_bonus)

    # Letter score: center heavier + fewer components
    center_gap   = C - ((L + R)/2.0)
    center_score = float(min(max(center_gap / 0.05, 0.0), 1.0))
    few_comps    = 1.0 - comp_score
    letter_score = 0.70*center_score + 0.30*few_comps

    # --- DECISION ------------------------------------------------------------
    if chat_score >= 0.55 and chat_score >= letter_score:
        t, conf = "chat", float(chat_score)
    elif letter_score >= 0.55 and letter_score > chat_score:
        t, conf = "letter", float(letter_score)
    else:
        t, conf = "other", float(max(chat_score, letter_score) * 0.6)

    return {
        "type": t,
        "confidence": round(conf, 2),
        "hints": {
            "left_right_alignment": bool((lr_gap > 0.02) or single_side_pattern),
            "component_count": int(comp_count),
            "densities": {"left": round(L,4), "center": round(C,4), "right": round(R,4)},
            "rel_side_ratio": round(rel_side_ratio, 3),
            "portrait": bool(HWR >= 1.6),
            "image_w": int(W), "image_h": int(H)
        }
    }

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print('Usage: python -m cv_detect path/to/image')
        sys.exit(1)
    print(json.dumps(classify_layout_cv(sys.argv[1]), indent=2))
