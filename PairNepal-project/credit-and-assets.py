#!/usr/bin/env python3
"""
Add the brand identity assets, the developer credit, and re-point the About
panel links that still belonged to the upstream project.

Design constraints honoured here:
- No DOM element referenced by the app's own JS is removed. `_evaluateBtnConfig`
  in ui.js calls setAttribute on its target, and only short-circuits when the
  server sends an empty config. Removing an anchor would therefore crash the
  About panel the moment an operator sets the matching environment variable.
  Every upstream anchor is kept in place and re-pointed instead.
- The developer credit carries no data-i18n-key, so the localization pass (which
  rewrites textContent of tagged elements) can never blank it out. A proper noun
  should not be translated anyway.
"""
import json
import pathlib

ROOT = pathlib.Path(__file__).parent / "app" / "public"
report = []
DEVELOPER = "Samir Puri"
SITE = "https://samirpuri.com.np"
SITE_LABEL = "samirpuri.com.np"
EMAIL = "Developer@samirpuri.com.np"


def patch(path, pairs, label):
    """Apply (old, new, expected_count) triples, asserting each one landed."""
    p = ROOT / path
    text = p.read_text(encoding="utf-8")
    for old, new, count in pairs:
        found = text.count(old)
        if found != count:
            raise SystemExit(f"!! {path} :: {label} :: expected {count}, found {found}\n   {old[:120]}")
        text = text.replace(old, new)
    p.write_text(text, encoding="utf-8")
    report.append(f"{path} — {label}")


# ------------------------------------------------------------------ 1. sprite icons
SPRITE_ADD = '''    <symbol id="pn-user" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round">
        <circle cx="12" cy="8.5" r="3.6"/>
        <path d="M4.8 20.2a7.4 7.4 0 0 1 14.4 0"/>
    </symbol>
    <symbol id="pn-mail" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round">
        <rect x="2.8" y="5" width="18.4" height="14" rx="2.6"/>
        <path d="m3.6 7 8.4 6 8.4-6"/>
    </symbol>
'''

idx = ROOT / "index.html"
t = idx.read_text(encoding="utf-8")
assert 'id="pn-user"' not in t
anchor = '    <symbol id="wifi-tethering"'
assert anchor in t
t = t.replace(anchor, SPRITE_ADD + anchor, 1)
idx.write_text(t, encoding="utf-8")
report.append("index.html — credit icons added to the sprite")

# ------------------------------------------- 2. About: developer link + credit block
patch("index.html", [
    (
        '<a class="icon-button" id="donation-btn" target="_blank" href="https://www.buymeacoffee.com/pairdrop" rel="noreferrer" data-i18n-key="about.buy-me-a-coffee" data-i18n-attrs="title">\n'
        '                    <svg class="icon">\n'
        '                        <use xlink:href="#donation"></use>\n'
        '                    </svg>\n'
        '                </a>',
        f'<a class="icon-button" id="donation-btn" target="_blank" href="{SITE}" rel="noreferrer noopener" data-i18n-key="about.developer" data-i18n-attrs="title">\n'
        '                    <svg class="icon">\n'
        '                        <use xlink:href="#pn-user"></use>\n'
        '                    </svg>\n'
        '                </a>',
        1,
    ),
    (
        '<a class="icon-button" id="x-twitter-btn" target="_blank" href="https://x.com/intent/tweet?text=https%3A%2F%2Fpairdrop.net%20by%20https%3A%2F%2Fgithub.com%2Fschlagmichdoch%2F&amp;" rel="noreferrer" data-i18n-key="about.tweet" data-i18n-attrs="title">',
        '<a class="icon-button" id="x-twitter-btn" target="_blank" href="https://x.com/intent/tweet?text=PairNepal%20%E2%80%94%20send%20files%20between%20your%20devices%2C%20instantly" rel="noreferrer noopener" data-i18n-key="about.tweet" data-i18n-attrs="title">',
        1,
    ),
    (
        '            <a class="btn btn-small" href="brand.html">About PairNepal</a>\n',
        '            <a class="btn btn-small" href="brand.html">About PairNepal</a>\n'
        '            <div class="pn-credit">\n'
        f'                <span>Built by <a href="{SITE}" target="_blank" rel="noreferrer noopener">{DEVELOPER}</a></span>\n'
        '                <span class="pn-credit__sep" aria-hidden="true">·</span>\n'
        f'                <a href="{SITE}" target="_blank" rel="noreferrer noopener">{SITE_LABEL}</a>\n'
        '                <span class="pn-credit__sep" aria-hidden="true">·</span>\n'
        f'                <a href="mailto:{EMAIL}">{EMAIL}</a>\n'
        '            </div>\n',
        1,
    ),
], "About panel credit + re-pointed links")

# ------------------------------------------------------------- 3. app footer credit
patch("index.html", [
    (
        '<x-instructions class="grow fade-in" data-i18n-key="instructions.x-instructions" data-i18n-attrs="desktop mobile data-drop-peer data-drop-bg"></x-instructions>',
        '<x-instructions class="grow fade-in" data-i18n-key="instructions.x-instructions" data-i18n-attrs="desktop mobile data-drop-peer data-drop-bg"></x-instructions>\n'
        '        <p class="pn-footcredit">\n'
        f'            PairNepal — built by <a href="{SITE}" target="_blank" rel="noreferrer noopener">{DEVELOPER}</a>\n'
        f'            <span aria-hidden="true">·</span> <a href="mailto:{EMAIL}">{EMAIL}</a>\n'
        '        </p>',
        1,
    ),
], "app footer credit")

# -------------------------------------- 4. meta + social card + icons (app + brand)
patch("index.html", [
    ('<meta name="twitter:image" content="images/logo_transparent_512x512.png">',
     '<meta name="twitter:image" content="images/pairnepal-social.png">', 1),
    ('<meta property="og:image" content="images/logo_transparent_512x512.png">',
     '<meta property="og:image" content="images/pairnepal-social.png">\n'
     '    <meta property="og:image:width" content="1200">\n'
     '    <meta property="og:image:height" content="630">\n'
     f'    <meta name="author" content="{DEVELOPER}">\n'
     f'    <link rel="author" href="{SITE}">\n'
     '    <link rel="me" href="mailto:' + EMAIL + '">', 1),
    ('<link rel="shortcut icon" href="images/favicon-96x96.png">',
     '<link rel="shortcut icon" href="images/favicon-96x96.png">\n'
     '    <link rel="icon" href="images/favicon.ico" sizes="any">\n'
     '    <link rel="icon" type="image/png" sizes="192x192" href="images/android-chrome-192x192.png">', 1),
], "app meta + icons")

patch("brand.html", [
    ('    <link rel="icon" sizes="96x96" href="images/favicon-96x96.png">',
     '    <link rel="icon" href="images/favicon.ico" sizes="any">\n'
     '    <link rel="icon" sizes="96x96" href="images/favicon-96x96.png">\n'
     '    <link rel="apple-touch-icon" href="images/apple-touch-icon.png">\n'
     '    <meta property="og:type" content="website">\n'
     '    <meta property="og:site_name" content="PairNepal">\n'
     '    <meta property="og:title" content="PairNepal — Send files between your devices, instantly">\n'
     '    <meta property="og:description" content="Send photos, documents and video straight between your phone, laptop and tablet. No signup, no cables, no size limits.">\n'
     '    <meta property="og:image" content="images/pairnepal-social.png">\n'
     '    <meta property="og:image:width" content="1200">\n'
     '    <meta property="og:image:height" content="630">\n'
     '    <meta name="twitter:card" content="summary_large_image">\n'
     '    <meta name="twitter:image" content="images/pairnepal-social.png">\n'
     f'    <meta name="author" content="{DEVELOPER}">', 1),
    (
        '            <nav aria-label="Footer">\n'
        '                <a href="/">Open the app</a>\n'
        '                <a href="#how">How it works</a>\n'
        '                <a href="#sound">Sound design</a>\n'
        '                <a href="#faq">FAQ</a>\n'
        '            </nav>',
        '            <div>\n'
        '                <nav aria-label="Footer">\n'
        '                    <a href="/">Open the app</a>\n'
        '                    <a href="#how">How it works</a>\n'
        '                    <a href="#sound">Sound design</a>\n'
        '                    <a href="#faq">FAQ</a>\n'
        '                </nav>\n'
        '                <div class="pn-credit pn-credit--left">\n'
        f'                    <span>PairNepal — built by <a href="{SITE}" target="_blank" rel="noreferrer noopener">{DEVELOPER}</a></span>\n'
        '                    <span class="pn-credit__sep" aria-hidden="true">·</span>\n'
        f'                    <a href="{SITE}" target="_blank" rel="noreferrer noopener">{SITE_LABEL}</a>\n'
        '                    <span class="pn-credit__sep" aria-hidden="true">·</span>\n'
        f'                    <a href="mailto:{EMAIL}">{EMAIL}</a>\n'
        '                </div>\n'
        f'                <p class="pn-credit__note">Built on the open-source PairDrop project, used under GPL-3.0.</p>\n'
        '            </div>',
        1,
    ),
], "brand page meta + footer credit")

# ------------------------------------------------------------------- 5. humans.txt
(ROOT / "humans.txt").write_text(
    f"""/* TEAM */
Developer: {DEVELOPER}
Contact: {EMAIL}
Website: {SITE}
Location: Nepal

/* SITE */
Last update: 2026/10/09
Language: English
Doctype: HTML5
Standards: HTML5, CSS3, ES6
Components: Instrument Serif, Instrument Sans, JetBrains Mono
Software: PairNepal, built on PairDrop (GPL-3.0)
""", encoding="utf-8")
report.append("humans.txt — written")

# ---------------------------------------------------------------------- 6. manifest
mpath = ROOT / "manifest.json"
mf = json.loads(mpath.read_text(encoding="utf-8"))
mf["name"] = "PairNepal"
mf["short_name"] = "PairNepal"
mf["description"] = "Send files between your devices instantly. No signup, no cables."
mf["background_color"] = "#f7f8fa"
mf["theme_color"] = "#c11235"
mf["lang"] = "en"
mf["icons"] = [
    {"src": "images/favicon-96x96.png", "sizes": "96x96", "type": "image/png"},
    {"src": "images/android-chrome-192x192.png", "sizes": "192x192", "type": "image/png"},
    {"src": "images/android-chrome-512x512.png", "sizes": "512x512", "type": "image/png"},
    {"src": "images/android-chrome-192x192-maskable.png", "sizes": "192x192", "type": "image/png", "purpose": "maskable"},
    {"src": "images/android-chrome-512x512-maskable.png", "sizes": "512x512", "type": "image/png", "purpose": "maskable"},
]
mpath.write_text(json.dumps(mf, indent=4) + "\n", encoding="utf-8")
report.append("manifest.json — brand icons, theme colour, lang")

# ----------------------------------------------------------------------- 7. strings
lpath = ROOT / "lang" / "en.json"
lang = json.loads(lpath.read_text(encoding="utf-8"))
lang["about"]["developer"] = f"{DEVELOPER} — {SITE_LABEL}"
lang["about"]["tweet_title"] = "Share PairNepal"
lang["about"]["github_title"] = "Source code (PairDrop, GPL-3.0)"
lpath.write_text(json.dumps(lang, indent=4, ensure_ascii=False) + "\n", encoding="utf-8")
report.append("lang/en.json — developer + share titles")

# ------------------------------------------------------------------------ 8. styles
css = ROOT / "styles" / "brand.css"
c = css.read_text(encoding="utf-8")
assert ".pn-credit" not in c
c = c.replace("""/* About page brand mark */""", """/* Developer credit — About panel, app footer, brand page footer. */
.pn-credit {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    justify-content: center;
    gap: 6px 8px;
    font-size: 12.5px;
    line-height: 1.6;
    color: var(--pn-ink-3);
    margin-top: 14px;
    max-width: 46ch;
    text-align: center;
}

.pn-credit--left { justify-content: flex-start; text-align: left; margin-top: 18px; }

.pn-credit a {
    color: var(--pn-ink-2);
    text-decoration: none;
    border-bottom: 1px solid var(--pn-line-strong);
    padding-bottom: 1px;
}

.pn-credit a:hover { color: var(--pn-accent); border-bottom-color: var(--pn-accent); }

.pn-credit__sep { color: var(--pn-line-strong); }

.pn-credit__note {
    font-size: 12px;
    color: var(--pn-ink-3);
    margin: 8px 0 0;
    max-width: 46ch;
}

/* Persistent, quiet credit in the app shell. */
.pn-footcredit {
    font-size: 11.5px;
    color: var(--pn-ink-3);
    text-align: center;
    margin: 0 0 14px;
    padding: 0 16px;
}

.pn-footcredit a {
    color: var(--pn-ink-3);
    text-decoration: none;
    border-bottom: 1px solid var(--pn-line);
}

.pn-footcredit a:hover { color: var(--pn-accent); border-bottom-color: var(--pn-accent); }

/* About page brand mark */""")
css.write_text(c, encoding="utf-8")
report.append("brand.css — credit styles")

# ----------------------------------------------------------------- 9. cache version
sw = ROOT / "service-worker.js"
s = sw.read_text(encoding="utf-8")
s = s.replace("const cacheVersion = 'v1.11.2-pn3';", "const cacheVersion = 'v1.11.2-pn4';")
sw.write_text(s, encoding="utf-8")
report.append("service-worker.js — cacheVersion pn4 (icon assets changed)")

print("Applied:")
for r in report:
    print("  -", r)
print(f"\n{len(report)} change groups applied.")
