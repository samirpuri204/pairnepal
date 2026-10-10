#!/usr/bin/env python3
"""
Rebrand, pass 2 — the two anchors that pass 1 could not match.

The upstream `og:description` line contains a character that does not survive a
naive copy/paste comparison, so this pass works on whole regions delimited by
stable comment markers instead of exact line text. That makes it robust to any
invisible whitespace or punctuation differences upstream.
"""
import pathlib
import re

ROOT = pathlib.Path(__file__).parent / "app" / "public"
idx = ROOT / "index.html"
text = idx.read_text(encoding="utf-8")
report = []

# ------------------------------------------------------------------ 1. head meta
old_head = re.search(
    r"    <!-- Web App Config -->.*?    <!-- Icons -->",
    text, re.DOTALL)
if not old_head:
    raise SystemExit("!! head region not found — aborting rather than guessing")

new_head = """    <!-- Web App Config -->
    <title>PairNepal — Send files between devices, instantly</title>
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
    <meta name="author" content="PairNepal">
    <meta property="og:title" content="PairNepal — Send files between devices, instantly">
    <meta property="og:type" content="website">
    <meta property="og:site_name" content="PairNepal">
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:description" content="Send photos, documents and video straight between your devices. No signup, no cables, no upload limits.">
    <meta property="og:description" content="Send photos, documents and video straight between your devices. No signup, no cables, no upload limits.">
    <!-- Icons -->"""

text = text[:old_head.start()] + new_head + text[old_head.end():]
report.append("head meta region rewritten")

# -------------------------------------------------------------- 2. brand scripts
if "pairnepal-boot.js" not in text:
    anchor = "</body>"
    if anchor not in text:
        raise SystemExit("!! </body> not found")
    block = ('    <!-- PairNepal brand layer: sound design, motion, ident -->\n'
             '    <script src="scripts/pairnepal-sound.js" defer></script>\n'
             '    <script src="scripts/pairnepal-motion.js" defer></script>\n'
             '    <script src="scripts/pairnepal-boot.js" defer></script>\n')
    text = text.replace(anchor, block + anchor, 1)
    report.append("brand scripts injected before </body>")
else:
    report.append("brand scripts already present")

idx.write_text(text, encoding="utf-8")

# --------------------------------------------------------------- verification
check = idx.read_text(encoding="utf-8")
assert "pairnepal-boot.js" in check, "scripts missing"
assert "<title>PairNepal" in check, "title missing"
assert "Instrument+Serif" in check, "fonts missing"
assert "pn-brand" in check, "header brand missing"
assert "pn-ident" in check, "ident missing"
assert "PairDrop | Transfer Files" not in check, "old title still present"

print("Applied:")
for r in report:
    print("  -", r)
print("\nVerification: all brand assertions passed.")
