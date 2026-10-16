#!/usr/bin/env python3
"""Static checks for the declared Minecraft Java 1.13–26.3 resource-pack range."""

import json
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "MustacheStorage"


def check(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def main() -> None:
    metadata = json.loads((PACK / "pack.mcmeta").read_text(encoding="utf-8"))["pack"]

    # 1.13–1.21.8 clients need the legacy fields; newer clients need both bounds.
    check(metadata.get("pack_format") == 41, "Unexpected legacy pack_format")
    legacy = metadata.get("supported_formats", {})
    check(legacy.get("min_inclusive") == 4, "Minimum legacy format should be 4 (1.13)")
    check(legacy.get("max_inclusive") == 64, "Legacy maximum must be 64 (1.21.8)")
    check(metadata.get("min_format") == 4, "Minimum format should be 4 (1.13)")
    check(metadata.get("max_format") == [97, 1], "Maximum format must be 97.1 (26.3)")

    # These three names are also used by the vanilla Minecraft 26.3 chest atlas.
    chest_dir = PACK / "assets/minecraft/textures/entity/chest"
    for name in ("normal.png", "normal_left.png", "normal_right.png"):
        texture = chest_dir / name
        raw = texture.read_bytes()
        check(raw[:8] == b"\x89PNG\r\n\x1a\n", f"Not a PNG: {texture}")
        check(raw[12:16] == b"IHDR" and len(raw) >= 24, f"Invalid PNG header: {texture}")
        width, height = struct.unpack(">II", raw[16:24])
        check(width > 0 and height > 0, f"Invalid PNG dimensions: {texture}")

    print("Static resource-pack metadata and chest texture validation passed (1.13–26.3).")


if __name__ == "__main__":
    main()
