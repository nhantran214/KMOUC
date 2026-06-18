#!/usr/bin/env python3
"""Smoke test for LLM API keys (Gemini and OpenAI)."""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

REPO_DIR = Path(__file__).resolve().parent
MODULE_8_DIR = REPO_DIR / "Module_8"

load_dotenv(REPO_DIR / ".env")
load_dotenv(MODULE_8_DIR / ".env")

PROMPT = "Reply with exactly one word: OK"
GEMINI_INSTALL_HINT = (
    "Install Gemini support: python -m pip install google-genai "
    "(or langchain-google-genai)"
)


def mask_key(key: str) -> str:
    if len(key) <= 12:
        return "(hidden)"
    return f"{key[:8]}...{key[-4:]}"


def call_gemini(api_key: str, model: str, prompt: str) -> str:
    try:
        from google import genai

        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(model=model, contents=prompt)
        return (response.text or "").strip()
    except ImportError:
        pass

    try:
        from langchain_google_genai import ChatGoogleGenerativeAI

        llm = ChatGoogleGenerativeAI(
            model=model,
            google_api_key=api_key,
            temperature=0,
        )
        return llm.invoke(prompt).content.strip()
    except ImportError:
        pass

    try:
        import google.generativeai as genai_legacy

        genai_legacy.configure(api_key=api_key)
        response = genai_legacy.GenerativeModel(model).generate_content(prompt)
        return (response.text or "").strip()
    except ImportError as exc:
        raise ImportError(GEMINI_INSTALL_HINT) from exc

    raise ImportError(GEMINI_INSTALL_HINT)


def call_openai(api_key: str, model: str, prompt: str) -> str:
    try:
        from openai import OpenAI
    except ImportError as exc:
        raise ImportError(
            "Install OpenAI support: python -m pip install openai"
        ) from exc

    client = OpenAI(api_key=api_key)
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=10,
    )
    return (response.choices[0].message.content or "").strip()


def test_gemini(model: str | None = None) -> int | None:
    """Return 0 on success, 1 on failure, None when no key is configured."""
    api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
    model = model or os.getenv("GEMINI_MODEL", "gemini-2.0-flash")

    if not api_key:
        print("GEMINI: SKIP — set GOOGLE_API_KEY or GEMINI_API_KEY")
        return None

    print(f"GEMINI: key={mask_key(api_key)}, model={model}")
    try:
        text = call_gemini(api_key, model, PROMPT)
        print(f"GEMINI: SUCCESS — {text!r}")
        return 0
    except ImportError as exc:
        print(f"GEMINI: FAILED — {exc}")
        return 1
    except Exception as exc:
        print(f"GEMINI: FAILED — {type(exc).__name__}: {exc}")
        return 1


def test_openai(model: str | None = None) -> int | None:
    """Return 0 on success, 1 on failure, None when no key is configured."""
    api_key = os.getenv("OPENAI_API_KEY")
    model = model or os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    if not api_key:
        print("OPENAI: SKIP — set OPENAI_API_KEY")
        return None

    print(f"OPENAI: key={mask_key(api_key)}, model={model}")
    try:
        text = call_openai(api_key, model, PROMPT)
        print(f"OPENAI: SUCCESS — {text!r}")
        return 0
    except ImportError as exc:
        print(f"OPENAI: FAILED — {exc}")
        return 1
    except Exception as exc:
        print(f"OPENAI: FAILED — {type(exc).__name__}: {exc}")
        return 1


def main() -> int:
    parser = argparse.ArgumentParser(description="Test Gemini and/or OpenAI API keys.")
    parser.add_argument(
        "--provider",
        choices=["gemini", "openai", "all"],
        default="all",
        help="Which provider to test (default: all)",
    )
    parser.add_argument("--gemini-model", default=None, help="Override GEMINI_MODEL")
    parser.add_argument("--openai-model", default=None, help="Override OPENAI_MODEL")
    args = parser.parse_args()

    providers = (
        ["gemini", "openai"] if args.provider == "all" else [args.provider]
    )
    results: dict[str, int | None] = {}
    if "gemini" in providers:
        results["gemini"] = test_gemini(args.gemini_model)
    if "openai" in providers:
        results["openai"] = test_openai(args.openai_model)

    ran = [name for name, code in results.items() if code is not None]
    failed = [name for name, code in results.items() if code == 1]
    missing = [name for name, code in results.items() if code is None]

    if args.provider != "all" and missing:
        return 1
    if not ran:
        print("\nNo API keys found to test.")
        return 1
    if failed:
        print(f"\nFailed: {', '.join(failed)}")
        return 1

    print("\nAll tests passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
