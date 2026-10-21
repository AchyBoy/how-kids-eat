#!/usr/bin/env python3
"""Build the play site.
   python3 build.py         rebuild play.html + the PDF, same version
   python3 build.py --bump  new version (do this for every change people should see)
Then: git add -A && git commit -m "..." && git push   (GitHub Pages serves it in about a minute)
Source is src/: body.html is the script, print-head.html the print styles,
screen.css the phone styles, notes.js the note pencils."""
import json, pathlib, subprocess, sys, datetime
R = pathlib.Path(__file__).parent
S = R / "src"
vf = R / "version.json"
ver = json.loads(vf.read_text()) if vf.exists() else {"v": 0}
if "--bump" in sys.argv or ver["v"] == 0:
    ver["v"] += 1
ver["updated"] = datetime.date.today().strftime("%B %-d, %Y")
vf.write_text(json.dumps(ver) + "\n")
FRESH = ('<script id="fresh">var BUILD=%d;(function(){if(location.protocol==="file:")return;'
         'fetch("version.json?t="+Date.now(),{cache:"no-store"}).then(function(r){return r.json()}).then(function(j){'
         'if(!j||!j.v||j.v===BUILD)return;var k="hke-fresh-"+j.v;try{if(sessionStorage.getItem(k))return;sessionStorage.setItem(k,"1")}catch(e){}'
         'var u=new URL(location.href);u.searchParams.set("v",j.v);location.replace(u.toString())}).catch(function(){})})();</script>') % ver["v"]

head = (S / "print-head.html").read_text().replace(
    '<meta charset="utf-8">', '<meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1">\n' + FRESH, 1)
nav = ('<div class="topnav"><a href="./">&larr; How Kids Eat</a>'
       f'<a href="How-Kids-Eat.pdf?v={ver["v"]}" download="How Kids Eat.pdf">Download PDF</a></div>\n<div id="notesbar"></div>\n')
html = (head + (S / "screen.css").read_text() + "</style>\n</head>\n<body>\n" + nav
        + (S / "body.html").read_text().replace('<span class="stamp" id="stamp"></span>', f'<span class="stamp" id="stamp">Version {ver["v"]}, updated {ver["updated"]}</span>') + "\n<script>\n" + (S / "notes.js").read_text() + "</script>\n</body>\n</html>\n")
(R / "play.html").write_text(html)

chrome = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
subprocess.run([chrome, "--headless", "--disable-gpu", "--disable-background-networking", "--no-pdf-header-footer",
                f"--print-to-pdf={R / 'How-Kids-Eat.pdf'}", (R / "play.html").as_uri()], check=True, capture_output=True)
idx = (R / "index.html").read_text()
import re
idx = re.sub(r'How-Kids-Eat\.pdf(\?v=\d+)?"', f'How-Kids-Eat.pdf?v={ver["v"]}"', idx)
idx = re.sub(r'<span id="ver">[^<]*</span>', f'<span id="ver">Version {ver["v"]}, updated {ver["updated"]}</span>', idx)
idx = re.sub(r'<script id="fresh">.*?</script>', '', idx)
idx = idx.replace('<meta charset="utf-8">', '<meta charset="utf-8">\n' + FRESH, 1)
(R / "index.html").write_text(idx)
print("built version", ver["v"], ver["updated"])
