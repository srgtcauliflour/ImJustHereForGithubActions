#!/usr/bin/env python3
import json,re,sys
from pathlib import Path

analysis=Path(sys.argv[1])
game=Path(sys.argv[2])
timeline_path=analysis/"main-film-timeline.json"
data=json.loads(timeline_path.read_text())
entries=data["entries"]
by_label={e["label"]:e for e in entries}
label_re=re.compile(r"^\\s*label\\s+([A-Za-z0-9_]+)\\s*:")
say_re=re.compile(r"""^\\s*(?:([A-Za-z_][A-Za-z0-9_.]*)\\s+)?(["\x27])(.*?)\\2(?:\\s+\\([^)]*\\))?\\s*$""")
dialogue={}
for fn in sorted(game.rglob("*.rpy")):
    try:
        rel=fn.relative_to(game)
    except ValueError:
        rel=fn
    if "story" not in [part.lower() for part in rel.parts]:
        continue
    active=None
    for line_no,line in enumerate(fn.read_text(errors="ignore").splitlines(),1):
        m=label_re.match(line)
        if m:
            active=m.group(1); continue
        if not active or active not in by_label: continue
        m=say_re.match(line)
        if not m: continue
        raw=m.group(3).strip()
        if not raw or re.search(r"\\.(webp|webm|png|jpe?g|mp3|ogg|opus|wav|mp4)$",raw,re.I):
            continue
        clean=re.sub(r"{[^}]*}","",raw)
        clean=re.sub(r"\\[[^]]*\\]","",clean).strip()
        words=re.findall(r"[A-Za-z0-9_]+(?:[-'][A-Za-z0-9_]+)*",clean)
        if not words: continue
        secs=max(1.6,min(8.0,len(words)/3.5))
        dialogue.setdefault(active,[]).append({"speaker":m.group(1) or "narration","text":raw,"source":str(fn),"line":line_no,"duration_seconds":round(secs,2)})
count=0
for e in entries:
    e["dialogue"]=dialogue.get(e["label"],[])
    count+=len(e["dialogue"])
    if e["dialogue"]:
        dt=sum(x["duration_seconds"] for x in e["dialogue"])
        e["duration_seconds"]=round(max(float(e.get("duration_seconds") or 0),dt),2)
        e["editorial_status"]="dialogue-timed"
runtime=round(sum(float(e.get("duration_seconds") or 0) for e in entries),2)
data.update({"version":3,"status":"dialogue-timed structural draft","estimated_runtime_seconds":runtime,"dialogue_lines":count})
timeline_path.write_text(json.dumps(data,indent=2))
summary={"dialogue_lines":count,"timeline_entries_with_dialogue":sum(bool(e["dialogue"]) for e in entries),"estimated_runtime_seconds":runtime}
(analysis/"dialogue-timing-summary.json").write_text(json.dumps(summary,indent=2))
print("Dialogue lines extracted:",count)
print("Timeline entries with dialogue:",summary["timeline_entries_with_dialogue"])
print("Dialogue-aware runtime seconds:",runtime)
)
dialogue={}
for fn in sorted(game.rglob("*.rpy")):
    if "story" not in str(fn).lower():
        continue
    active=None
    for line_no,line in enumerate(fn.read_text(errors="ignore").splitlines(),1):
        m=label_re.match(line)
        if m:
            active=m.group(1); continue
        if not active or active not in by_label: continue
        m=say_re.match(line)
        if not m: continue
        raw=m.group(3).strip()
        if not raw or re.search(r"\\.(webp|webm|png|jpe?g|mp3|ogg|opus|wav|mp4)$",raw,re.I):
            continue
        clean=re.sub(r"{[^}]*}","",raw)
        clean=re.sub(r"\\[[^]]*\\]","",clean).strip()
        words=re.findall(r"[A-Za-z0-9_]+(?:[-'][A-Za-z0-9_]+)*",clean)
        if not words: continue
        secs=max(1.6,min(8.0,len(words)/3.5))
        dialogue.setdefault(active,[]).append({"speaker":m.group(1) or "narration","text":raw,"source":str(fn),"line":line_no,"duration_seconds":round(secs,2)})
count=0
for e in entries:
    e["dialogue"]=dialogue.get(e["label"],[])
    count+=len(e["dialogue"])
    if e["dialogue"]:
        dt=sum(x["duration_seconds"] for x in e["dialogue"])
        e["duration_seconds"]=round(max(float(e.get("duration_seconds") or 0),dt),2)
        e["editorial_status"]="dialogue-timed"
runtime=round(sum(float(e.get("duration_seconds") or 0) for e in entries),2)
data.update({"version":3,"status":"dialogue-timed structural draft","estimated_runtime_seconds":runtime,"dialogue_lines":count})
timeline_path.write_text(json.dumps(data,indent=2))
summary={"dialogue_lines":count,"timeline_entries_with_dialogue":sum(bool(e["dialogue"]) for e in entries),"estimated_runtime_seconds":runtime}
(analysis/"dialogue-timing-summary.json").write_text(json.dumps(summary,indent=2))
print("Dialogue lines extracted:",count)
print("Timeline entries with dialogue:",summary["timeline_entries_with_dialogue"])
print("Dialogue-aware runtime seconds:",runtime)
