#!/usr/bin/env python3
"""Build DBpedia text corpora for Module 8 from en_100_summaries.csv.

Source (open):
  https://github.com/dice-group/DBpedia-Summarizer
  data_eval/en_100_summaries.csv

Outputs:
  Module_8/data/dbpedia_course_corpus.txt      — full 100-article corpus (notebook default)
  Module_8/data/dbpedia_maritime_corpus.txt    — maritime/logistics-filtered subset
"""

from __future__ import annotations

import csv
import re
from pathlib import Path

MODULE_DIR = Path(__file__).resolve().parents[1]
CSV_PATH = MODULE_DIR / "data" / "dbpedia_en_100_summaries.csv"
OUT_FULL = MODULE_DIR / "data" / "dbpedia_course_corpus.txt"
OUT_MARITIME = MODULE_DIR / "data" / "dbpedia_maritime_corpus.txt"

MARITIME_PATTERN = re.compile(
    r"\b("
    r"port|harbor|harbour|maritime|shipping|vessel|ship|canal|logistics|"
    r"freight|container|dock|navy|suez|panama|maersk|tanker|ferry|"
    r"cargo|seaport|waterway|merchant marine|dockyard|shipyard"
    r")\b",
    re.I,
)

# Extra curated maritime/port entities (DBpedia-style abstracts for course theme)
CURATED_MARITIME = [
    (
        "Port_of_Singapore",
        "The Port of Singapore is a major transshipment hub in Southeast Asia, operated by PSA International. "
        "It connects global shipping routes across Asia, Europe, and the Middle East and is one of the busiest container ports worldwide.",
    ),
    (
        "Port_of_Rotterdam",
        "The Port of Rotterdam is the largest seaport in Europe by cargo throughput. It is located in the Netherlands "
        "and managed by the Port of Rotterdam Authority, serving as a gateway for European logistics and inland distribution.",
    ),
    (
        "Port_of_Busan",
        "The Port of Busan is one of the busiest container ports in South Korea. It is managed by the Busan Port Authority "
        "and functions as a hub for Northeast Asian shipping routes.",
    ),
    (
        "Maersk",
        "A.P. Moller - Maersk is a Danish shipping and logistics company. It operates container shipping through Maersk Line "
        "and provides integrated logistics services worldwide.",
    ),
    (
        "Mediterranean_Shipping_Company",
        "Mediterranean Shipping Company (MSC) is a global container shipping line headquartered in Geneva, Switzerland. "
        "MSC operates a large fleet and serves major trade lanes connecting Asia, Europe, and the Americas.",
    ),
    (
        "Panama_Canal",
        "The Panama Canal is an artificial waterway in Panama connecting the Atlantic and Pacific Oceans. "
        "It is administered by the Panama Canal Authority and shortens interoceanic shipping routes.",
    ),
    (
        "Suez_Canal",
        "The Suez Canal is an artificial sea-level waterway in Egypt linking the Mediterranean Sea and the Red Sea. "
        "It is operated by the Suez Canal Authority and is critical for Europe–Asia maritime trade.",
    ),
    (
        "International_Maritime_Organization",
        "The International Maritime Organization (IMO) is a United Nations agency responsible for international shipping regulation, "
        "including safety, security, and environmental standards adopted by member states.",
    ),
    (
        "DHL",
        "DHL is an international logistics company providing express delivery, freight forwarding, and supply chain services. "
        "It operates hubs near major seaports and airports for multimodal transport.",
    ),
    (
        "Ship_commissioning",
        "Ship commissioning is the process of placing a ship in active service. It includes sea trials, crew training, "
        "and certification before a vessel enters operational duty.",
    ),
    (
        "Port_of_Shanghai",
        "The Port of Shanghai is a major deep-water port in China and one of the world's busiest container ports. "
        "It serves Yangtze River Delta manufacturing exports and global container trade.",
    ),
    (
        "Port_of_Los_Angeles",
        "The Port of Los Angeles is a seaport in San Pedro Bay, California. It handles containerized cargo, automobiles, "
        "and bulk commodities for U.S. West Coast trade.",
    ),
    (
        "Port_of_Hamburg",
        "The Port of Hamburg is Germany's largest seaport on the River Elbe. It is a key European hub for container, bulk, and logistics services.",
    ),
    (
        "Port_of_Antwerp",
        "The Port of Antwerp is one of Europe's largest seaports, located in Belgium. It specializes in container handling, chemicals, and integrated logistics.",
    ),
    (
        "Port_of_Hong_Kong",
        "The Port of Hong Kong is a major deep-water port in southern China. It has historically been a global transshipment and container logistics center.",
    ),
    (
        "Port_of_Dubai",
        "Port Jebel Ali in Dubai is the largest port in the Middle East and a major transshipment hub for global container routes.",
    ),
    (
        "CMA_CGM",
        "CMA CGM is a French container transportation and shipping company. It operates worldwide liner services and port-related logistics.",
    ),
    (
        "COSCO",
        "COSCO Shipping is a Chinese state-owned shipping and logistics company. It operates container fleets and global port investments.",
    ),
    (
        "Evergreen_Marine",
        "Evergreen Marine is a Taiwanese container transportation company. It operates global liner services and container vessels.",
    ),
    (
        "Hapag-Lloyd",
        "Hapag-Lloyd is a German international shipping and container transportation company. It serves major trade lanes worldwide.",
    ),
    (
        "FedEx",
        "FedEx is an American multinational delivery services company. It integrates air freight, ground logistics, and supply chain operations.",
    ),
    (
        "UPS",
        "United Parcel Service (UPS) is an American multinational shipping and logistics company providing parcel and freight services globally.",
    ),
    (
        "Kuehne+Nagel",
        "Kuehne+Nagel is a global transport and logistics company headquartered in Switzerland. It provides sea freight, air freight, and contract logistics.",
    ),
    (
        "Bosporus",
        "The Bosporus is a strait in Turkey connecting the Black Sea and the Sea of Marmara. It is a strategic route for oil tankers and merchant shipping.",
    ),
    (
        "Strait_of_Malacca",
        "The Strait of Malacca is a narrow passage between the Malay Peninsula and Sumatra. It is one of the world's most important shipping lanes for oil and trade.",
    ),
    (
        "English_Channel",
        "The English Channel is a body of water separating southern England from northern France. It is a major route for ferry and cargo traffic.",
    ),
    (
        "Classification_society",
        "A classification society is an organization that establishes and maintains standards for the construction and maintenance of ships and offshore structures.",
    ),
    (
        "Bill_of_lading",
        "A bill of lading is a legal document issued by a carrier to a shipper detailing the type, quantity, and destination of goods being shipped.",
    ),
    (
        "Container_ship",
        "A container ship is a cargo vessel designed to carry intermodal containers. Containerization revolutionized global logistics and port operations.",
    ),
    (
        "Oil_tanker",
        "An oil tanker is a ship designed for bulk transport of oil. Tanker routes often pass through strategic chokepoints such as the Suez and Panama canals.",
    ),
]


def load_csv_rows(path: Path) -> list[dict[str, str]]:
    if not path.is_file():
        raise FileNotFoundError(
            f"Missing {path}. Download with:\n"
            "  curl -fsSL -o Module_8/data/dbpedia_en_100_summaries.csv "
            "https://raw.githubusercontent.com/dice-group/DBpedia-Summarizer/master/data_eval/en_100_summaries.csv"
        )
    rows: list[dict[str, str]] = []
    with path.open(encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            url = (row.get("url") or "").strip()
            abstract = (row.get("abstract") or row.get("short_abstract") or "").strip()
            if url and abstract:
                rows.append({"entity": url, "abstract": abstract})
    return rows


def write_corpus(path: Path, entries: list[tuple[str, str]], header: str) -> None:
    parts = [
        header,
        "",
        "License note: Abstracts derived from DBpedia / Wikipedia content (CC BY-SA).",
        "Source package: dice-group/DBpedia-Summarizer (en_100_summaries.csv) + curated maritime entries.",
        "",
    ]
    for i, (entity, text) in enumerate(entries, start=1):
        parts.append(f"[{i}] {entity}")
        parts.append(text.strip())
        parts.append("")
    path.write_text("\n".join(parts), encoding="utf-8")
    print(f"Wrote {path} ({len(entries)} entries, {path.stat().st_size:,} bytes)")


def main() -> None:
    rows = load_csv_rows(CSV_PATH)
    all_entries = [(r["entity"], r["abstract"]) for r in rows]

    maritime_from_csv = [
        (r["entity"], r["abstract"])
        for r in rows
        if MARITIME_PATTERN.search(r["abstract"]) or MARITIME_PATTERN.search(r["entity"])
    ]

    curated_keys = {e for e, _ in CURATED_MARITIME}
    maritime_merged: list[tuple[str, str]] = list(CURATED_MARITIME)
    for entity, abstract in maritime_from_csv:
        if entity not in curated_keys:
            maritime_merged.append((entity, abstract))

    write_corpus(
        OUT_FULL,
        all_entries,
        "DBpedia Course Corpus (100 articles) — Module 8 Knowledge Graph Lab",
    )
    write_corpus(
        OUT_MARITIME,
        maritime_merged,
        "DBpedia Maritime / Logistics Corpus — Module 8 Knowledge Graph Lab",
    )


if __name__ == "__main__":
    main()
