#!/usr/bin/env python3
"""
Sync the signalling modules into the Vercel function's library folder.

`app/public/` is the Vercel project root, so the function cannot import from
`app/server/` (outside the project). The three signalling modules are therefore
copied across. They import each other by bare sibling path (./peer.js,
./helper.js), so a flat copy needs no rewriting — which is what keeps them
verbatim copies of upstream rather than a fork.

Run this after changing anything in app/server/:

    python3 sync-vercel-fn.py

app/public/api/server.js is NOT generated — it is hand-written and is the only
Vercel-specific file. It must never call listen(): Vercel owns the listener and
performs the HTTP Upgrade itself.
"""
import pathlib
import re
import shutil

ROOT = pathlib.Path(__file__).parent
SRC = ROOT / "app" / "server"
DST = ROOT / "app" / "public" / "pn-lib"
MODULES = ["ws-server.js", "peer.js", "helper.js"]

DST.mkdir(parents=True, exist_ok=True)
for name in MODULES:
    src = SRC / name
    if not src.exists():
        raise SystemExit(f"missing upstream module: {src}")
    shutil.copy2(src, DST / name)
    print(f"synced {name}")

# Guard the invariant the whole Vercel deployment depends on: Vercel owns the
# listener, so the function must never bind a port. Comments are stripped first,
# because the file explains this rule and would otherwise trip its own check.
fn = ROOT / "app" / "public" / "api" / "server.js"
body = fn.read_text(encoding="utf-8")
code = re.sub(r"/\*.*?\*/", "", body, flags=re.DOTALL)
code = re.sub(r"^\s*//.*$", "", code, flags=re.MULTILINE)

if re.search(r"\.listen\s*\(", code):
    raise SystemExit("!! api/server.js must not call listen() on Vercel")
if "'../pn-lib/ws-server.js'" not in code and '"../pn-lib/ws-server.js"' not in code:
    raise SystemExit("!! api/server.js does not import the signalling server from ../pn-lib")
if "export default server" not in code:
    raise SystemExit("!! api/server.js must export an http.Server as default for Vercel")

print("api/server.js: no listen() call, imports pn-lib, exports the server")
