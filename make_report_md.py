import sys, json, pathlib

inp = "out/chronology.jsonl"
out = "out/evidence_report.md"
if len(sys.argv) > 1: inp = sys.argv[1]
if len(sys.argv) > 2: out = sys.argv[2]

msgs = []
with open(inp, "r", encoding="utf-8") as f:
    for line in f:
        line=line.strip()
        if not line: continue
        try: msgs.append(json.loads(line))
        except: pass

def esc(s): return (s or "").replace("\r"," ").replace("\n","  \n")

md = ["# Evidex (Lawyer Tool) — Exhibit Timeline", ""]
for i, m in enumerate(msgs, 1):
    ts = m.get("ts")
    sp = m.get("speaker") or "Unknown"
    fc = m.get("from_client")
    msg = esc(m.get("message"))
    who = "Client" if fc is True else ("Other" if fc is False else sp)
    md.append(f"**{i}. {who}**  ")
    md.append(f"- Time: {ts if ts else '—'}  ")
    md.append(f"- Text: {msg}")
    md.append("")

pathlib.Path("out").mkdir(exist_ok=True)
with open(out, "w", encoding="utf-8") as f: f.write("\n".join(md))
print(f"✅ Wrote Markdown → {out}")
