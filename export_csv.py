import sys, json, csv

def read_jsonl(path):
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line: 
                continue
            try:
                yield json.loads(line)
            except json.JSONDecodeError:
                pass

def main():
    inp = sys.argv[1] if len(sys.argv) > 1 else "out/chronology.jsonl"
    out = sys.argv[2] if len(sys.argv) > 2 else "out/chronology.csv"
    rows = list(read_jsonl(inp))
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["ts","speaker","from_client","message"])
        for r in rows:
            w.writerow([
                r.get("ts"),
                r.get("speaker"),
                r.get("from_client"),
                r.get("message"),
            ])
    print(f"✅ Wrote CSV → {out} ({len(rows)} rows)")

if __name__ == "__main__":
    main()
