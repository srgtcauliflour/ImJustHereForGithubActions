#!/usr/bin/env python3
import json,sys
from pathlib import Path
A=Path(sys.argv[1])
timeline=json.loads((A/"main-film-timeline.json").read_text())
entries=timeline["entries"]
dossiers=json.loads((A/"main-route-dossier.json").read_text())
picks={d["choice_label"]:d.get("draft_structural_pick") for d in dossiers if d.get("draft_structural_pick")}
# Build a conservative first main-route cut: keep chronological story beats,
# annotate the selected branch at critical choices, and never delete a beat
# unless graph evidence explicitly identifies it as an alternate target.
all_targets=set()
for d in dossiers:
    for c in d.get("candidates",[]): all_targets.add(c.get("target"))
selected=set(picks.values())
excluded_targets=all_targets-selected
route=[]
for e in entries:
    x=dict(e)
    x["route_status"]="selected"
    if e["label"] in excluded_targets:
        x["route_status"]="alternate-branch-candidate"
    if e["label"] in picks:
        x["selected_branch_target"]=picks[e["label"]]
    route.append(x)
# Do not destructively remove alternate labels yet; emit both a safe editorial
# manifest and a candidate filtered cut for review/render preparation.
candidate=[x for x in route if x["route_status"]=="selected"]
def runtime(rows):
    return round(sum(float(x.get("duration_seconds") or 0) for x in rows),2)
manifest={
 "version":1,
 "policy":"complete selected route; length is not a constraint",
 "critical_choices":len(dossiers),
 "structural_branch_picks":picks,
 "full_editorial_entries":len(route),
 "candidate_main_route_entries":len(candidate),
 "candidate_runtime_seconds":runtime(candidate),
 "entries":candidate,
}
(A/"main-route-render-manifest.json").write_text(json.dumps(manifest,indent=2))
(A/"route-review.json").write_text(json.dumps({"entries":route,"excluded_target_candidates":sorted(x for x in excluded_targets if x)},indent=2))
print("Critical route decisions:",len(dossiers))
print("Candidate main-route entries:",len(candidate))
print("Alternate branch target candidates:",len(excluded_targets))
print("Candidate dialogue-aware runtime seconds:",runtime(candidate))
