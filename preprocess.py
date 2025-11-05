import os, cv2, numpy as np

def _deskew(gray):
    coords = np.column_stack(np.where(gray < 250))
    if coords.size == 0:
        return gray, 0.0
    rect = cv2.minAreaRect(coords)
    angle = rect[-1]
    angle = -(90 + angle) if angle < -45 else -angle
    (h, w) = gray.shape[:2]
    M = cv2.getRotationMatrix2D((w//2, h//2), angle, 1.0)
    rot = cv2.warpAffine(gray, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
    return rot, float(angle)

def preprocess_for_ocr(in_path: str, out_path: str | None = None):
    img = cv2.imread(in_path)
    if img is None:
        raise FileNotFoundError(in_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8)).apply(gray)
    gray = cv2.GaussianBlur(gray, (3,3), 0)
    rotated, angle = _deskew(gray)
    bin_img = cv2.adaptiveThreshold(rotated, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                    cv2.THRESH_BINARY, 31, 15)
    bin_img = cv2.morphologyEx(bin_img, cv2.MORPH_CLOSE, np.ones((1,1), np.uint8), iterations=1)
    if out_path is None:
        root, _ = os.path.splitext(in_path)
        out_path = f"{root}.prep.png"
    cv2.imwrite(out_path, bin_img)
    return out_path, {"deskew_deg": round(angle, 2)}
