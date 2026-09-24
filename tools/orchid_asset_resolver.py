#!/usr/bin/env python3
import json,re,sys
from pathlib import Path
analysis=Path(sys.argv[1]); game=Path(sys.argv[2])
timeline=json.loads((analysis/"main-film-timeline.json").read_text())
entries=timeline["entries"]
# Build a case-insensitive stem/name index of every real media asset.
exts={".webp",".webm",".png",".jpg",".jpeg",".gif",".mp4",".mp3",".ogg",".opus",".wav"}
assets=[]
for p in game.rglob("*"):
    if p.is_file() and p.suffix.lower() in exts:
        rel=p.relative_to(game).as_posix()
        assets.append({"path":rel,"stem":p.stem.lower(),"name":p.name.lower(),"ext":p.suffix.lower()})
by_stem={}
for a in assets: by_stem.setdefault(a["stem"],[]).append(a)

# Parse Ren'Py audio aliases from all decompiled scripts.
alias={}
assign=re.compile(r'^\s*(?:define\s+)?(?:audio\.)?([A-Za-z_][A-Za-z0-9_]*)\s*=\s*["\x27]([^"\x27]+)["\x27]')
for fn in (analysis/"decompiled"/"scripts").rglob("*.rpy"):
    for line in fn.read_text(errors="ignore").splitlines():
        m=assign.match(line)
        if m and Path(m.group(2)).suffix.lower() in exts:
            alias[m.group(1).lower()]=m.group(2)

resolved=0; unresolved={}
for e in entries:
    out=[]
    for ev in e.get("events",[]):
        name=ev.get("name")
        if not name: continue
        key=str(name).strip("'\"").lower()
        candidates=[]
        if key in alias:
            candidates=[{"path":alias[key],"via":"audio-alias"}]
        else:
            # scene names commonly map directly to asset stems.
            stem=Path(key).stem
            candidates=[{"path":a["path"],"via":"asset-stem"} for a in by_stem.get(stem,[])]
        if candidates:
            resolved+=1
            out.append({"event":ev,"matches":candidates})
        elif ev.get("type") not in ("hide","stop"):
            unresolved[key]=unresolved.get(key,0)+1
    e["resolved_events"]=out
summary={"asset_files_indexed":len(assets),"audio_aliases":len(alias),
         "resolved_symbolic_events":resolved,"unique_unresolved_symbols":len(unresolved),
         "top_unresolved":sorted(unresolved.items(),key=lambda x:(-x[1],x[0]))[:100]}
timeline["version"]=5; timeline["status"]="symbolic-media-resolved structural draft"
(analysis/"main-film-timeline.json").write_text(json.dumps(timeline,indent=2))
(analysis/"symbolic-media-summary.json").write_text(json.dumps(summary,indent=2))
print("Media assets indexed:",len(assets))
print("Audio aliases resolved:",len(alias))
print("Symbolic events resolved to assets:",resolved)
print("Unique unresolved media symbols:",len(unresolved))
