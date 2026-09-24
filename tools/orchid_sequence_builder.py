#!/usr/bin/env python3
import json,sys,re
from pathlib import Path
A=Path(sys.argv[1]); m=json.loads((A/"main-route-execution-manifest.json").read_text())
entries=m["entries"]; seq=[]; music=None; visual=None
for e in entries:
 evs=e.get("resolved_events") or e.get("events") or []
 dialogue=e.get("dialogue") or []
 items=[]
 for x in evs:
  line=int(x.get("line") or x.get("source_line") or 0)
  kind=x.get("kind") or x.get("type") or "event"
  items.append((line,0,{"type":"event","event":x}))
 for i,d in enumerate(dialogue):
  line=int(d.get("line") or d.get("source_line") or 0)
  items.append((line,1,{"type":"dialogue","dialogue":d}))
 items.sort(key=lambda z:(z[0],z[1]))
 for _,__,item in items:
  if item["type"]=="event":
   x=item["event"]; k=str(x.get("kind") or x.get("type") or "").lower()
   if k in ("scene","show"): visual=x.get("resolved_path") or x.get("asset") or x.get("name") or visual
   if k=="play" and str(x.get("channel","")).lower()=="music": music=x.get("resolved_path") or x.get("asset") or x.get("name")
   if k=="stop" and str(x.get("channel","")).lower()=="music": music=None
  item["label"]=e["label"]; item["chapter"]=e.get("chapter"); item["visual_state"]=visual; item["music_state"]=music
  seq.append(item)
# Split on chapter changes; these become independently renderable jobs.
chapters=[]; cur=None
for item in seq:
 ch=item.get("chapter") or "unknown"
 if cur is None or cur["chapter"]!=ch:
  cur={"chapter":ch,"sequence":[]}; chapters.append(cur)
 cur["sequence"].append(item)
for i,ch in enumerate(chapters,1):
 ch["part"]=i; ch["event_count"]=sum(x["type"]=="event" for x in ch["sequence"]); ch["dialogue_count"]=sum(x["type"]=="dialogue" for x in ch["sequence"])
out={"version":1,"route_runtime_seconds":m["runtime_seconds"],"route_entries":len(entries),"sequence_items":len(seq),"chapters":chapters,
"render_policy":{"webm_min_cycles":3,"preserve_music_across_labels":True,"chapter_outputs":True,"complete_route":True}}
(A/"main-film-ordered-sequence.json").write_text(json.dumps(out,indent=2))
summary={"chapters":len(chapters),"sequence_items":len(seq),"events":sum(c["event_count"] for c in chapters),"dialogue":sum(c["dialogue_count"] for c in chapters)}
(A/"ordered-sequence-summary.json").write_text(json.dumps(summary,indent=2))
print("Render chapters:",summary["chapters"]); print("Ordered sequence items:",summary["sequence_items"]); print("Ordered events:",summary["events"]); print("Ordered dialogue:",summary["dialogue"])
