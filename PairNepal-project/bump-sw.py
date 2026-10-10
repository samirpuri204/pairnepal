#!/usr/bin/env python3
"""
Stamps the service-worker cache version from a hash of the precached files.

`service-worker.js` serves everything in `relativePathsToCache` **cache-first**
and only re-fetches when `cacheVersion` changes — its own comment says so. That
makes bumping the version by hand load-bearing, and forgetting it means
returning visitors keep stale CSS or JS for as long as the cached worker lives.

That is exactly how a scroll fix can ship without reaching anybody: `brand.css`
is precached, so a laptop that had already visited kept the old stylesheet with
`overflow-y: hidden` while a phone that had not came up correct.

Hashing the precached files makes a stale cache impossible — any change to any
precached asset produces a new cache name, so the worker must re-fetch. Run this
before every deploy. It is idempotent.
"""
import hashlib
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).parent
PUBLIC = ROOT / "app" / "public"
SW = PUBLIC / "service-worker.js"


def main():
    src = SW.read_text()

    m = re.search(r"const relativePathsToCache = \[(.*?)\];", src, re.S)
    if not m:
        sys.exit("could not find relativePathsToCache in service-worker.js")
    paths = re.findall(r"'([^']+)'", m.group(1))

    h = hashlib.sha256()
    hashed, missing = 0, 0
    for rel in paths:
        if rel in ("./", "."):
            rel = "index.html"
        p = PUBLIC / rel.lstrip("./")
        if p.is_file():
            h.update(rel.encode())
            h.update(p.read_bytes())
            hashed += 1
        else:
            missing += 1

    digest = h.hexdigest()[:10]

    cur = re.search(r"const cacheVersion = '([^']+)';", src)
    if not cur:
        sys.exit("could not find cacheVersion in service-worker.js")
    base = cur.group(1)
    prefix = base.split("-")[0]          # keep the app version, e.g. v1.11.2
    new = f"{prefix}-{digest}"

    if new == base:
        print(f"cacheVersion unchanged: {new}  ({hashed} files hashed, {missing} not on disk)")
        return

    SW.write_text(re.sub(r"const cacheVersion = '[^']+';",
                         f"const cacheVersion = '{new}';", src, count=1))
    print(f"cacheVersion {base} -> {new}")
    print(f"  {hashed} precached files hashed, {missing} not present locally")


if __name__ == "__main__":
    main()
