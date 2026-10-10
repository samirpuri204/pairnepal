#!/usr/bin/env python3
"""
Builds brand/os-icons.html — a standalone proof page that renders every device
icon actually shipped in index.html, so the per-OS mapping can be inspected
without needing real devices on other operating systems.

The symbols are lifted verbatim out of index.html, so what is on the page is
what the app draws.
"""
import pathlib
import re

ROOT = pathlib.Path(__file__).parent
INDEX = ROOT / "app" / "public" / "index.html"
OUT = ROOT / "brand" / "os-icons.html"

BY_OS = ["os-apple", "os-windows", "os-linux", "os-ubuntu", "os-android", "os-chrome"]
BY_CLASS = ["phone-iphone", "tablet-mac", "desktop-mac"]


def main():
    html = INDEX.read_text()
    syms = re.findall(r'<symbol id="[^"]+"[^>]*>.*?</symbol>', html, re.S)
    have = {re.search(r'id="([^"]+)"', s).group(1) for s in syms}


def _build():
    html = INDEX.read_text()
    syms = re.findall(r'<symbol id="[^"]+"[^>]*>.*?</symbol>', html, re.S)
    have = {re.search(r'id="([^"]+)"', s).group(1) for s in syms}

    missing = [i for i in BY_OS + BY_CLASS if i not in have]
    if missing:
        raise SystemExit(f"index.html is missing symbols: {missing}")

    def tiles(ids, label):
        out = [f'<p class="label">{label}</p><div class="row">']
        for i in ids:
            out.append(
                f'<span class="cell"><span class="well">'
                f'<svg class="icon"><use href="#{i}"></use></svg></span>'
                f'<span class="px">{i}</span></span>'
            )
        out.append("</div>")
        return "".join(out)

    OUT.write_text(f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<title>PairNepal device icons</title>
<style>
  :root{{--accent:#c11235;--ink:#101828;--ink3:#8896ab}}
  *{{box-sizing:border-box}}
  body{{margin:0;padding:26px 30px 40px;font-family:'Instrument Sans',system-ui,sans-serif;
       background:#f7f8fa;color:var(--ink)}}
  h1{{font-size:23px;margin:0 0 3px}}
  .sub{{font-family:ui-monospace,monospace;font-size:10px;letter-spacing:.14em;
        text-transform:uppercase;color:var(--ink3);margin-bottom:20px}}
  .label{{font-family:ui-monospace,monospace;font-size:10px;letter-spacing:.16em;
          text-transform:uppercase;color:var(--ink3);margin:18px 0 10px}}
  .row{{display:flex;gap:22px;flex-wrap:wrap;align-items:flex-end;
        background:#fff;border:1px solid #e7eaf0;border-radius:12px;padding:16px 18px}}
  .cell{{display:flex;flex-direction:column;align-items:center;gap:7px;width:96px}}
  .well{{display:grid;place-items:center;width:92px;height:92px;border-radius:14px;
         background:#f7f8fa;border:1px solid #eceff4}}
  .icon{{width:42px;height:42px;fill:var(--accent);color:var(--accent)}}
  .px{{font-family:ui-monospace,monospace;font-size:9px;color:var(--ink3);
       text-align:center;word-break:break-all}}
  .dark{{background:#0b0d12;border-color:#232a37}}
  .dark .well{{background:#141821;border-color:#232a37}}
  .dark .icon{{fill:#ff5470;color:#ff5470}}
  .dark .px,.dark .label{{color:#7b8798}}
</style></head>
<body>
<h1>PairNepal — device icons as shipped</h1>
<div class="sub">lifted verbatim from index.html</div>
{''.join(f'<svg style="display:none" xmlns="http://www.w3.org/2000/svg">{s}</svg>' for s in syms)}
{tiles(BY_OS, 'Operating system icons (dark theme accent)')}
<div class="row dark">{''.join(
    f'<span class="cell"><span class="well"><svg class="icon"><use href="#{i}"></use></svg></span>'
    f'<span class="px">{i}</span></span>' for i in BY_OS)}</div>
{tiles(BY_CLASS, 'Fallbacks when no OS is reported')}
</body></html>
""")
    print("wrote", OUT)
    print("symbols found:", len(syms))


if __name__ == "__main__":
    _build()
