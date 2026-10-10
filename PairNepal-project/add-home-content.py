#!/usr/bin/env python3
"""
Gives the homepage something for a crawler to index.

The app is a hard one-screen layout (`html, body { height: 100%; overflow-y:
hidden }`), so `/` carried about 165 words of visible text — almost all of it
inside dialogs that are hidden until opened. A page with no body copy cannot
rank for its own brand name, let alone for the spaced variants of it.

Two changes, both idempotent:

  1. Wrap the app in `.pn-app-shell`, which is pinned to exactly one viewport
     height. The app's internal layout is untouched because the shell supplies
     the same definite height `<body>` used to.
  2. Append an editorial section below it and let the document scroll.

The copy is real information about the product and names the brand the way
people actually type it. It is not a keyword list.
"""
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).parent
INDEX = ROOT / "app" / "public" / "index.html"

SHELL_OPEN = '<div class="pn-app-shell">'
MARKER = "<!-- pn:tail -->"
ANCHOR = '<x-dialog id="language-select-dialog"'

TAIL = MARKER + """
<section class="pn-tail" aria-labelledby="pn-tail-title">
    <div class="pn-tail__wrap">

        <p class="pn-tail__kicker">Send files between your devices</p>
        <h2 id="pn-tail-title">What is PairNepal?</h2>
        <p class="pn-tail__lede">
            PairNepal is a free file transfer tool that sends photos, videos and documents
            straight between your own devices — phone to laptop, laptop to tablet, desktop to
            phone. It runs in the browser, so there is nothing to install, no account to create
            and no upload limit. You will see it written a few different ways — PairNepal,
            Pair Nepal, pair nepal, pairnepal — and every one of them means this page.
        </p>

        <div class="pn-tail__stats">
            <div><b>0</b><span>accounts to create</span></div>
            <div><b>0</b><span>files kept on a server</span></div>
            <div><b>0</b><span>upload size limit</span></div>
            <div><b>3</b><span>steps, start to finish</span></div>
        </div>

        <h2>How PairNepal moves a file</h2>
        <ol class="pn-tail__steps">
            <li>
                <h3>Open PairNepal on both devices</h3>
                <p>
                    Load pairnepal.bond on the phone and on the computer. On the same Wi-Fi they
                    find each other on their own — no code to type, no cable, no pairing screen.
                </p>
            </li>
            <li>
                <h3>Choose the device you are sending to</h3>
                <p>
                    Every nearby device appears by name, with the operating system it is running
                    under it. Pick the one you want, then choose the photos, videos or documents
                    you are sending.
                </p>
            </li>
            <li>
                <h3>Watch the file travel device to device</h3>
                <p>
                    The transfer runs directly between the two browsers over an encrypted
                    peer-to-peer connection. The server only helps the two devices find each
                    other; the file itself never passes through it.
                </p>
            </li>
        </ol>

        <h2>Not on the same Wi-Fi? PairNepal handles that too</h2>
        <p>
            Devices on the same network are the quickest path, but they are not the only one.
            Pair two devices once with a six-digit code and they stay paired, so they can reach
            each other across different networks later. For one-off transfers, join a temporary
            five-letter room and send across the internet without pairing anything.
        </p>

        <h2>What you can send with PairNepal</h2>
        <p>
            Anything a browser can read, with the original quality kept intact:
        </p>
        <ul class="pn-tail__list">
            <li><b>Photos and RAW files</b> — full resolution, no re-compression and no downscaling.</li>
            <li><b>Video</b> — including files far past the limit a chat app will accept.</li>
            <li><b>Documents</b> — PDFs, spreadsheets, slide decks, archives and folders.</li>
            <li><b>Folders</b> — sent whole, with the directory structure preserved.</li>
        </ul>
        <p>
            Because the file moves straight to the other device, its size is limited by your
            browser and your disk, not by an upload cap.
        </p>

        <h2>PairNepal compared with the usual options</h2>
        <table class="pn-tail__table">
            <caption class="sr-only">PairNepal compared with email, chat apps, cloud drives and AirDrop</caption>
            <thead>
                <tr>
                    <th scope="col">Method</th>
                    <th scope="col">Cross-platform</th>
                    <th scope="col">Size limit</th>
                    <th scope="col">File leaves your devices</th>
                    <th scope="col">Account</th>
                </tr>
            </thead>
            <tbody>
                <tr class="is-hero">
                    <th scope="row">PairNepal</th>
                    <td>Yes — any two browsers</td>
                    <td>None</td>
                    <td>No, peer to peer</td>
                    <td>Not needed</td>
                </tr>
                <tr>
                    <th scope="row">Email attachment</th>
                    <td>Yes</td>
                    <td>Often 25 MB</td>
                    <td>Yes, via a mail server</td>
                    <td>Yes</td>
                </tr>
                <tr>
                    <th scope="row">Chat app</th>
                    <td>Yes</td>
                    <td>Compressed, capped</td>
                    <td>Yes, via the provider</td>
                    <td>Yes</td>
                </tr>
                <tr>
                    <th scope="row">Cloud drive</th>
                    <td>Yes</td>
                    <td>Quota per plan</td>
                    <td>Yes, stored in the cloud</td>
                    <td>Yes</td>
                </tr>
                <tr>
                    <th scope="row">AirDrop</th>
                    <td>Apple devices only</td>
                    <td>None</td>
                    <td>No</td>
                    <td>Not needed</td>
                </tr>
            </tbody>
        </table>

        <h2>Which devices and systems PairNepal works with</h2>
        <p>
            Any device with a current browser works: Windows, macOS, Linux, Android, iOS and
            ChromeOS. Each device shows its own operating system under its icon in the app, so
            it is obvious which of your machines you are about to send to. There is no native
            app to install on any of them — although you can add PairNepal to your home screen
            so it opens like one.
        </p>

        <h2>Frequently asked questions</h2>

        <details class="pn-tail__faq">
            <summary>Is Pair Nepal the same thing as PairNepal?</summary>
            <p>
                Yes. PairNepal, Pair Nepal, Pair nepal, pair Nepal, Pairnepal and
                pairnepal.bond all refer to this same free file transfer tool. The name is one
                word, but search engines and people routinely split it in two, so both spellings
                land here.
            </p>
        </details>

        <details class="pn-tail__faq">
            <summary>Is PairNepal free?</summary>
            <p>
                Yes, and there is no paid tier waiting behind it. Transfers run directly between
                your devices rather than through our storage, so there is no bandwidth bill to
                pass on to you.
            </p>
        </details>

        <details class="pn-tail__faq">
            <summary>Do my files go through a server?</summary>
            <p>
                No. The PairNepal server only introduces the two devices to each other. Once they
                are connected the data travels directly between the browsers, which is why there
                is no size limit and why nothing is stored.
            </p>
        </details>

        <details class="pn-tail__faq">
            <summary>Do I need to sign up?</summary>
            <p>
                No account, no email address and no installation. Open pairnepal.bond on both
                devices and the transfer can start immediately.
            </p>
        </details>

        <details class="pn-tail__faq">
            <summary>Does PairNepal work between a phone and a computer?</summary>
            <p>
                That is the most common use. Android or iPhone to Windows, macOS or Linux works
                because both ends are ordinary browsers, not applications tied to one platform.
            </p>
        </details>

        <p class="pn-tail__close">
            PairNepal is built by
            <a href="https://samirpuri.com.np" target="_blank" rel="noreferrer noopener">Samir Puri</a>.
            Read <a href="brand.html">how PairNepal works in detail</a>, or open
            <a href="/">the file transfer app</a> and send something.
        </p>

    </div>
</section>
"""


def main():
    html = INDEX.read_text()
    if MARKER in html:
        print("already applied — nothing to do")
        return
    if ANCHOR not in html:
        sys.exit(f"anchor not found in {INDEX}: {ANCHOR}")
    m = re.search(r"<body[^>]*>", html)
    if not m:
        sys.exit(f"no <body> in {INDEX}")

    # 1. open the shell immediately inside <body>
    html = html[:m.end()] + "\n" + SHELL_OPEN + html[m.end():]

    # 2. close the shell, then append the editorial section, before the dialogs
    i = html.index(ANCHOR)
    html = html[:i] + "</div>\n\n" + TAIL + "\n" + html[i:]

    INDEX.write_text(html)
    print("wrapped the app shell and appended the homepage content")


if __name__ == "__main__":
    main()
