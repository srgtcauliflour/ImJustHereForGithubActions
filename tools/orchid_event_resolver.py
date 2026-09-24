#!/usr/bin/env python3
import json, re, sys
from pathlib import Path

analysis=Path(sys.argv[1])
root=analysis/"decompiled"/"scripts"
timeline_path=analysis/"main-film-timeline.json"
data=json.loads(timeline_path.read_text())
entries=data["entries"]
by_label={e["label"]:e for e in entries}
label_re=re.compile(r'^\s*label\s+([^\s(:]+)')
scene_re=re.compile(r'^\s*(scene|show|hide)\s+([^\s:]+)')
play_re=re.compile(r'^\s*(play|queue|stop)\s+(music|sound|audio|voice)(?:\s+([^\s]+))?')
voice_re=re.compile(r'^\s*voice\s+([^\s]+)')
pause_re=re.compile(r'^\s*(?:pause|with)\b(.*)$')
events={}
files=0
for fn in sorted(root.rglob("*.rpy")):
    if "story" not in [p.lower() for p in fn.parts]:
        continue
    files+=1; active=None
    for line_no,line in enumerate(fn.read_text(errors="ignore").splitlines(),1):
        m=label_re.match(line)
        if m:
            active=m.group(1); continue
        if not active or active not in by_label: continue
        ev=None
        m=scene_re.match(line)
        if m: ev={"type":m.group(1),"name":m.group(2)}
        else:
            m=play_re.match(line)
            if m: ev={"type":m.group(1),"channel":m.group(2),"name":m.group(3)}
            else:
                m=voice_re.match(line)
                if m: ev={"type":"voice","name":m.group(1)}
                else:
                    m=pause_re.match(line)
                    if m: ev={"type":"timing","command":line.strip()}
        if ev:
            ev.update({"line":line_no,"source":str(fn)})
            events.setdefault(active,[]).append(ev)
for e in entries:
    e["events"]=events.get(e["label"],[])
summary={
 "story_files_scanned":files,
 "timeline_entries":len(entries),
 "timeline_entries_with_events":sum(bool(e["events"]) for e in entries),
 "scene_show_hide_events":sum(sum(x["type"] in ("scene","show","hide") for x in e["events"]) for e in entries),
 "audio_control_events":sum(sum(x["type"] in ("play","queue","stop","voice") for x in e["events"]) for e in entries),
 "timing_transition_events":sum(sum(x["type"]=="timing" for x in e["events"]) for e in entries),
}
data["version"]=4
data["status"]="event-resolved structural draft"
timeline_path.write_text(json.dumps(data,indent=2))
(analysis/"event-resolution-summary.json").write_text(json.dumps(summary,indent=2))
print("Story files scanned for events:",files)
print("Timeline entries with events:",summary["timeline_entries_with_events"])
print("Scene/show/hide events:",summary["scene_show_hide_events"])
print("Audio control events:",summary["audio_control_events"])
print("Timing/transition events:",summary["timing_transition_events"])
