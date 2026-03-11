#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any


API_BASE = "https://api.heygen.com"


def load_local_env() -> None:
    env_path = Path(__file__).resolve().parent.parent / ".env.local"
    if not env_path.is_file():
        return

    for raw_line in env_path.read_text().splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip())


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Probe HeyGen account access and resolve a talking photo or avatar ID."
    )
    parser.add_argument(
        "--talking-photo-id",
        default=os.environ.get("HEYGEN_TALKING_PHOTO_ID", ""),
        help="Talking photo ID to resolve. Defaults to HEYGEN_TALKING_PHOTO_ID.",
    )
    parser.add_argument(
        "--avatar-id",
        default="",
        help="Optional studio avatar ID to resolve separately.",
    )
    parser.add_argument(
        "--voice-name",
        default="Oleksandr Kuguk",
        help="Optional voice name fragment to search for.",
    )
    return parser.parse_args()


def api_get(path: str, api_key: str) -> Any:
    request = urllib.request.Request(
        f"{API_BASE}{path}",
        headers={
            "X-Api-Key": api_key,
            "Content-Type": "application/json",
        },
    )
    with urllib.request.urlopen(request, timeout=60) as response:
        return json.load(response)


def find_item(items: list[dict[str, Any]], key_name: str, needle: str) -> dict[str, Any] | None:
    for item in items:
        if item.get(key_name) == needle:
            return item
    return None


def filter_voice_samples(voices: list[dict[str, Any]], query: str) -> list[dict[str, Any]]:
    lowered = query.lower()
    matches: list[dict[str, Any]] = []
    for voice in voices:
        name = str(voice.get("name", ""))
        if lowered in name.lower():
            matches.append(
                {
                    "voice_id": voice.get("voice_id"),
                    "name": name,
                    "language": voice.get("language"),
                    "gender": voice.get("gender"),
                    "support_pause": voice.get("support_pause"),
                    "emotion_support": voice.get("emotion_support"),
                    "support_interactive_avatar": voice.get("support_interactive_avatar"),
                }
            )
    return matches[:10]


def main() -> int:
    load_local_env()
    args = parse_args()
    api_key = os.environ.get("HEYGEN_API_KEY")
    if not api_key:
        print("Missing HEYGEN_API_KEY in environment.", file=sys.stderr)
        return 1

    try:
        avatars_payload = api_get("/v2/avatars", api_key)
        voices_payload = api_get("/v2/voices", api_key)
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        print(
            json.dumps(
                {
                    "ok": False,
                    "error": f"HTTP {exc.code}",
                    "body": body[:1000],
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return 1

    avatars_data = avatars_payload.get("data", {})
    avatar_items = avatars_data.get("avatars") or []
    talking_photo_items = avatars_data.get("talking_photos") or []

    resolved_talking_photo: dict[str, Any] = {"provided_id": args.talking_photo_id}
    if args.talking_photo_id:
        talking_photo_match = find_item(talking_photo_items, "talking_photo_id", args.talking_photo_id)
        if talking_photo_match:
            resolved_talking_photo["type"] = "talking_photo"
            resolved_talking_photo["record"] = {
                "talking_photo_id": talking_photo_match.get("talking_photo_id"),
                "talking_photo_name": talking_photo_match.get("talking_photo_name"),
                "preview_image_url": talking_photo_match.get("preview_image_url"),
            }
        else:
            resolved_talking_photo["type"] = "not_found"

    resolved_avatar: dict[str, Any] = {"provided_id": args.avatar_id}
    if args.avatar_id:
        avatar_match = find_item(avatar_items, "avatar_id", args.avatar_id)
        if avatar_match:
            resolved_avatar["type"] = "avatar"
            resolved_avatar["record"] = {
                "avatar_id": avatar_match.get("avatar_id"),
                "avatar_name": avatar_match.get("avatar_name"),
                "gender": avatar_match.get("gender"),
                "preview_image_url": avatar_match.get("preview_image_url"),
                "preview_video_url": avatar_match.get("preview_video_url"),
                "default_voice_id": avatar_match.get("default_voice_id"),
            }
        else:
            resolved_avatar["type"] = "not_found"

    voices_data = voices_payload.get("data", {})
    voice_items = voices_data.get("voices") or []

    output = {
        "ok": True,
        "accounts_scope": {
            "avatars_count": len(avatar_items),
            "talking_photos_count": len(talking_photo_items),
            "voices_count": len(voice_items),
        },
        "resolved_talking_photo": resolved_talking_photo,
        "resolved_avatar": resolved_avatar,
        "voice_matches": filter_voice_samples(voice_items, args.voice_name),
    }
    print(json.dumps(output, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
