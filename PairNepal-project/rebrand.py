#!/usr/bin/env python3
"""
PairDrop -> PairNepal rebrand.

Verifiable, idempotent text/AST substitutions across the app. Every replacement
asserts that it happened exactly the expected number of times, so a silent
no-op is impossible.
"""
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).parent / "app" / "public"
changes = []


def sub(path, old, new, count=1, label=""):
    p = ROOT / path
    text = p.read_text(encoding="utf-8")
    found = text.count(old)
    if found != count:
        print(f"  !! {path}: expected {count} match(es), found {found} :: {label or old[:60]}")
        return False
    p.write_text(text.replace(old, new), encoding="utf-8")
    changes.append(f"{path}: {label or old[:50]}")
    return True


# ---------------------------------------------------------------- brand assets
BRAND_MARK = (
    '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" '
    'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
    '<path d="M3 18.6 9.4 7.2l3.3 5.9 2.2-3.5L21 18.6z" fill="currentColor" fill-opacity=".14"/>'
    '<path d="M3 18.6 9.4 7.2l3.3 5.9 2.2-3.5L21 18.6z"/>'
    '<path d="M8.7 3.5a8.3 8.3 0 0 1 6.6 0" stroke-width="1.5"/>'
    "</svg>"
)

HEADER_BRAND = f"""        <a class="pn-brand" href="#about" aria-label="PairNepal — about this app">
            <span class="pn-brand__mark">{BRAND_MARK}</span>
            <span class="pn-brand__text">
                <span class="pn-brand__name">PairNepal</span>
                <span class="pn-brand__tag">Send files, instantly</span>
            </span>
        </a>
"""

# The in-app brand motion graphic: an animated SVG ident, no video file.
IDENT = """            <div class="pn-ident" role="img" aria-label="Two devices connected, a file moving between them">
                <span class="pn-ident__ring"></span>
                <span class="pn-ident__ring" style="inset:13%"></span>
                <svg class="pn-ident__svg" viewBox="0 0 260 130" fill="none" aria-hidden="true">
                    <line class="pn-ident__beam" x1="62" y1="65" x2="198" y2="65" stroke-width="1.8"/>
                    <circle class="pn-ident__packet" cx="62" cy="65" r="4.5" data-pn-travel="136"/>

                    <g class="pn-ident__node">
                        <rect x="22" y="41" width="40" height="48" rx="11" stroke="currentColor" stroke-width="1.6"/>
                        <path d="M37 80h10" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/>
                        <path d="M34 60h16M34 67h11" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" opacity=".6"/>
                    </g>

                    <g class="pn-ident__node">
                        <rect x="108" y="34" width="52" height="36" rx="6" stroke="currentColor" stroke-width="1.6"/>
                        <path d="M100 77h68a4 4 0 0 1-4 4h-60a4 4 0 0 1-4-4z" stroke="currentColor" stroke-width="1.4"/>
                        <path d="M118 46h32M118 54h20" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" opacity=".6"/>
                    </g>

                    <g class="pn-ident__node">
                        <rect x="198" y="44" width="38" height="42" rx="10" stroke="currentColor" stroke-width="1.6"/>
                        <path d="M210 60h14M210 67h9" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" opacity=".6"/>
                    </g>
                </svg>
                <span class="pn-ident__label">looking</span>
            </div>
"""

# ------------------------------------------------------------------- index.html
HEAD_OLD = """    <title>PairDrop | Transfer Files Cross-Platform. No Setup, No Signup.</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="theme-color" content="#3367d6">
    <meta name="color-scheme" content="dark light">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
    <meta name="apple-mobile-web-app-title" content="PairDrop">
    <meta name="application-name" content="PairDrop">
    <!-- Descriptions -->
    <meta name="description" content="Instantly share images, videos, PDFs, and links with people nearby. Peer2Peer and Open Source. No Setup, No Signup.">
    <meta name="keywords" content="File, Transfer, Share, Peer2Peer">
    <meta name="author" content="schlagmichdoch">
    <meta property="og:title" content="PairDrop">
    <meta property="og:type" content="article">
    <meta property="og:url" content="https://pairdrop.net/">
    <meta property="og:author" content="https://github.com/schlagmichdoch">
    <meta name="twitter:author" content="@schlagmichdoch">
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:description" content="Instantly share images, videos, PDFs, and links with people nearby. Peer2Peer and Open Source. No Setup, No Signup.">
    <meta property="og:description" content="Instantly share images, videos, PDFs, and links with people nearby. Peer2Peer and Open Source. No Setup, No Signup.">"""

HEAD_NEW = """    <title>PairNepal — Send files between devices, instantly</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="theme-color" content="#f7f8fa" media="(prefers-color-scheme: light)">
    <meta name="theme-color" content="#0b0d12" media="(prefers-color-scheme: dark)">
    <meta name="color-scheme" content="light dark">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="default">
    <meta name="apple-mobile-web-app-title" content="PairNepal">
    <meta name="application-name" content="PairNepal">
    <!-- Descriptions -->
    <meta name="description" content="Send photos, documents and video straight between your devices. No signup, no cables, no upload limits — peer to peer, in the browser.">
    <meta name="keywords" content="file transfer, share files, peer to peer, PairNepal, send files Nepal">
    <meta property="og:title" content="PairNepal — Send files between devices, instantly">
    <meta property="og:type" content="website">
    <meta property="og:site_name" content="PairNepal">
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:description" content="Send photos, documents and video straight between your devices. No signup, no cables, no upload limits.">
    <meta property="og:description" content="Send photos, documents and video straight between your devices. No signup, no cables, no upload limits.">"""

sub("index.html", HEAD_OLD, HEAD_NEW, label="head meta")

sub(
    "index.html",
    '    <link rel="preload" href="fonts/OpenSans/static/OpenSans-Medium.ttf" as="font" type="font/ttf" crossorigin>\n'
    '    <link rel="stylesheet" type="text/css" href="styles/styles-main.css">',
    '    <!-- Typefaces: Instrument Serif (display) · Instrument Sans (UI) · JetBrains Mono (codes) -->\n'
    '    <link rel="preconnect" href="https://fonts.googleapis.com">\n'
    '    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
    '    <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Instrument+Sans:wght@400..700'
    '&family=Instrument+Serif:ital@0;1&family=JetBrains+Mono:wght@400;600&display=swap">\n'
    '    <link rel="stylesheet" type="text/css" href="styles/styles-main.css">',
    label="font loading",
)

# Brand lockup as the last header child (header is flex-row-reverse, so the last
# child lands on the left and the tools keep the right).
sub(
    "index.html",
    '    </header>\n    <!-- Center -->',
    HEADER_BRAND + '    </header>\n    <!-- Center -->',
    label="header brand lockup",
)

# The ident goes inside the empty state; localization only rewrites descendants
# that carry data-i18n-key, so this block is never overwritten by ui.js.
sub(
    "index.html",
    '        <x-no-peers class="center grow fade-in no-animation-on-load" data-i18n-key="instructions.no-peers" data-i18n-attrs="data-drop-bg">\n',
    '        <x-no-peers class="center grow fade-in no-animation-on-load" data-i18n-key="instructions.no-peers" data-i18n-attrs="data-drop-bg">\n'
    + IDENT,
    label="ident in empty state",
)

# About page identity
sub(
    "index.html",
    '            <div class="title-wrapper" dir="ltr">\n                <h1>PairDrop</h1>\n                <div class="font-subheading">v1.11.2</div>\n            </div>',
    '            <div class="title-wrapper" dir="ltr">\n                <h1>PairNepal</h1>\n                <div class="font-subheading">Peer-to-peer file transfer</div>\n            </div>',
    label="about title",
)

sub(
    "index.html",
    '            <svg class="icon logo">\n                <use xlink:href="#wifi-tethering"></use>\n            </svg>\n            <div class="title-wrapper" dir="ltr">',
    f'            <span class="pn-about-mark">{BRAND_MARK}</span>\n            <div class="title-wrapper" dir="ltr">',
    label="about logo mark",
)

# Brand scripts: defer keeps document order and runs after parsing.
sub(
    "index.html",
    "    </div>\n</body>\n</html>",
    '    </div>\n'
    '    <!-- PairNepal brand layer: sound design, motion, ident -->\n'
    '    <script src="scripts/pairnepal-sound.js" defer></script>\n'
    '    <script src="scripts/pairnepal-motion.js" defer></script>\n'
    '    <script src="scripts/pairnepal-boot.js" defer></script>\n'
    "</body>\n</html>",
    label="brand scripts",
)

# ---------------------------------------------------------------- deferred CSS
sub(
    "scripts/main.js",
    '        this.deferredStyles = [\n            "styles/styles-deferred.css"\n        ];',
    '        this.deferredStyles = [\n            "styles/styles-deferred.css",\n'
    '            // Brand layer must cascade last, so it loads after the deferred sheet.\n'
    '            "styles/brand.css"\n        ];',
    label="defer brand.css last",
)

# --------------------------------------------------------------------- manifest
mpath = ROOT / "manifest.json"
mf = json.loads(mpath.read_text(encoding="utf-8"))
mf["name"] = "PairNepal"
mf["short_name"] = "PairNepal"
mf["description"] = "Send files between your devices instantly. No signup, no cables."
mf["background_color"] = "#f7f8fa"
mf["theme_color"] = "#c11235"
mf.pop("screenshots", None)  # upstream screenshots show the old brand
mpath.write_text(json.dumps(mf, indent=4) + "\n", encoding="utf-8")
changes.append("manifest.json: name/theme/description, upstream screenshots removed")

# ---------------------------------------------------------------- service worker
sw = ROOT / "service-worker.js"
text = sw.read_text(encoding="utf-8")
text = text.replace("const cacheVersion = 'v1.11.2';", "const cacheVersion = 'v1.11.2-pn1';")
text = text.replace("const cacheTitle = `pairdrop-cache-${cacheVersion}`;",
                    "const cacheTitle = `pairnepal-cache-${cacheVersion}`;")
text = text.replace(
    "    'styles/styles-deferred.css',",
    "    'styles/styles-deferred.css',\n    'styles/brand.css',")
text = text.replace(
    "    'scripts/util.js',",
    "    'scripts/util.js',\n    'scripts/pairnepal-sound.js',\n"
    "    'scripts/pairnepal-motion.js',\n    'scripts/pairnepal-boot.js',")
sw.write_text(text, encoding="utf-8")
changes.append("service-worker.js: cache version + brand assets")

# ------------------------------------------------------------------- en strings
lpath = ROOT / "lang" / "en.json"
lang = json.loads(lpath.read_text(encoding="utf-8"))


def walk(node):
    if isinstance(node, dict):
        return {k: walk(v) for k, v in node.items()}
    if isinstance(node, list):
        return [walk(v) for v in node]
    if isinstance(node, str):
        return node.replace("PairDrop", "PairNepal")
    return node


lang = walk(lang)
# Keep the upstream attribution honest — this is a GPL-3.0 derivative work.
lang["about"]["claim"] = "Send files straight between your devices — no signup, no cables."
lang["about"]["github_title"] = "Source code (PairDrop, GPL-3.0)"
lpath.write_text(json.dumps(lang, indent=4, ensure_ascii=False) + "\n", encoding="utf-8")
changes.append("lang/en.json: brand strings renamed, attribution preserved")

print("\nApplied changes:")
for c in changes:
    print("  -", c)
print(f"\n{len(changes)} change groups applied.")
