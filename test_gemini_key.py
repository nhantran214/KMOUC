#!/usr/bin/env python3
"""Smoke test for a Google Gemini API key."""

from __future__ import annotations

import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from google import genai

MODULE_DIR = Path(__file__).resolve().parent
load_dotenv(MODULE_DIR / ".env")

API_KEY = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")


def mask_key(key: str) -> str:
    if len(key) <= 12:
        return "(hidden)"
    return f"{key[:8]}...{key[-4:]}"


def main() -> int:
    if not API_KEY:
        print(
            "ERROR: Missing API key.\n"
            "Set GOOGLE_API_KEY or GEMINI_API_KEY in your shell or in Module_8/.env"
        )
        return 1

    print(f"API key: {mask_key(API_KEY)}")
    print(f"Model: {MODEL}")
    print("Calling Gemini...")

    client = genai.Client(api_key=API_KEY)
    try:
        response = client.models.generate_content(
            model=MODEL,
            contents="Reply with exactly one word: OK",
        )
        text = (response.text or "").strip()
        print(f"SUCCESS: {text!r}")
        return 0
    except Exception as exc:
        print(f"FAILED: {type(exc).__name__}: {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
