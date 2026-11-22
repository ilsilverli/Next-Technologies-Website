#!/usr/bin/env python3
"""Build ar/index.html (https://nextec.sa/ar/) from index.html and i18n/ar.json.

index.html is the single source of layout and English text. Every element that
carries data-i="key" gets its contents replaced with the Arabic text for that key;
page-level details (language, direction, title, description, preview tags,
accessibility labels, asset paths) are switched to their Arabic versions.

Run from the repository root after any change to index.html or i18n/ar.json:

    python3 tools/build_arabic.py

The script stops with an error instead of writing a partial page if anything it
expects is missing, so a successful run means the Arabic page is complete.
"""
import json
import pathlib
import sys
from html.parser import HTMLParser

ROOT = pathlib.Path(__file__).resolve().parent.parent
SOURCE = ROOT / "index.html"
STRINGS = ROOT / "i18n" / "ar.json"
OUTPUT = ROOT / "ar" / "index.html"

VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link",
        "meta", "source", "track", "wbr"}


class TranslatableSpans(HTMLParser):
    """Find the inner-content byte range of every element with data-i."""

    def __init__(self, text):
        super().__init__(convert_charrefs=False)
        self.text = text
        self.line_starts = [0]
        for i, ch in enumerate(text):
            if ch == "\n":
                self.line_starts.append(i + 1)
        self.stack = []   # (tag, key or None, inner_start)
        self.spans = []   # (key, inner_start, inner_end, depth_of_keyed_ancestors)

    def char_pos(self):
        line, col = self.getpos()
        return self.line_starts[line - 1] + col

    def handle_starttag(self, tag, attrs):
        if tag in VOID:
            return
        key = dict(attrs).get("data-i")
        start = self.char_pos() + len(self.get_starttag_text())
        self.stack.append((tag, key, start))

    def handle_endtag(self, tag):
        if tag in VOID:
            return
        end = self.char_pos()
        while self.stack:
            open_tag, key, start = self.stack.pop()
            if key:
                nested = sum(1 for _, k, _ in self.stack if k)
                self.spans.append((key, start, end, nested))
            if open_tag == tag:
                break


def replace_once(text, old, new, label):
    count = text.count(old)
    if count != 1:
        sys.exit(f"build_arabic: expected exactly one {label!r} in index.html, found {count}")
    return text.replace(old, new)


def replace_all(text, old, new, label, minimum=1):
    count = text.count(old)
    if count < minimum:
        sys.exit(f"build_arabic: expected {label!r} in index.html, found none")
    return text.replace(old, new)


def main():
    # Read without newline translation so the output keeps the source's line endings.
    with SOURCE.open(encoding="utf-8", newline="") as fh:
        source = fh.read()
    strings = json.loads(STRINGS.read_text(encoding="utf-8"))
    page, text = strings["page"], strings["text"]

    parser = TranslatableSpans(source)
    parser.feed(source)
    parser.close()
    if parser.stack and any(k for _, k, _ in parser.stack):
        sys.exit("build_arabic: an element with data-i was never closed")

    # Only outermost translatable elements are replaced, as the page did before.
    spans = [s for s in parser.spans if s[3] == 0]
    missing = sorted({k for k, *_ in spans if k not in text})
    if missing:
        sys.exit("build_arabic: no Arabic text for: " + ", ".join(missing))

    out = source
    for key, start, end, _ in sorted(spans, key=lambda s: s[1], reverse=True):
        out = out[:start] + text[key] + out[end:]

    # Page language, direction, title and description.
    out = replace_once(out, '<html lang="en" dir="ltr">', '<html lang="ar" dir="rtl">', "html tag")
    out = replace_once(out, "<title>Next Technologies | Technology Advisory &amp; Solution Architecture in Riyadh</title>",
                       f"<title>{page['title']}</title>", "title")
    desc_en = "Next Technologies connects business priorities with practical technology through advisory, solution architecture and integration."
    out = replace_once(out, f'<meta name="description" content="{desc_en}">',
                       f'<meta name="description" content="{page["description"]}">', "meta description")

    # Search-engine and link-preview tags.
    out = replace_once(out, '<link rel="canonical" href="https://nextec.sa/">',
                       '<link rel="canonical" href="https://nextec.sa/ar/">', "canonical")
    out = replace_once(out, '<meta property="og:site_name" content="Next Technologies">',
                       f'<meta property="og:site_name" content="{page["siteName"]}">', "og:site_name")
    out = replace_once(out, '<meta property="og:title" content="Next Technologies | Technology Advisory &amp; Solution Architecture in Riyadh">',
                       f'<meta property="og:title" content="{page["title"]}">', "og:title")
    out = replace_once(out, f'<meta property="og:description" content="{desc_en}">',
                       f'<meta property="og:description" content="{page["description"]}">', "og:description")
    out = replace_once(out, '<meta property="og:url" content="https://nextec.sa/">',
                       '<meta property="og:url" content="https://nextec.sa/ar/">', "og:url")
    out = replace_once(out, '<meta property="og:locale" content="en_US">\r\n<meta property="og:locale:alternate" content="ar_SA">',
                       '<meta property="og:locale" content="ar_SA">\r\n<meta property="og:locale:alternate" content="en_US">', "og:locale")

    # Language link points back to English.
    out = replace_once(out, '<a class="lang" id="language" href="ar/" lang="ar" hreflang="ar" aria-label="Switch to Arabic">العربية</a>',
                       f'<a class="lang" id="language" href="../" lang="en" hreflang="en" aria-label="{page["switchLabel"]}">English</a>',
                       "language link")

    # Accessibility labels.
    out = replace_all(out, 'aria-label="Next Technologies home"', f'aria-label="{page["homeLabel"]}"', "home label")
    out = replace_once(out, 'aria-label="Main navigation"', f'aria-label="{page["mainNavLabel"]}"', "main nav label")
    out = replace_once(out, 'aria-label="Footer navigation"', f'aria-label="{page["footerNavLabel"]}"', "footer nav label")
    out = replace_once(out, 'aria-label="Open navigation"', f'aria-label="{page["openNavLabel"]}"', "menu label")

    # Enquiry email shows the visitor's language.
    out = replace_once(out, '<input type="hidden" name="Language" value="English">',
                       '<input type="hidden" name="Language" value="Arabic">', "language field")

    # The Arabic page lives one folder down, so local assets move up a level.
    out = replace_all(out, 'src="assets/', 'src="../assets/', "image paths")
    out = replace_all(out, "url(assets/", "url(../assets/", "font paths")

    OUTPUT.parent.mkdir(exist_ok=True)
    with OUTPUT.open("w", encoding="utf-8", newline="") as fh:
        fh.write(out)
    print(f"Built {OUTPUT.relative_to(ROOT)}: {len(spans)} texts translated, {len(out.encode('utf-8'))} bytes")


if __name__ == "__main__":
    main()
