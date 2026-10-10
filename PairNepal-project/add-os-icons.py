#!/usr/bin/env python3
"""
Inserts per-OS device icons into app/public/index.html as <symbol> elements.

The paths are the official simple-icons (CC0) 24x24 marks, downloaded into
brand/os/, so they are exact rather than hand-transcribed. Re-runnable: the
region between the two markers is replaced in place.
"""
import pathlib
import re

ROOT = pathlib.Path(__file__).parent
OS_DIR = ROOT / "brand" / "os"
INDEX = ROOT / "app" / "public" / "index.html"

BEGIN = "<!-- pn:os-icons:begin -->"
END = "<!-- pn:os-icons:end -->"

# id -> source file. Apple covers macOS and iOS; Windows covers desktop and
# tablet; the Linux family keeps Ubuntu distinct because users recognise it.
ICONS = [
    ("os-apple", "apple.svg"),
    ("os-windows", "windows11.svg"),
    ("os-linux", "linux.svg"),
    ("os-ubuntu", "ubuntu.svg"),
    ("os-android", "android.svg"),
    ("os-chrome", "googlechrome.svg"),
]


def main():
    html = INDEX.read_text()

    blocks = []
    for sym_id, fname in ICONS:
        svg = (OS_DIR / fname).read_text()
        vb = re.search(r'viewBox="([^"]+)"', svg)
        ds = re.findall(r'\bd="([^"]+)"', svg)
        if not vb or not ds:
            raise SystemExit(f"{fname}: could not find viewBox/path")
        path = " ".join(ds)
        blocks.append(
            f'        <symbol id="{sym_id}" viewBox="{vb.group(1)}">\n'
            f'            <path d="{path}"></path>\n'
            f'        </symbol>'
        )

    block = BEGIN + "\n" + "\n".join(blocks) + "\n        " + END

    if BEGIN in html and END in html:
        html = re.sub(re.escape(BEGIN) + r".*?" + re.escape(END),
                      lambda _m: block, html, flags=re.S)
    else:
        anchor = '        <symbol id="desktop-mac"'
        i = html.index(anchor)
        j = html.index("</symbol>", i) + len("</symbol>")
        html = html[:j] + "\n\n" + block + html[j:]

    INDEX.write_text(html)
    print(f"inserted {len(ICONS)} OS symbols into {INDEX}")


if __name__ == "__main__":
    main()
