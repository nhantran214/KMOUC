#!/usr/bin/env python3
"""Download additional maritime DBpedia abstracts via SPARQL (optional, larger corpus).

Requires network access to https://dbpedia.org/sparql

Example:
  python scripts/download_dbpedia_maritime_sparql.py --limit 150 --out data/dbpedia_maritime_sparql.txt
"""

from __future__ import annotations

import argparse
import json
import urllib.parse
import urllib.request
from pathlib import Path

QUERY = """
PREFIX dbo: <http://dbpedia.org/ontology/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT ?entity ?label ?abstract WHERE {
  {
    ?entity a dbo:Port ; rdfs:label ?label ; dbo:abstract ?abstract .
  } UNION {
    ?entity a dbo:Canal ; rdfs:label ?label ; dbo:abstract ?abstract .
  } UNION {
    ?entity a dbo:Ship ; rdfs:label ?label ; dbo:abstract ?abstract .
  } UNION {
    ?entity a dbo:Company ; rdfs:label ?label ; dbo:abstract ?abstract .
    FILTER (regex(?abstract, "port|shipping|maritime|vessel|logistics|canal|freight|container", "i"))
  }
  FILTER (lang(?label) = "en")
  FILTER (lang(?abstract) = "en")
  FILTER (strlen(?abstract) > 120 && strlen(?abstract) < 1800)
}
LIMIT %LIMIT%
"""


def fetch(limit: int) -> list[tuple[str, str, str]]:
    q = QUERY.replace("%LIMIT%", str(limit))
    url = "https://dbpedia.org/sparql?" + urllib.parse.urlencode(
        {"query": q, "format": "application/sparql-results+json"}
    )
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "KMOU-Module8/1.0", "Accept": "application/sparql-results+json"},
    )
    with urllib.request.urlopen(req, timeout=180) as resp:
        payload = json.loads(resp.read().decode("utf-8"))
    rows = []
    for b in payload["results"]["bindings"]:
        entity = b["entity"]["value"].rsplit("/", 1)[-1]
        label = b["label"]["value"]
        abstract = b["abstract"]["value"]
        rows.append((entity, label, abstract))
    return rows


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=120)
    parser.add_argument(
        "--out",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "data" / "dbpedia_maritime_sparql.txt",
    )
    args = parser.parse_args()

    rows = fetch(args.limit)
    lines = [
        "DBpedia Maritime SPARQL Corpus — Module 8",
        "",
        f"Downloaded via DBpedia SPARQL endpoint ({len(rows)} entities).",
        "License: CC BY-SA (DBpedia / Wikipedia).",
        "",
    ]
    for i, (entity, label, abstract) in enumerate(rows, start=1):
        lines.append(f"[{i}] {entity} ({label})")
        lines.append(abstract.strip())
        lines.append("")

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {args.out} ({len(rows)} entries, {args.out.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()
