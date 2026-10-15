#!/usr/bin/env python3
"""Sinkronkan CVE iOS/iPadOS dari halaman keamanan resmi Apple.

Sumber utama adalah indeks rilis keamanan Apple dan halaman advisori Apple.
Skrip ini mengumpulkan CVE yang disebutkan Apple; bukan alat eksploitasi.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import time
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin, urlparse
from urllib.request import Request, urlopen

INDEX_URL = "https://support.apple.com/en-us/100100"
OUTPUT = Path("data/ios-ipados-cves.json")
CVE_RE = re.compile(r"\bCVE-\d{4}-\d{4,}\b", re.IGNORECASE)
IOS_TITLE_RE = re.compile(r"\b(iOS|iPadOS)\b", re.IGNORECASE)
DATE_RE = re.compile(r"(?:Released|Published|Posted)\s+([A-Z][a-z]+\s+\d{1,2},\s+\d{4})", re.I)
USER_AGENT = "Strong-Bee-mdm_server-CVE-catalog/1.0 (public defensive security research)"


class PageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.text_parts: list[str] = []
        self.links: list[tuple[str, str]] = []
        self._anchor_depth = 0
        self._anchor_href = ""
        self._anchor_text: list[str] = ""

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attrs_dict = dict(attrs)
        if tag.lower() == "a":
            self._anchor_depth += 1
            if self._anchor_depth == 1:
                self._anchor_href = attrs_dict.get("href") or ""
                self._anchor_text = []

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() == "a" and self._anchor_depth:
            self._anchor_depth -= 1
            if self._anchor_depth == 0 and self._anchor_href:
                self.links.append((self._anchor_href, " ".join(self._anchor_text).strip()))
                self._anchor_href = ""
                self._anchor_text = []

    def handle_data(self, data: str) -> None:
        clean = " ".join(data.split())
        if clean:
            self.text_parts.append(clean)
            if self._anchor_depth:
                self._anchor_text.append(clean)

    @property
    def text(self) -> str:
        return " ".join(self.text_parts)


def fetch(url: str, timeout: int = 30) -> str:
    parsed = urlparse(url)
    if parsed.scheme != "https" or parsed.hostname not in {"support.apple.com", "www.apple.com"}:
        raise ValueError(f"URL sumber tidak diizinkan: {url}")
    request = Request(url, headers={"User-Agent": USER_AGENT, "Accept": "text/html"})
    with urlopen(request, timeout=timeout) as response:
        charset = response.headers.get_content_charset() or "utf-8"
        return response.read().decode(charset, errors="replace")


def extract_advisory_links(html: str, base_url: str = INDEX_URL) -> list[tuple[str, str]]:
    parser = PageParser()
    parser.feed(html)
    found: dict[str, str] = {}
    for href, title in parser.links:
        url = urljoin(base_url, href).split("#", 1)[0]
        parsed = urlparse(url)
        if parsed.scheme != "https" or parsed.hostname not in {"support.apple.com", "www.apple.com"}:
            continue
        if IOS_TITLE_RE.search(title) and re.search(r"security|content", title, re.I):
            found[url] = title or url
    return sorted(found.items())


def extract_cves(text: str, url: str, title: str) -> list[dict[str, str]]:
    date_match = DATE_RE.search(text)
    published = date_match.group(1) if date_match else ""
    ids = sorted({match.upper() for match in CVE_RE.findall(text)})
    results = []
    for cve in ids:
        pos = text.upper().find(cve)
        excerpt = " ".join(text[max(0, pos - 220):pos + len(cve) + 220].split())
        results.append({
            "cve": cve,
            "product": "iOS/iPadOS",
            "advisory_title": title,
            "published_date": published,
            "context": excerpt,
            "apple_advisory_url": url,
            "source": "Apple Security Updates",
        })
    return results


def sync(output: Path = OUTPUT, max_advisories: int | None = None, delay: float = 0.4) -> dict:
    index_html = fetch(INDEX_URL)
    advisories = extract_advisory_links(index_html)
    if not advisories:
        raise RuntimeError("Tidak menemukan tautan advisori iOS/iPadOS di indeks Apple; data lama tidak ditimpa.")
    if max_advisories is not None:
        advisories = advisories[:max_advisories]

    records: dict[str, dict] = {}
    failures: list[dict[str, str]] = []
    for index, (url, title) in enumerate(advisories):
        try:
            html = fetch(url)
            parser = PageParser()
            parser.feed(html)
            for item in extract_cves(parser.text, url, title):
                existing = records.get(item["cve"])
                if existing:
                    urls = set(existing.get("advisory_urls", [existing["apple_advisory_url"]]))
                    urls.add(url)
                    existing["advisory_urls"] = sorted(urls)
                    if not existing.get("published_date") and item["published_date"]:
                        existing["published_date"] = item["published_date"]
                else:
                    item["advisory_urls"] = [url]
                    records[item["cve"]] = item
        except (HTTPError, URLError, TimeoutError, ValueError, UnicodeError) as exc:
            failures.append({"url": url, "error": str(exc)})
        if index + 1 < len(advisories):
            time.sleep(max(0.0, delay))

    if failures and not records:
        raise RuntimeError(f"Gagal membaca seluruh advisori ({len(failures)} kegagalan); data lama tidak ditimpa.")
    payload = {
        "schema_version": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "scope": "CVE yang tercantum pada advisori keamanan resmi Apple untuk iOS/iPadOS",
        "source_index": INDEX_URL,
        "advisories_checked": len(advisories),
        "advisory_fetch_failures": failures,
        "total_unique_cves": len(records),
        "cves": sorted(records.values(), key=lambda item: item["cve"]),
        "notice": "Katalog ini mencerminkan CVE yang dipublikasikan Apple dan ditemukan oleh sinkronisasi. Ini bukan jaminan seluruh CVE pihak ketiga atau seluruh kerentanan yang belum diberi CVE tercakup.",
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    temp = output.with_suffix(output.suffix + ".tmp")
    temp.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temp.replace(output)
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description="Sinkronkan katalog CVE iOS/iPadOS dari advisori Apple.")
    parser.add_argument("--output", type=Path, default=OUTPUT, help="Lokasi berkas JSON keluaran")
    parser.add_argument("--max-advisories", type=int, help="Batas jumlah advisori (untuk pengujian)")
    parser.add_argument("--delay", type=float, default=0.4, help="Jeda antarpemintaan dalam detik")
    args = parser.parse_args()
    try:
        result = sync(args.output, args.max_advisories, args.delay)
    except Exception as exc:  # CLI harus gagal secara jelas agar CI tidak menimpa data dengan hasil kosong.
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(f"Selesai: {result['total_unique_cves']} CVE unik dari {result['advisories_checked']} advisori.")
    if result["advisory_fetch_failures"]:
        print(f"Peringatan: {len(result['advisory_fetch_failures'])} advisori gagal diambil.")
    print(f"Data tersimpan di {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
