#!/usr/bin/env python3
import json, re, sys
from pathlib import Path

analysis = Path(sys.argv[1])
decompiled = analysis / "decompiled" / "scripts"
timeline_path = analysis / "main-film-timeline.json"
data = json.loads(timeline_path.read_text())
entries = data["entries"]
by_label = {e["label"]: e for e in entries}

label_re = re.compile(r'^\s*label\s+([^\s(:]+)')
say_re = re.compile(r"""^\s*(?:([A-Za-z_][A-Za-z0-9_.]*)\s+)?(["'])(.*?)\2(?:\s+\([^)]*\))?\s*$""")
dialogue = {}
story_files = [p for p in sorted(decompiled.rglob("*.rpy")) if "story" in [x.lower() for x in p.parts]]

for fn in story_files:
    active = None
    for line_no, line in enumerate(fn.read_text(errors="ignore").splitlines(), 1):
        lm = label_re.match(line)
        if lm:
            active = lm.group(1)
            continue
        if not active or active not in by_label:
            continue
        sm = say_re.match(line)
        if not sm:
            continue
        raw = sm.group(3).strip()
        if not raw or re.search(r'\.(?:webp|webm|png|jpe?g|mp3|ogg|opus|wav|mp4)$', raw, re.I):
            continue
        clean = re.sub(r'{[^}]*}', '', raw)
        clean = re.sub(r'\[[^]]*\]', '', clean).strip()
        words = re.findall(r"[A-Za-z0-9_]+(?:[-'][A-Za-z0-9_]+)*", clean)
        if not words:
            continue
        seconds = max(1.6, min(8.0, len(words) / 3.5))
        dialogue.setdefault(active, []).append({
            "speaker": sm.group(1) or "narration",
            "text": raw,
            "source": str(fn),
            "line": line_no,
            "duration_seconds": round(seconds, 2),
        })

count = 0
for e in entries:
    e["dialogue"] = dialogue.get(e["label"], [])
    count += len(e["dialogue"])
    if e["dialogue"]:
        dt = sum(x["duration_seconds"] for x in e["dialogue"])
        e["duration_seconds"] = round(max(float(e.get("duration_seconds") or 0), dt), 2)
        e["editorial_status"] = "dialogue-timed"

runtime = round(sum(float(e.get("duration_seconds") or 0) for e in entries), 2)
data.update({"version": 3, "status": "dialogue-timed structural draft",
             "estimated_runtime_seconds": runtime, "dialogue_lines": count})
timeline_path.write_text(json.dumps(data, indent=2))
summary = {
    "story_files_scanned": len(story_files),
    "dialogue_lines": count,
    "timeline_entries_with_dialogue": sum(bool(e["dialogue"]) for e in entries),
    "estimated_runtime_seconds": runtime,
}
(analysis / "dialogue-timing-summary.json").write_text(json.dumps(summary, indent=2))
print("Story files scanned for dialogue:", len(story_files))
print("Dialogue lines extracted:", count)
print("Timeline entries with dialogue:", summary["timeline_entries_with_dialogue"])
print("Dialogue-aware runtime seconds:", runtime)
