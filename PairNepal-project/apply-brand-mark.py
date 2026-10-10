#!/usr/bin/env python3
"""
Replaces the old inline mountain mark with the new "leaning pair" mark in the
shipped HTML.

The mark is drawn with currentColor so the cascade decides its colour — which is
what makes it work on both themes from a single definition. Re-runnable.
"""
import pathlib
import re

ROOT = pathlib.Path(__file__).parent

OLD_PATH_MARKER = "M3 18.6 9.4 7.2"

MARK_INNER = (
    '<rect x="2.8" y="4.6" width="7.6" height="16.4" rx="2.6" transform="rotate(22 6.6 12.8)"/>'
    '<rect x="13.6" y="4.6" width="7.6" height="16.4" rx="2.6" transform="rotate(-22 17.4 12.8)"/>'
)


def new_svg(cls=None, extra_attrs=""):
    klass = f' class="{cls}"' if cls else ""
    return (
        f'<svg{klass} viewBox="0 0 24 24" fill="currentColor" '
        f'xmlns="http://www.w3.org/2000/svg" aria-hidden="true"{extra_attrs}>'
        f'{MARK_INNER}</svg>'
    )


TARGETS = [
    ROOT / "app" / "public" / "index.html",
    ROOT / "app" / "public" / "brand.html",
]


def main():
    for p in TARGETS:
        s = p.read_text()
        before = s.count(OLD_PATH_MARKER)

        # 1. Any inline <svg> that draws the old mark.
        s = re.sub(r"<svg\b[^>]*>(?:(?!</svg>).)*?" + re.escape(OLD_PATH_MARKER) + r".*?</svg>",
                   lambda _m: new_svg(), s, flags=re.S)

        # 2. The app footer's gradient logo, which used the upstream wifi glyph.
        s = re.sub(r'<svg class="icon logo">(?:(?!</svg>).)*?</svg>',
                   lambda _m: new_svg(cls="icon logo"), s, flags=re.S)

        p.write_text(s)
        after = s.count(OLD_PATH_MARKER)
        print(f"{p.name:12} replaced {before - after} mark(s); {after} still present")


if __name__ == "__main__":
    main()
