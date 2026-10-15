#!/usr/bin/env python3
"""Defensive version check for Apple's CVE-2025-43418 advisory.

This tool compares a user-supplied OS version with Apple's published fixed
versions. It does not connect to devices, trigger Spotlight/lock-screen flows,
or access device data. It is advisory-only and cannot prove patch installation.
"""
from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass


VERSION_RE = re.compile(r"^\s*(\d+)\.(\d+)(?:\.(\d+))?\s*$")


@dataclass(frozen=True)
class Assessment:
    status: str
    message: str


def parse_version(value: str) -> tuple[int, int, int] | None:
    """Parse a dotted Apple OS version; return None for malformed input."""
    match = VERSION_RE.fullmatch(value)
    if not match:
        return None
    major, minor, patch = (int(part or 0) for part in match.groups())
    return major, minor, patch


def assess_version(value: str) -> Assessment:
    """Classify known iOS/iPadOS release branches using Apple's fixed versions."""
    version = parse_version(value)
    if version is None:
        return Assessment("UNKNOWN", "Versi tidak valid; gunakan format seperti 18.7.1 atau 26.1.")

    major, minor, patch = version
    if major == 18:
        if version >= (18, 7, 2):
            return Assessment(
                "PATCH_LEVEL_MEETS_ADVISORY",
                "Versi memenuhi ambang perbaikan iOS/iPadOS 18.7.2 yang disebut Apple.",
            )
        return Assessment(
            "UPDATE_REQUIRED",
            "Versi lebih lama dari iOS/iPadOS 18.7.2; perbarui ke rilis aman yang tersedia untuk perangkat.",
        )
    if major == 26:
        if version >= (26, 1, 0):
            return Assessment(
                "PATCH_LEVEL_MEETS_ADVISORY",
                "Versi memenuhi ambang perbaikan iOS/iPadOS 26.1 yang disebut Apple.",
            )
        return Assessment(
            "UPDATE_REQUIRED",
            "Versi lebih lama dari iOS/iPadOS 26.1; perbarui ke rilis aman yang tersedia untuk perangkat.",
        )
    return Assessment(
        "MANUAL_REVIEW_REQUIRED",
        "Cabang versi ini tidak dinilai otomatis. Verifikasi model perangkat dan jalur pembaruan pada advisori Apple.",
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Pemeriksaan defensif ambang versi CVE-2025-43418 (tanpa exploit)."
    )
    parser.add_argument("version", help="Versi iOS/iPadOS, misalnya 18.7.1 atau 26.1")
    args = parser.parse_args()
    result = assess_version(args.version)
    print(f"Assessment: {result.status}")
    print(result.message)
    print("Catatan: pemeriksaan versi ini bukan bukti forensik bahwa patch terpasang.")
    print("Advisori Apple: https://support.apple.com/en-us/125633")
    print("Advisori Apple: https://support.apple.com/en-us/125632")
    return 0 if result.status == "PATCH_LEVEL_MEETS_ADVISORY" else 1


if __name__ == "__main__":
    sys.exit(main())
