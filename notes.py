#!/usr/bin/env python3
"""Read the notes Andrew and Amanda left on the play site.
   python3 notes.py         print them
   python3 notes.py clear   archive them to notes-archive.jsonl (kept out of git), then empty the list"""
import json, pathlib, sys, time, urllib.request
R = pathlib.Path(__file__).parent
KEY = (R / ".notes-key").read_text().strip()
URL = "https://api.jobhubgo.com/api/yam/" + KEY
d = json.load(urllib.request.urlopen(URL)).get("data") or {}
cs = d.get("comments", [])
if sys.argv[1:] == ["clear"]:
    with open(R / "notes-archive.jsonl", "a") as f:
        for c in cs: f.write(json.dumps(dict(c, cleared=time.strftime("%Y-%m-%dT%H:%M"))) + "\n")
    body = json.dumps({"data": {"comments": []}, "updatedAt": int(time.time() * 1000)}).encode()
    print(urllib.request.urlopen(urllib.request.Request(URL, body, {"Content-Type": "application/json"}, method="PUT")).read().decode()[:60])
else:
    v = json.loads((R / "version.json").read_text())["v"]
    print(f"{len(cs)} note(s), site is on version {v}")
    for c in sorted(cs, key=lambda c: (c["i"], c["at"])):
        old = "" if c.get("v") == v else f"  (left on version {c.get('v')}, match on the quote)"
        print(f'\n{c["who"]}, {c["at"][:16]}{old}\n  "{c["quote"]}"\n  -> {c["text"]}')
