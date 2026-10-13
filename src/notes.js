// Notes on the script. Only someone who opened a link with #c=<key>&n=<name> sees the
// pencils; the key and name are saved in this browser so later visits keep them.
// Notes live in the shared blob store on api.jobhubgo.com, one list for everybody.
(function () {
  const API = "https://api.jobhubgo.com/api/yam/";
  const h = new URLSearchParams(location.hash.slice(1));
  if (h.get("c")) { localStorage.setItem("hke.c", h.get("c")); localStorage.setItem("hke.n", h.get("n") || "Someone"); history.replaceState(null, "", location.pathname); }
  const KEY = localStorage.getItem("hke.c"), WHO = localStorage.getItem("hke.n");
  let V = 0;

  fetch("version.json?t=" + Date.now(), { cache: "no-store" }).then(r => r.json()).then(j => {
    V = j.v;
    const s = document.getElementById("stamp");
    if (s) s.textContent = "Version " + j.v + ", updated " + j.updated;
  }).catch(() => {});

  if (!KEY) return;
  document.body.classList.add("pencils");

  const targets = Array.from(document.querySelectorAll(".line, .dir, .bit, .note li, .cast .row, .scene-head .name"));
  const quote = el => el.textContent.replace(/\s+/g, " ").trim().slice(0, 80);
  let comments = [];

  async function load() {
    try { const j = await (await fetch(API + KEY, { cache: "no-store" })).json(); return (j.data && j.data.comments) || []; } catch { return null; }
  }
  // Read, change, write back, so two people saving at once don't erase each other.
  async function save(change) {
    for (let tries = 0; tries < 3; tries++) {
      const cur = await load();
      if (cur === null) break;
      const next = change(cur);
      const r = await fetch(API + KEY, { method: "PUT", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ data: { comments: next }, updatedAt: Date.now() }) });
      const j = await r.json().catch(() => ({}));
      if (j.ok) { comments = next; draw(); return true; }
    }
    alert("That note did not save. Check your signal and try again.");
    return false;
  }

  targets.forEach((el, i) => {
    const b = document.createElement("button");
    b.className = "pen"; b.textContent = "✎"; b.title = "Add a note";
    b.onclick = async () => {
      const t = prompt("Note on: \"" + quote(el).slice(0, 60) + "\"");
      if (!t || !t.trim()) return;
      await save(cur => cur.concat({ id: Date.now().toString(36) + Math.random().toString(36).slice(2, 6), i, quote: quote(el), text: t.trim(), who: WHO, at: new Date().toISOString(), v: V }));
    };
    el.appendChild(b);
    const box = document.createElement("div");
    box.className = "notes"; box.dataset.i = i;
    el.after(box);
  });

  function draw() {
    document.querySelectorAll(".notes").forEach(b => (b.innerHTML = ""));
    let placed = 0;
    for (const c of comments) {
      // Match on the quote first, the script may have changed since the note was left.
      let i = targets.findIndex(el => quote(el) === c.quote);
      const moved = i < 0;
      if (moved) i = Math.min(c.i, targets.length - 1);
      const box = document.querySelector('.notes[data-i="' + i + '"]');
      if (!box) continue;
      const d = document.createElement("div");
      d.className = "n";
      d.innerHTML = "<b></b><span></span>" + (moved ? '<span class="old"></span>' : "");
      d.querySelector("b").textContent = c.who + ":";
      d.querySelector("span").textContent = c.text;
      if (moved) d.querySelector(".old").textContent = "This line has changed since: \"" + c.quote + "\"";
      if (c.who === WHO) {
        const x = document.createElement("button");
        x.textContent = "Delete";
        x.onclick = () => confirm("Delete this note?") && save(cur => cur.filter(o => o.id !== c.id));
        d.prepend(x);
      }
      box.appendChild(d);
      placed++;
    }
    const bar = document.getElementById("notesbar");
    bar.textContent = "Notes on, as " + WHO + ". Tap ✎ after any line. " + placed + " note" + (placed === 1 ? "" : "s") + " so far.";
  }

  load().then(c => { comments = c || []; draw(); });
})();
