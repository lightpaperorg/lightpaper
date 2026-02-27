"""KSUID-style document ID generator: doc_ + 11 base62 chars (time-sortable)."""

import os
import struct
import time

BASE62 = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
EPOCH = 1740000000  # 2025-02-20 — custom epoch for compact IDs


def _base62_encode(num: int, length: int) -> str:
    result = []
    while num > 0:
        result.append(BASE62[num % 62])
        num //= 62
    return "".join(reversed(result)).rjust(length, "0")


def generate_doc_id() -> str:
    """Generate a time-sortable document ID: doc_ + 11 base62 chars."""
    ts = int(time.time()) - EPOCH
    rand = struct.unpack(">I", os.urandom(4))[0]
    # 4 bytes timestamp + 4 bytes random = 8 bytes = fits in 11 base62 chars
    combined = (ts << 32) | rand
    return "doc_" + _base62_encode(combined, 11)
