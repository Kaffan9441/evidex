import sys, json
from cv_detect import classify_layout_cv

if len(sys.argv) < 2:
    print("Usage: python cv_probe.py path/to/image.png")
    sys.exit(1)

res = classify_layout_cv(sys.argv[1])
print(json.dumps(res, indent=2))
