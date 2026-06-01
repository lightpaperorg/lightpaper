"""License info map and copyright notice generator."""

from __future__ import annotations

LICENSES: dict[str, dict] = {
    "all-rights-reserved": {
        "name": "All Rights Reserved",
        "short": "All rights reserved",
        "url": None,
        "spdx": None,
    },
    "cc-by-4.0": {
        "name": "Creative Commons Attribution 4.0 International",
        "short": "CC BY 4.0",
        "url": "https://creativecommons.org/licenses/by/4.0/",
        "spdx": "CC-BY-4.0",
    },
    "cc-by-sa-4.0": {
        "name": "Creative Commons Attribution-ShareAlike 4.0 International",
        "short": "CC BY-SA 4.0",
        "url": "https://creativecommons.org/licenses/by-sa/4.0/",
        "spdx": "CC-BY-SA-4.0",
    },
    "cc-by-nc-4.0": {
        "name": "Creative Commons Attribution-NonCommercial 4.0 International",
        "short": "CC BY-NC 4.0",
        "url": "https://creativecommons.org/licenses/by-nc/4.0/",
        "spdx": "CC-BY-NC-4.0",
    },
    "cc-by-nc-sa-4.0": {
        "name": "Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International",
        "short": "CC BY-NC-SA 4.0",
        "url": "https://creativecommons.org/licenses/by-nc-sa/4.0/",
        "spdx": "CC-BY-NC-SA-4.0",
    },
    "cc0": {
        "name": "CC0 1.0 Universal (Public Domain)",
        "short": "CC0 1.0 — Public Domain",
        "url": "https://creativecommons.org/publicdomain/zero/1.0/",
        "spdx": "CC0-1.0",
    },
}

VALID_LICENSES = set(LICENSES.keys())


def get_license_info(license_key: str) -> dict:
    """Get license metadata. Falls back to all-rights-reserved for unknown keys."""
    return LICENSES.get(license_key, LICENSES["all-rights-reserved"])


def copyright_notice(author_name: str | None, year: int | None, license_key: str) -> str:
    """Generate a copyright footer line: '© 2026 Author Name. CC BY 4.0.'"""
    info = get_license_info(license_key)
    parts = []
    if author_name and year:
        parts.append(f"\u00a9 {year} {author_name}.")
    elif author_name:
        parts.append(f"\u00a9 {author_name}.")
    parts.append(info["short"] + ".")
    return " ".join(parts)
