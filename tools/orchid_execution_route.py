#!/usr/bin/env python3
import json,sys
from pathlib import Path
A=Path(sys.argv[1])
timeline=json.loads((A/"main-film-timeline.json").read_text())
dossiers=json.loads((A/"main-route-dossier.json").read_text())
entries=timeline["entries"]; by={e["label"]:e for e in entries}; order={e["label"]:i for i,e in enumerate(entries)}
picks={d["choice_label"]:d.get("draft_structural_pick") for d in dossiers if d.get("draft_structural_pick")}
# Use explicit graph when present in the analysis package.
edges=[]
ep=A/"edges.csv"
if ep.exists():
 import csv
 with ep.open() as f: edges=list(csv.DictReader(f))
graph={}
for x in edges:
 if x.get("from") in by and x.get("to") in by: graph.setdefault(x["from"],[]).append(x["to"])
# Conservative execution traversal. At a locked critical choice, only the selected
# target is traversed. Else explicit outgoing edges are followed; when no explicit
# edge exists, fall through to the next chronological story label.
start=entries[0]["label"]; seen=set(); stack=[start]
while stack:
 n=stack.pop()
 if n in seen or n not in by: continue
 seen.add(n)
 if n in picks and picks[n] in by:
  nxt=[picks[n]]
 else:
  nxt=list(dict.fromkeys(graph.get(n,[])))
  if not nxt:
   i=order[n]
   nxt=[entries[i+1]["label"]] if i+1<len(entries) else []
 for x in reversed(nxt):
  if x not in seen: stack.append(x)
selected=[dict(e) for e in entries if e["label"] in seen]
excluded=[e["label"] for e in entries if e["label"] not in seen]
runtime=round(sum(float(e.get("duration_seconds") or 0) for e in selected),2)
out={"version":2,"policy":"execution-aware selected route; runtime is not capped",
 "entry_label":start,"critical_choices":len(picks),"selected_entries":len(selected),
 "excluded_unreachable_entries":len(excluded),"runtime_seconds":runtime,
 "runtime_hours":round(runtime/3600,3),"selected_branch_targets":picks,
 "excluded_labels":excluded,"entries":selected}
(A/"main-route-execution-manifest.json").write_text(json.dumps(out,indent=2))
print("Execution entry label:",start)
print("Locked critical choices:",len(picks))
print("Execution-reachable entries:",len(selected))
print("Excluded unreachable entries:",len(excluded))
print("Execution-aware runtime seconds:",runtime)
print("Execution-aware runtime hours:",round(runtime/3600,3))
