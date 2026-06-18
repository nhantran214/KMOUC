#!/usr/bin/env python3
"""Build Korean notebook from English Module 3 LLMs notebook."""

from __future__ import annotations

import json
import re
from pathlib import Path

from _module3_ko_translations import MARKDOWN_KO, PRINT_REPLACEMENTS

SRC = Path(__file__).with_name(
    "Module_3_Practical_LLMs_at_Work_Local_Models_and_Prompt_Engineering.ipynb"
)
DST = Path(__file__).with_name(
    "Module_3_Practical_LLMs_at_Work_Local_Models_and_Prompt_Engineering_KO.ipynb"
)


def _find_print_spans(source: str) -> list[tuple[int, int]]:
    spans: list[tuple[int, int]] = []
    i = 0
    while i < len(source):
        m = re.search(r"\bprint\s*\(", source[i:])
        if not m:
            break
        start = i + m.start()
        j = i + m.end() - 1
        depth = 0
        in_str: str | None = None
        escape = False
        while j < len(source):
            ch = source[j]
            if in_str:
                if escape:
                    escape = False
                elif ch == "\\":
                    escape = True
                elif ch == in_str:
                    in_str = None
            else:
                if ch in ("'", '"'):
                    in_str = ch
                elif ch == "(":
                    depth += 1
                elif ch == ")":
                    depth -= 1
                    if depth == 0:
                        spans.append((start, j + 1))
                        i = j + 1
                        break
            j += 1
        else:
            break
    return spans


def _literal_newline_pairs(
    english: str, korean: str
) -> list[tuple[str, str]]:
    pairs = [(english, korean)]
    if "\n" in english or "\n" in korean:
        pairs.append(
            (
                english.replace("\n", "\\n"),
                korean.replace("\n", "\\n"),
            )
        )
    return pairs


def _translate_prints(source: str) -> str:
    replacements = [(a, b) for a, b in PRINT_REPLACEMENTS if a != b]
    expanded: list[tuple[str, str]] = []
    for english, korean in replacements:
        expanded.extend(_literal_newline_pairs(english, korean))
    expanded.sort(key=lambda pair: len(pair[0]), reverse=True)
    spans = _find_print_spans(source)
    if not spans:
        return source
    parts: list[str] = []
    prev = 0
    for start, end in spans:
        parts.append(source[prev:start])
        chunk = source[start:end]
        for english, korean in expanded:
            chunk = chunk.replace(english, korean)
        parts.append(chunk)
        prev = end
    parts.append(source[prev:])
    return "".join(parts)


def _to_source_list(text: str) -> list[str]:
    if not text:
        return []
    return text.splitlines(keepends=True)


def build() -> None:
    nb = json.loads(SRC.read_text(encoding="utf-8"))
    for idx, cell in enumerate(nb["cells"]):
        cell["execution_count"] = None
        cell["outputs"] = []
        if cell["cell_type"] == "markdown":
            if idx in MARKDOWN_KO:
                cell["source"] = _to_source_list(MARKDOWN_KO[idx])
        elif cell["cell_type"] == "code":
            original = "".join(cell.get("source", []))
            translated = _translate_prints(original)
            cell["source"] = _to_source_list(translated)
    DST.write_text(
        json.dumps(nb, ensure_ascii=False, indent=1) + "\n",
        encoding="utf-8",
    )
    print(f"Wrote {DST}")


if __name__ == "__main__":
    build()
