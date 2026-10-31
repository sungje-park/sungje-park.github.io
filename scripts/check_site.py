#!/usr/bin/env python3
"""Check generated HTML links, asset paths, anchors, JSON-LD, and XML offline."""

import argparse
import json
import sys
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit


class Document(HTMLParser):
    def __init__(self, text):
        super().__init__(convert_charrefs=True)
        self.anchors = set()
        self.references = []
        self.errors = []
        self.jsonld = None
        self.feed(text)
        self.close()

    def handle_starttag(self, tag, pairs):
        attrs = dict(pairs)
        if attrs.get("id"):
            if attrs["id"] in self.anchors:
                self.errors.append(f"duplicate id: {attrs['id']}")
            self.anchors.add(attrs["id"])
        if tag == "a" and attrs.get("name"):
            self.anchors.add(attrs["name"])
        self.references.extend(attrs[key] for key in ("href", "src") if attrs.get(key))
        if attrs.get("srcset") and not attrs["srcset"].startswith("data:"):
            self.references.extend(part.strip().split()[0] for part in attrs["srcset"].split(",") if part.strip())
        if tag == "img" and "alt" not in attrs:
            self.errors.append(f"image missing alt: {attrs.get('src')}")
        if tag == "script" and attrs.get("type") == "application/ld+json":
            self.jsonld = []

    def handle_data(self, data):
        if self.jsonld is not None:
            self.jsonld.append(data)

    def handle_endtag(self, tag):
        if tag == "script" and self.jsonld is not None:
            try:
                json.loads("".join(self.jsonld))
            except ValueError as error:
                self.errors.append(f"invalid JSON-LD: {error}")
            self.jsonld = None


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path)
    parser.add_argument("--base-url", default="/", help="The same baseURL used for the Hugo build")
    args = parser.parse_args()
    root = args.directory.resolve()
    if not (root / "index.html").is_file():
        parser.error(f"No generated index.html in {root}")
    base = urlsplit(args.base_url)
    prefix = unquote(base.path).rstrip("/") + "/"
    documents = {path.resolve(): Document(path.read_text(encoding="utf-8")) for path in root.rglob("*.html")}
    errors = []
    checked = 0
    for path, document in documents.items():
        label = path.relative_to(root)
        errors.extend(f"{label}: {error}" for error in document.errors)
        for reference in document.references:
            url = urlsplit(reference)
            if url.scheme and url.scheme not in ("http", "https"):
                continue
            if url.netloc and url.netloc != base.netloc:
                continue
            checked += 1
            url_path = unquote(url.path)
            if url_path.startswith("/"):
                if not url_path.startswith(prefix):
                    errors.append(f"{label}: link outside site base path: {reference}")
                    continue
                target = root / url_path[len(prefix):]
            else:
                target = path.parent / url_path if url_path else path
            target = target.resolve()
            if not target.is_relative_to(root):
                errors.append(f"{label}: link outside output directory: {reference}")
                continue
            if target.is_dir():
                target /= "index.html"
            if not target.is_file():
                errors.append(f"{label}: missing target: {reference}")
            elif url.fragment and target in documents and unquote(url.fragment) not in documents[target].anchors:
                errors.append(f"{label}: missing anchor: {reference}")
    for path in root.rglob("*.xml"):
        try:
            ET.parse(path)
        except ET.ParseError as error:
            errors.append(f"{path.relative_to(root)}: invalid XML: {error}")
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print(f"Checked {len(documents)} HTML pages and {checked} internal references; XML and JSON-LD are valid.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
